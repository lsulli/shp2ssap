from qgis.core import (
    QgsWkbTypes,
    QgsGeometry,
    QgsVectorLayer,
    QgsFeature,
    QgsProject,
    QgsVectorLayerEditBuffer
)
from qgis.utils import iface
from qgis.gui import QgsMessageBar
from qgis.core import Qgis


def _max_vertices_per_part(g):
    if not g or g.isEmpty():
        return 0

    if QgsWkbTypes.isMultiType(g.wkbType()):
        parts = g.asMultiPolyline()
    else:
        parts = [g.asPolyline()]

    return max(len(p) for p in parts if p)


def simplify_geometries(
    layer: QgsVectorLayer,
    output_name=None,
    max_points=99,
    tol_start=0.10,
    tol_step=0.10,
    tol_max=50.0,
    max_iter=500,
    only_selected=False,
    edit_original=False
):
    """
    Semplifica le geometrie di un layer di linee.
    
    Se edit_original = True: modifica direttamente il layer attivo
    Se edit_original = False: crea una COPIA del layer attivo
    
    Args:
        output_name: nome del layer di output (se None, usa "nome_layer_semplificato")
        max_points: numero massimo di vertici per parte
        tol_start: tolleranza iniziale di semplificazione
        tol_step: incremento della tolleranza
        tol_max: tolleranza massima
        max_iter: numero massimo di iterazioni
        only_selected: opera solo sulle feature selezionate
        edit_original: se True modifica il layer originale, se False crea una copia
    """

    if not layer:
        raise RuntimeError("Nessun layer attivo.")

    if QgsWkbTypes.geometryType(layer.wkbType()) != QgsWkbTypes.LineGeometry:
        raise RuntimeError("Il layer attivo non è un layer di linee.")

    # Se output_name non è specificato, genera automaticamente "nome_layer_semplificato"
    if output_name is None:
        layer_name = layer.name()
        # Rimuovi eventuali suffissi esistenti per evitare doppi suffissi
        if layer_name.endswith('_semplificato'):
            base_name = layer_name[:-13]  # Rimuove '_semplificato'
        else:
            base_name = layer_name
        output_name = f"{base_name}_semplificato"

    # Modalità editing diretto
    if edit_original:
        if only_selected and layer.selectedFeatureCount() == 0:
            raise RuntimeError("Nessuna feature selezionata.")
        
        return _simplify_in_place(
            layer=layer,
            max_points=max_points,
            tol_start=tol_start,
            tol_step=tol_step,
            tol_max=tol_max,
            max_iter=max_iter,
            only_selected=only_selected
        )
    
    # Modalità copia
    else:
        return _simplify_to_copy(
            layer=layer,
            output_name=output_name,
            max_points=max_points,
            tol_start=tol_start,
            tol_step=tol_step,
            tol_max=tol_max,
            max_iter=max_iter,
            only_selected=only_selected
        )


def _simplify_in_place(layer, max_points, tol_start, tol_step, tol_max, max_iter, only_selected):
    """
    Semplifica le geometrie direttamente sul layer originale
    Attiva automaticamente la modalità editing e la chiude al termine
    """
    feats = layer.selectedFeatures() if only_selected else layer.getFeatures()
    
    not_fixed = 0
    changed = 0
    skipped = 0
    
    # Attiva la modalità editing se non è già attiva
    was_editing = layer.isEditable()
    if not was_editing:
        print("Attivazione modalità editing...")
        layer.startEditing()
    
    try:
        for f in feats:
            geom = f.geometry()
            
            if not geom or geom.isEmpty():
                skipped += 1
                continue
            
            current_max = _max_vertices_per_part(geom)
            
            if current_max > max_points:
                tol = tol_start
                it = 0
                new_geom = None
                
                while it < max_iter and tol <= tol_max:
                    test_geom = geom.simplify(tol)
                    if not test_geom.isEmpty() and _max_vertices_per_part(test_geom) <= max_points:
                        new_geom = test_geom
                        break
                    tol += tol_step
                    it += 1
                
                if new_geom:
                    # Modifica la geometria della feature
                    layer.changeGeometry(f.id(), new_geom)
                    changed += 1
                    print(f"Feature {f.id()} semplificata con tolleranza {tol:.2f}")
                else:
                    not_fixed += 1
                    print(f"Feature {f.id()} NON semplificata (raggiunta tolleranza max {tol_max})")
            else:
                print(f"Feature {f.id()} ha già {current_max} vertici (<= {max_points})")
        
        # Salva le modifiche
        if changed > 0:
            success = layer.commitChanges()
            if success:
                print("\n Modifiche salvate con successo!")
            else:
                print("\n Errore durante il salvataggio delle modifiche:")
                print(layer.commitErrors())
                layer.rollBack()
        else:
            # Se non ci sono modifiche, esci senza salvare
            layer.rollBack()
            print("\nNessuna modifica da salvare.")
    
    except Exception as e:
        # In caso di errore, annulla tutte le modifiche
        print(f"\n❌ Errore durante l'elaborazione: {e}")
        layer.rollBack()
        raise
    
    print("\n--- RISULTATI EDITING DIRETTO ---")
    print(f"Feature modificate: {changed}")
    print(f"Feature non semplificabili: {not_fixed}")
    print(f"Feature saltate (geometria nulla): {skipped}")
    print(f"Feature totali processate: {changed + not_fixed + skipped}")
    
    if changed > 0:
        # Mostra messaggio nella barra di QGIS
        iface.messageBar().pushMessage(
            "Successo", 
            f"Semplificate {changed} geometrie. {not_fixed} non semplificabili.",
            level=Qgis.Success, 
            duration=3
        )
    
    return layer


def _simplify_to_copy(layer, output_name, max_points, tol_start, tol_step, tol_max, max_iter, only_selected):
    """
    Crea una copia del layer con le geometrie semplificate
    """
    crs = layer.crs()
    geom_type = QgsWkbTypes.displayString(layer.wkbType())

    out_layer = QgsVectorLayer(
        f"{geom_type}?crs={crs.authid()}",
        output_name,
        "memory"
    )

    pr = out_layer.dataProvider()
    pr.addAttributes(layer.fields())
    out_layer.updateFields()

    feats = layer.selectedFeatures() if only_selected else layer.getFeatures()

    new_features = []
    not_fixed = 0
    changed = 0
    skipped = 0

    for f in feats:
        geom = f.geometry()

        if not geom or geom.isEmpty():
            skipped += 1
            new_f = QgsFeature(out_layer.fields())
            new_f.setAttributes(f.attributes())
            new_f.setGeometry(geom)
            new_features.append(new_f)
            continue

        new_geom = QgsGeometry(geom)
        current_max = _max_vertices_per_part(new_geom)

        if current_max > max_points:
            tol = tol_start
            it = 0

            while it < max_iter and tol <= tol_max:
                test_geom = geom.simplify(tol)
                if not test_geom.isEmpty() and _max_vertices_per_part(test_geom) <= max_points:
                    new_geom = test_geom
                    changed += 1
                    break
                tol += tol_step
                it += 1

            if _max_vertices_per_part(new_geom) > max_points:
                not_fixed += 1

        new_f = QgsFeature(out_layer.fields())
        new_f.setAttributes(f.attributes())
        new_f.setGeometry(new_geom)
        new_features.append(new_f)

    pr.addFeatures(new_features)
    out_layer.updateExtents()

    QgsProject.instance().addMapLayer(out_layer)

    print("\n--- RISULTATI CREAZIONE COPIA ---")
    print(f"Layer copia '{output_name}' creato.")
    print(f"Feature modificate: {changed}")
    print(f"Feature non semplificabili: {not_fixed}")
    print(f"Feature saltate (geometria nulla): {skipped}")
    print(f"Numero feature nel layer copia: {out_layer.featureCount()}")

    return out_layer


# ESEMPI DI UTILIZZO:

# 1. Per creare una copia con nome automatico "nome_layer_semplificato":
# simplify_geometries(max_points=99)

# 2. Per creare una copia con nome personalizzato:
# simplify_geometries(output_name="Mio_Layer_Semplificato", max_points=99)

# 3. Per modificare direttamente il layer attivo (attiva/salva automaticamente):
# simplify_geometries(edit_original=True, max_points=99)

# 4. Per modificare solo le feature selezionate del layer attivo:
# simplify_geometries(edit_original=True, only_selected=True, max_points=99)

# 5. Con parametri personalizzati:
# simplify_geometries(
#     edit_original=True,
#     max_points=50,
#     tol_start=0.5,
#     tol_step=0.2,
#     tol_max=100.0,
#     only_selected=True
# )