from __future__ import annotations

from typing import Optional

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsWkbTypes,
    QgsExpression,
    QgsFeatureRequest,
    QgsMessageLog,
    Qgis,
)

def _log(msg, level=Qgis.Info):
    QgsMessageLog.logMessage(str(msg), "Shp2SSAP_Trim", level)
    try:
        print(msg)
    except Exception:
        pass

def _make_equals_expr(layer: QgsVectorLayer, field_name: str, value):
    idx = layer.fields().indexOf(field_name)
    if idx < 0:
        raise ValueError(f"Campo '{field_name}' non presente.")
    fld = layer.fields()[idx]
    if fld.typeName().lower() in ("string", "text", "varchar", "char"):
        v = str(value).replace("'", "''")
        return f'"{field_name}" = \'{v}\''
    return f'"{field_name}" = {value}'

def _same_id(a, b) -> bool:
    try:
        return int(a) == int(b)
    except Exception:
        return str(a) == str(b)

def _to_lines_xy(geom: QgsGeometry):
    if geom is None or geom.isEmpty():
        return []
    if QgsWkbTypes.isMultiType(geom.wkbType()):
        return [list(line) for line in geom.asMultiPolyline()]
    return [list(geom.asPolyline())]

def _clip_polyline_points(pts, xmin, xmax):
    # Semplificazione: mantieni i punti con xmin<=x<=xmax.
    # Se un segmento attraversa il limite, inserisci il punto di intersezione lineare.
    if not pts or len(pts) < 2:
        return []

    def interp(p1, p2, x):
        # interpolazione lineare su x
        if p2.x() == p1.x():
            return None
        t = (x - p1.x()) / (p2.x() - p1.x())
        if t < 0 or t > 1:
            return None
        y = p1.y() + t * (p2.y() - p1.y())
        try:
            from qgis.core import QgsPointXY
            return QgsPointXY(x, y)
        except Exception:
            return None

    out = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        ax_in = xmin <= a.x() <= xmax
        bx_in = xmin <= b.x() <= xmax

        if ax_in and not out:
            out.append(a)
        elif ax_in and out and (out[-1].x() != a.x() or out[-1].y() != a.y()):
            out.append(a)

        # attraversamento a xmin
        if (a.x() < xmin and b.x() > xmin) or (a.x() > xmin and b.x() < xmin):
            ip = interp(a, b, xmin)
            if ip is not None:
                if not out or (out[-1].x() != ip.x() or out[-1].y() != ip.y()):
                    out.append(ip)

        # attraversamento a xmax
        if (a.x() < xmax and b.x() > xmax) or (a.x() > xmax and b.x() < xmax):
            ip = interp(a, b, xmax)
            if ip is not None:
                if not out or (out[-1].x() != ip.x() or out[-1].y() != ip.y()):
                    out.append(ip)

        if bx_in:
            if not out or (out[-1].x() != b.x() or out[-1].y() != b.y()):
                out.append(b)

    # Rimuovi duplicati consecutivi
    cleaned = []
    for p in out:
        if not cleaned:
            cleaned.append(p)
        else:
            lp = cleaned[-1]
            if lp.x() != p.x() or lp.y() != p.y():
                cleaned.append(p)

    if len(cleaned) < 2:
        return []
    return cleaned

def _clip_geom_by_x(geom: QgsGeometry, xmin: float, xmax: float) -> Optional[QgsGeometry]:
    # Supporto LineString / MultiLineString
    lines = _to_lines_xy(geom)
    if not lines:
        return QgsGeometry()  # empty

    clipped = []
    for pts in lines:
        c = _clip_polyline_points(pts, xmin, xmax)
        if c and len(c) >= 2:
            clipped.append(c)

    if not clipped:
        return QgsGeometry()  # empty

    if len(clipped) == 1:
        return QgsGeometry.fromPolylineXY(clipped[0])
    return QgsGeometry.fromMultiPolylineXY(clipped)

def clip_lines_by_x_range(
    layer: QgsVectorLayer,
    id_field: str = "SSAP_ID",
    topo_id_value=1,
    edit_in_place: bool = False,
    output_name: str = "Linee_clippate_X",
    delete_if_empty: bool = False,
) -> QgsVectorLayer:
    """Clippa le geometrie lineari mantenendo solo la parte tra xmin/xmax della feature topo (id_field==topo_id_value).

    - Se edit_in_place=False: crea un layer memory copiando attributi+geometrie, lo aggiunge al progetto e modifica quello.
    - Se edit_in_place=True: modifica il layer originale.

    Ritorna il layer risultante (originale o memory).
    """
    if layer is None or not isinstance(layer, QgsVectorLayer) or not layer.isValid():
        raise ValueError("Layer non valido.")

    _log(f"Layer: {layer.name()} | provider={layer.providerType()} | wkb={QgsWkbTypes.displayString(layer.wkbType())}")

    if layer.geometryType() != QgsWkbTypes.LineGeometry:
        raise ValueError("Il layer NON è lineare (LineString/MultiLineString).")
    if id_field not in [f.name() for f in layer.fields()]:
        raise ValueError(f"Campo '{id_field}' non presente nel layer.")

    # Feature topo
    expr = _make_equals_expr(layer, id_field, topo_id_value)
    topo_feat = next(layer.getFeatures(QgsFeatureRequest(QgsExpression(expr)).setLimit(1)), None)
    if topo_feat is None or topo_feat.geometry() is None or topo_feat.geometry().isEmpty():
        raise RuntimeError(f"Non trovo la feature topo con: {expr}")

    bbox = topo_feat.geometry().boundingBox()
    xmin, xmax = bbox.xMinimum(), bbox.xMaximum()
    if xmin > xmax:
        xmin, xmax = xmax, xmin
    _log(f"Topo bbox: xmin={xmin} xmax={xmax}")

    # Target
    if edit_in_place:
        target = layer
        if not target.isEditable():
            target.startEditing()
        _log("Modalità: IN-PLACE (modifico originale)")
    else:
        # prova MultiLineString, fallback LineString
        target = QgsVectorLayer(f"MultiLineString?crs={layer.crs().authid()}", output_name, "memory")
        if not target.isValid():
            target = QgsVectorLayer(f"LineString?crs={layer.crs().authid()}", output_name, "memory")
        target.dataProvider().addAttributes(layer.fields())
        target.updateFields()

        feats = []
        for f in layer.getFeatures():
            nf = QgsFeature(target.fields())
            nf.setAttributes(f.attributes())
            nf.setGeometry(f.geometry())
            feats.append(nf)
        target.dataProvider().addFeatures(feats)
        QgsProject.instance().addMapLayer(target)
        target.startEditing()
        _log("Modalità: COPIA (layer memory)")

    updated = unchanged = deleted = skipped = 0
    ids_to_delete = []

    for f in target.getFeatures():
        if _same_id(f[id_field], topo_id_value):
            unchanged += 1
            continue

        g = f.geometry()
        if g is None or g.isEmpty():
            unchanged += 1
            continue

        fb = g.boundingBox()
        if fb.xMinimum() >= xmin and fb.xMaximum() <= xmax:
            unchanged += 1
            continue

        gnew = _clip_geom_by_x(g, xmin, xmax)
        if gnew is None:
            skipped += 1
            continue

        if gnew.isEmpty():
            if delete_if_empty:
                ids_to_delete.append(f.id())
            else:
                unchanged += 1
            continue

        if target.changeGeometry(f.id(), gnew):
            updated += 1

    if ids_to_delete and target.deleteFeatures(ids_to_delete):
        deleted = len(ids_to_delete)

    target.commitChanges()
    _log(f"RISULTATO: aggiornate={updated} | non toccate={unchanged} | skipped={skipped} | eliminate={deleted} | delete_if_empty={delete_if_empty}")
    return target
