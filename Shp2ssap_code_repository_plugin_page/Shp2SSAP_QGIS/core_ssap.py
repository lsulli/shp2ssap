from __future__ import annotations

import datetime as _dt
import math
import os
import re
import shutil
import tempfile
import time
import uuid
import re
import csv as _csv
import io as _io
from dataclasses import dataclass
from math import atan, degrees
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from qgis.PyQt.QtCore import QSettings
from qgis.core import QgsApplication, QgsMessageLog, Qgis

# --- pyshp: prima prova vendorizzato, poi fallback
try:
    from .extlibs import shapefile  # type: ignore
except Exception:
    import shapefile  # type: ignore

from .logger_utils import auto_log_module_functions

# =========================
# Etichette / fallback
# =========================
class _LblFallback:
    versione = "2.0.8 - build 276"
    msg_title = "Shp2SSAP"
    msg_title_error = "Errore"
    msg_title_check = "Verifica shapefile"

    msg_error01 = "ERRORE 01: impossibile leggere shapefile.\n"
    msg_error02 = "ERRORE 02: mancano campi obbligatori.\nCampi mancanti: "
    msg_error03 = "ERRORE 03: valori non ammessi nel campo SSAP: "
    msg_error04 = "ERRORE 04: shapefile non è di tipo Polyline.\n"
    msg_error11 = "\nERRORE 11: ordine verticale strati (top→bottom) non coerente.\n"

    msg_err_end1 = "\nCorreggi gli errori e riprova."
    msg_err_end2 = "\nSeleziona un percorso di output valido."
    header_msg_error = "Errore non previsto.\n"

LBL = _LblFallback()

# =========================
# Logging -> qgisSettingsDirPath()/Shp2SSAP
# =========================
_SETTINGS_DIR = Path(QgsApplication.qgisSettingsDirPath())
_PLUGIN_DIR = _SETTINGS_DIR / "Shp2SSAP"
_PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
_SPLIT_RE = re.compile(r"[\s;|:=]+")
_DECIMAL_COMMA_RE = re.compile(r"(\d),(\d)")



def default_txt_path() -> Path:
    """Percorso del file default.txt (compatibilità con gli script originali)."""
    return _PLUGIN_DIR / "default.txt"


def write_default_txt(values: dict) -> Path:
    """Scrive default.txt con TUTTI i valori del tab Opzioni (formato key=value)."""
    p = default_txt_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted(values.keys())
    lines = [
        "# Shp2SSAP QGIS - default.txt (autogenerato)",
        f"# generated={_dt.datetime.now().isoformat(timespec='seconds')}",
    ]
    for k in keys:
        v = values.get(k, "")
        lines.append(f"{k}={v}")
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def qgis_log_info(msg: str) -> None:
    """Log su pannello QGIS."""
    try:
        QgsMessageLog.logMessage(msg, "Shp2SSAP", Qgis.Info)
    except Exception:
        pass



def qgis_log_error(msg: str) -> None:
    """Log su pannello QGIS."""
    try:
        QgsMessageLog.logMessage(msg, "Shp2SSAP", Qgis.Critical)
    except Exception:
        pass



def safe_close_reader(sf) -> None:
    try:
        close = getattr(sf, "close", None)
        if callable(close):
            close()
    except Exception:
        pass


# =========================
# Settings (sostituisce default.txt)
# =========================
SETTINGS_GROUP = "Shp2SSAP"

DEFAULTS_FALLBACK = {
    "def_shp_dir": "",
    "def_ssap_dir": "",
    "def_ssap_path_exe": r"C:\SSAP2010\ssap2010_64bit.exe",
    "max_char_msg_err": 750,

    # Default valori Tab XY -> "Assegna valori a strato"
    "xy_phi_default": 0.0,
    "xy_c_default": 0.0,
    "xy_cu_default": 0.0,
    "xy_gamma_default": 0.0,
    "xy_gammasat_default": 0.0,
    "xy_falda_depth_default": 0.0,
    "xy_bedrock_depth_default": 5.0,

    # Bedrock parametri (usati quando bedrock è abilitato)
    "xy_phi_br_default": 50.0,
    "xy_c_br_default": 500.0,
    
    # Numero massimo nodi 
    "num_max_nodi_default": 99,
}



def get_settings() -> dict:
    s = QSettings()
    s.beginGroup(SETTINGS_GROUP)
    out = dict(DEFAULTS_FALLBACK)

    # percorsi + controlli generali
    out["def_shp_dir"] = s.value("def_shp_dir", out["def_shp_dir"], type=str)
    out["def_ssap_dir"] = s.value("def_ssap_dir", out["def_ssap_dir"], type=str)
    out["def_ssap_path_exe"] = s.value("def_ssap_path_exe", out["def_ssap_path_exe"], type=str)
    out["max_char_msg_err"] = s.value("max_char_msg_err", out["max_char_msg_err"], type=int)
    out["num_max_nodi_default"] = s.value("num_max_nodi_default", out["num_max_nodi_default"], type=int)

    # default tab XY
    out["xy_phi_default"] = s.value("xy_phi_default", out["xy_phi_default"], type=float)
    out["xy_c_default"] = s.value("xy_c_default", out["xy_c_default"], type=float)
    out["xy_cu_default"] = s.value("xy_cu_default", out["xy_cu_default"], type=float)
    out["xy_gamma_default"] = s.value("xy_gamma_default", out["xy_gamma_default"], type=float)
    out["xy_gammasat_default"] = s.value("xy_gammasat_default", out["xy_gammasat_default"], type=float)
    out["xy_falda_depth_default"] = s.value("xy_falda_depth_default", out["xy_falda_depth_default"], type=float)
    out["xy_bedrock_depth_default"] = s.value("xy_bedrock_depth_default", out["xy_bedrock_depth_default"], type=float)
    out["xy_phi_br_default"] = s.value("xy_phi_br_default", out["xy_phi_br_default"], type=float)
    out["xy_c_br_default"] = s.value("xy_c_br_default", out["xy_c_br_default"], type=float)

    # clamp/minimi
    if out["xy_bedrock_depth_default"] < 0:
        out["xy_bedrock_depth_default"] = DEFAULTS_FALLBACK["xy_bedrock_depth_default"]
    if out["xy_falda_depth_default"] < 0:
        out["xy_falda_depth_default"] = DEFAULTS_FALLBACK["xy_falda_depth_default"]

    s.endGroup()

    # aggiorna anche default.txt per compatibilità
    try:
        write_default_txt(out)
    except Exception:
        pass
    return out



def save_settings(values: dict) -> None:
    s = QSettings()
    s.beginGroup(SETTINGS_GROUP)

    # percorsi + controlli generali
    s.setValue("def_shp_dir", str(values.get("def_shp_dir", "")))
    s.setValue("def_ssap_dir", str(values.get("def_ssap_dir", "")))
    s.setValue("def_ssap_path_exe", str(values.get("def_ssap_path_exe", "")))
    s.setValue("num_max_nodi_default", str(values.get("num_max_nodi_default", 99)))

    # default tab XY
    s.setValue("xy_phi_default", float(values.get("xy_phi_default", 0.0)))
    s.setValue("xy_c_default", float(values.get("xy_c_default", 0.0)))
    s.setValue("xy_cu_default", float(values.get("xy_cu_default", 0.0)))
    s.setValue("xy_gamma_default", float(values.get("xy_gamma_default", 0.0)))
    s.setValue("xy_gammasat_default", float(values.get("xy_gammasat_default", 0.0)))
    s.setValue("xy_falda_depth_default", max(0.0, float(values.get("xy_falda_depth_default", 0.0))))
    s.setValue("xy_bedrock_depth_default", max(0.0, float(values.get("xy_bedrock_depth_default", 5.0))))
    s.setValue("xy_phi_br_default", float(values.get("xy_phi_br_default", 50.0)))
    s.setValue("xy_c_br_default", float(values.get("xy_c_br_default", 500.0)))

    s.endGroup()

    # aggiorna anche default.txt per compatibilità
    try:
        write_default_txt(get_settings())
    except Exception:
        pass


# =========================
# Utilities
# =========================
class SSAPError(Exception):
    pass


def _norm(s) -> str:
    return str(s).strip().lower()


def format_float_str(v: float) -> str:
    return f"{float(v):.2f}"


# =========================
# Parte A: Shp2SSAP
# =========================
@dataclass(frozen=True)
class FieldIndex:
    ssap_id: int
    ssap: int
    phi: int
    cu: int
    c: int
    gamma: int
    gammasat: int
    exclude: int
    dr_undr: int
    val1: Optional[int] = None
    sigci: Optional[int] = None
    gsi: Optional[int] = None
    mi: Optional[int] = None
    d: Optional[int] = None


@dataclass(frozen=True)
class Feature:
    idx: int
    ssap: str
    ssap_id: int
    exclude: bool
    record: Sequence
    points: Sequence[Tuple[float, float]]


@dataclass(frozen=True)
class TopoLimits:
    x_min: float
    x_max: float
    tol: float


def get_field_index(sf: shapefile.Reader) -> Tuple[FieldIndex, dict]:
    fields = sf.fields
    name_to_idx: dict[str, int] = {}
    for i, f in enumerate(fields):
        name = str(f[0]).upper()
        if name == "DELETIONFLAG":
            continue
        name_to_idx[name] = i - 1  # -1 per compensare DeletionFlag

    required = ["SSAP_ID", "SSAP", "PHI", "CU", "C", "GAMMA", "GAMMASAT", "EXCLUDE", "DR_UNDR"]
    missing = [x for x in required if x not in name_to_idx]
    if missing:
        raise SSAPError(LBL.msg_error02 + str(missing))

    flags = {
        "has_svr": "VAL1" in name_to_idx,
        "has_rock": all(k in name_to_idx for k in ["SIGCI", "GSI", "MI", "D"]),
    }

    fi = FieldIndex(
        ssap_id=name_to_idx["SSAP_ID"],
        ssap=name_to_idx["SSAP"],
        phi=name_to_idx["PHI"],
        cu=name_to_idx["CU"],
        c=name_to_idx["C"],
        gamma=name_to_idx["GAMMA"],
        gammasat=name_to_idx["GAMMASAT"],
        exclude=name_to_idx["EXCLUDE"],
        dr_undr=name_to_idx["DR_UNDR"],
        val1=name_to_idx.get("VAL1"),
        sigci=name_to_idx.get("SIGCI"),
        gsi=name_to_idx.get("GSI"),
        mi=name_to_idx.get("MI"),
        d=name_to_idx.get("D"),
    )
    return fi, flags


def iter_features(sf: shapefile.Reader, fi: FieldIndex) -> list[Feature]:
    feats: list[Feature] = []
    try:
        n = int(sf.numRecords)
    except Exception:
        n = len(sf.shapeRecords())

    for i in range(n):
        sr = sf.shapeRecord(i)
        rec = sr.record
        # pyshp può restituire tuple (x,y,z,...) se la geometria è 3D/M.
        # SSAP usa solo 2D: riduciamo sempre a (x,y).
        pts_raw = sr.shape.points
        pts = [(p[0], p[1]) for p in pts_raw]
        feats.append(
            Feature(
                idx=i,
                ssap=_norm(rec[fi.ssap]),
                ssap_id=rec[fi.ssap_id],
                exclude=(rec[fi.exclude] == 1),
                record=rec,
                points=pts,
            )
        )
    return feats


def check_shape_type(sf: shapefile.Reader) -> None:
    shapes = sf.shapes()
    if not shapes:
        raise SSAPError("Shapefile vuoto.")
    if shapes[0].shapeType not in (3, 13, 23):
        raise SSAPError(LBL.msg_error04)


def check_field_ssap_values(features: Sequence[Feature]) -> None:
    allowed = {"dat", "fld", "svr", "sin"}
    bad = sorted({f.ssap for f in features if f.ssap not in allowed})
    if bad:
        raise SSAPError(LBL.msg_error03 + str(bad))


def check_layers_number(features: Sequence[Feature], ssap_type: str, max_num: int) -> None:
    n = sum(1 for f in features if (not f.exclude) and f.ssap == ssap_type)
    if n > max_num:
        raise SSAPError(f"\nERRORE 05: numero strati '{ssap_type}' = {n}, superiore a {max_num} (limite SSAP).\n")


def check_points_number(features: Sequence[Feature]) -> None:
    bad = [f for f in features if (not f.exclude) and len(f.points) > 100 and f.ssap in {"dat", "fld", "sin"}]
    if bad:
        msg = "\nERRORE 06: presenti strati con numero punti > 100 (limite SSAP):\n"
        for f in bad:
            msg += f"- Strato '{f.ssap}' ID={f.ssap_id} punti={len(f.points)}\n"
        raise SSAPError(msg)


def check_id_zero(features: Sequence[Feature]) -> None:
    msg = ""
    for f in features:
        if f.exclude:
            continue
        if f.ssap != "fld" and f.ssap_id == 0:
            msg += f"\nERRORE 07: strato SSAP='{f.ssap}' con SSAP_ID=0 (ammesso solo per fld).\n"
        if f.ssap == "fld" and f.ssap_id != 0:
            msg += f"\nERRORE 07: strato fld deve avere SSAP_ID=0 (trovato {f.ssap_id}).\n"
    if msg:
        raise SSAPError(msg)


def check_all_negative_val(features: Sequence[Feature]) -> None:
    msg = ""
    for f in features:
        if f.exclude:
            continue
        for (x, y) in f.points:
            if x < 0 or y < 0:
                msg += f"- Strato '{f.ssap}' ID={f.ssap_id}: x={format_float_str(x)} y={format_float_str(y)}\n"
                break
    if msg:
        raise SSAPError("\nERRORE 08: presenti coordinate negative:\n" + msg)


def check_jutting_surface(features: Sequence[Feature]) -> None:
    topo = next((f for f in features if (not f.exclude) and f.ssap == "dat" and f.ssap_id == 1), None)
    if not topo or len(topo.points) < 2:
        return
    xs = [p[0] for p in topo.points]
    for i in range(len(xs) - 1):
        if xs[i] > xs[i + 1]:
            raise SSAPError("\nERRORE 09: la superficie topografica presenta una forma aggettante.\n")


def check_continuous_order(features: Sequence[Feature], ssap_type: str) -> None:
    ids = sorted([f.ssap_id for f in features if (not f.exclude) and f.ssap == ssap_type])
    if not ids:
        return
    start = 0 if ids[0] == 0 else 1
    expected = list(range(start, start + len(ids)))
    if ids != expected:
        raise SSAPError(
            f"\nERRORE 10: sequenza SSAP_ID non continua per '{ssap_type}'.\n"
            f"ID trovati (ordinati): {ids}\nID attesi: {expected}\n"
        )


def check_top_bottom_order(features: Sequence[Feature]) -> None:
    dats = sorted([f for f in features if (not f.exclude) and f.ssap == "dat"], key=lambda x: x.ssap_id)
    if len(dats) < 2:
        return

    mins = []
    maxs = []
    cents = []
    for f in dats:
        ys = [round(p[1], 2) for p in f.points]
        mins.append(min(ys))
        maxs.append(max(ys))
        cents.append(round(sum(ys) / len(ys), 2))

    def is_desc(v: list[float]) -> bool:
        return v == sorted(v, reverse=True)

    if not (is_desc(mins) or is_desc(maxs) or is_desc(cents)):
        raise SSAPError(LBL.msg_error11)


def run_precheck(sf: shapefile.Reader, features: Sequence[Feature], check_topbottom: bool) -> dict:
    check_shape_type(sf)
    check_field_ssap_values(features)
    check_layers_number(features, "dat", 20)
    check_layers_number(features, "svr", 10)
    check_layers_number(features, "fld", 1)
    check_layers_number(features, "sin", 1)
    check_points_number(features)
    check_id_zero(features)
    check_all_negative_val(features)
    check_jutting_surface(features)
    check_continuous_order(features, "dat")
    check_continuous_order(features, "svr")
    if check_topbottom:
        check_top_bottom_order(features)

    return {
        "dat": sum(1 for f in features if (not f.exclude) and f.ssap == "dat"),
        "fld": sum(1 for f in features if (not f.exclude) and f.ssap == "fld"),
        "svr": sum(1 for f in features if (not f.exclude) and f.ssap == "svr"),
        "sin": sum(1 for f in features if (not f.exclude) and f.ssap == "sin"),
    }


def topo_limits(features: Sequence[Feature], trim_factor: int) -> TopoLimits:
    topo = next((f for f in features if (not f.exclude) and f.ssap == "dat" and f.ssap_id == 1), None)
    if not topo:
        return TopoLimits(0.0, 0.0, 0.0)
    x_min = round(topo.points[0][0], 2)
    x_max = round(topo.points[-1][0], 2)
    length = round(x_max - x_min, 2)
    tol = round(length / max(20, trim_factor), 2)
    return TopoLimits(x_min, x_max, tol)


def xy_ref(points: Sequence[Tuple[float, float]], topo: TopoLimits) -> Tuple[float, float, float, float, float, float, float, float]:
    if len(points) < 2:
        return (0, 0, 0, 0, 0, 0, 0, 0)

    left_idx = 1
    for i, (x, _y) in enumerate(points):
        if x > (topo.x_min + topo.tol):
            left_idx = max(1, i)
            break

    right_idx = len(points) - 1
    for i, (x, _y) in enumerate(points):
        if x > (topo.x_max - topo.tol):
            right_idx = max(1, i)
            break

    x1sx, y1sx = points[left_idx - 1]
    x2sx, y2sx = points[left_idx]
    x1dx, y1dx = points[right_idx - 1]
    x2dx, y2dx = points[right_idx]
    return (
        round(x1sx, 2), round(y1sx, 2), round(x2sx, 2), round(y2sx, 2),
        round(x1dx, 2), round(y1dx, 2), round(x2dx, 2), round(y2dx, 2)
    )


def y_on_line(x1: float, y1: float, x2: float, y2: float, x: float) -> float:
    if x2 == x1:
        return y1
    return (((x - x1) / (x2 - x1)) * (y2 - y1)) + y1


def safe_rmtree(path: Path, retries: int = 8, delay: float = 0.2) -> None:
    for _ in range(retries):
        try:
            if path.exists():
                shutil.rmtree(path, ignore_errors=False)
            return
        except (PermissionError, OSError):
            time.sleep(delay)
    qgis_log_error(f"Impossibile cancellare temp dir (lock Windows): {path}")


def write_ssap_files(
    shp_path: Path,
    out_base: Path,
    check_topbottom: bool,
) -> list[Path]:
    created: list[Path] = []

    settings = get_settings()
    trim_factor = int(settings.get("trim_tolerance_factor", 20))

    tmp_root = Path(tempfile.gettempdir())
    td_path = tmp_root / f"shp2ssap_{uuid.uuid4().hex}"
    td_path.mkdir(parents=True, exist_ok=True)

    sf = None
    try:
        base = shp_path.with_suffix("")

        # Copia trio shapefile
        for ext in (".shp", ".dbf", ".shx"):
            src = base.with_suffix(ext)
            if not src.exists():
                raise SSAPError(f"Manca il file {src.name} (necessari .shp .dbf .shx).")
            shutil.copy2(src, td_path / src.name)

        tmp_shp = td_path / shp_path.name

        qgis_log_info(f"Shp2SSAP: avvio conversione {shp_path}")

        sf = shapefile.Reader(str(tmp_shp))
        fi, flags = get_field_index(sf)
        features = iter_features(sf, fi)

        counts = run_precheck(sf, features, check_topbottom=check_topbottom)

        dat_layers = sorted([f for f in features if (not f.exclude) and f.ssap == "dat"], key=lambda x: x.ssap_id)
        fld_layer = next((f for f in features if (not f.exclude) and f.ssap == "fld"), None)
        svr_layers = sorted([f for f in features if (not f.exclude) and f.ssap == "svr"], key=lambda x: x.ssap_id)
        sin_layers = [f for f in features if (not f.exclude) and f.ssap == "sin"]

        topo = topo_limits(features, trim_factor)

        t = _dt.datetime.now()
        header_date = f"File creato in data: {t.strftime('%A, %d %B %Y %H:%M')}"

        p_dat = out_base.with_suffix(".dat")
        p_geo = out_base.with_suffix(".geo")
        p_mod = out_base.with_suffix(".mod")
        p_fld = out_base.with_suffix(".fld")
        p_svr = out_base.with_suffix(".svr")
        p_sin = out_base.with_suffix(".sin")

        try:
            with open(p_dat, "w", encoding="utf-8", newline="\n") as f_dat, \
                 open(p_geo, "w", encoding="utf-8", newline="\n") as f_geo, \
                 open(p_mod, "w", encoding="utf-8", newline="\n") as f_mod:

                created.extend([p_dat, p_geo, p_mod])

                f_dat.write("|" + header_date + "\n")
                f_dat.write("|" + f"File .dat per SSAP2010 generato da Shp2SSAP, versione {LBL.versione}\n")
                f_dat.write("|" + f"Shapefile di input: '{shp_path}'\n")

                # DAT + GEO
                for lay in dat_layers:
                    pts = list(lay.points)
                    if not pts:
                        continue

                    refs = xy_ref(pts, topo) if (topo.tol > 0) else (0, 0, 0, 0, 0, 0, 0, 0)

                    rec = lay.record
                    dr = _norm(rec[fi.dr_undr])

                    is_rock = bool(flags.get("has_rock")) and fi.sigci is not None and float(rec[fi.sigci] or 0) > 0

                    if not is_rock:
                        if dr != "u":
                            f_geo.write("\t" + str(rec[fi.phi]))
                            f_geo.write("\t" + str(rec[fi.c]))
                            f_geo.write("\t0")
                        else:
                            cu = float(rec[fi.cu] or 0)
                            if cu == 0:
                                raise SSAPError(
                                    f"- Il valore di CU dello strato {lay.ssap_id} è zero: verifica non drenata non applicabile.\n"
                                )
                            f_geo.write("\t0\t0\t" + str(rec[fi.cu]))

                        f_geo.write("\t" + str(rec[fi.gamma]))
                        f_geo.write("\t" + str(rec[fi.gammasat]) + "\n")
                    else:
                        f_geo.write("\t0\t0\t0")
                        f_geo.write("\t" + str(rec[fi.gamma]))
                        f_geo.write("\t" + str(rec[fi.gammasat]))
                        f_geo.write("\t" + str(rec[fi.sigci]))
                        f_geo.write("\t" + str(rec[fi.gsi]))
                        f_geo.write("\t" + str(rec[fi.mi]))
                        f_geo.write("\t" + str(rec[fi.d]) + "\n")

                    f_dat.write(f"##{lay.ssap_id}-------------------------- Numero punti: ~{int(len(pts))}\n")

                    x_first = pts[0][0]
                    x_last = max(p[0] for p in pts)

                    for (x, y) in pts:
                        x2, y2 = x, y
                        f_dat.write("\t" + format_float_str(x2) + "\t\t" + format_float_str(y2) + "\n")

                # FLD
                has_fld = False
                if fld_layer is not None:
                    has_fld = True
                    with open(p_fld, "w", encoding="utf-8", newline="\n") as f_fld:
                        created.append(p_fld)
                        pts = list(fld_layer.points)
                        refs = xy_ref(pts, topo) if (topo.tol > 0) else (0, 0, 0, 0, 0, 0, 0, 0)

                        x_first = pts[0][0] if pts else 0
                        x_last = max((p[0] for p in pts), default=0)

                        for (x, y) in pts:
                            x2, y2 = x, y
                            f_fld.write("\t" + format_float_str(x2) + "\t\t" + format_float_str(y2) + "\n")

                # SVR
                has_svr = False
                if svr_layers and flags.get("has_svr") and fi.val1 is not None:
                    has_svr = True
                    with open(p_svr, "w", encoding="utf-8", newline="\n") as f_svr:
                        created.append(p_svr)
                        for lay in svr_layers:
                            pts = list(lay.points)
                            if len(pts) < 2:
                                continue
                            x_min = pts[0][0]
                            x_max = pts[-1][0]
                            val1 = lay.record[fi.val1]
                            f_svr.write(
                                format_float_str(x_min) + "\t" +
                                format_float_str(x_max) + "\t" +
                                format_float_str(float(val1)) + "\n"
                            )

                # SIN
                if sin_layers:
                    with open(p_sin, "w", encoding="utf-8", newline="\n") as f_sin:
                        created.append(p_sin)
                        f_sin.write("# Shp2SSAP - versione: " + str(LBL.versione) + "\n")
                        f_sin.write("# file " + str(p_sin.name) + " creato da Shapefile di input: '" + str(shp_path) + "'\n")
                        for lay in sin_layers:
                            pts = list(lay.points)
                            for (x, y) in pts:
                                f_sin.write("\t" + format_float_str(x) + "\t\t" + format_float_str(y) + "\n")

                # MOD
                dat_count = counts["dat"]
                f_mod.write(f"{dat_count}    {1 if has_fld else 0}    {1 if has_svr else 0}    0    0    0\n")
                f_mod.write(p_dat.name + "\n")
                if has_fld:
                    f_mod.write(p_fld.name + "\n")
                f_mod.write(p_geo.name + "\n")
                if has_svr:
                    f_mod.write(p_svr.name + "\n")

            qgis_log_info(f"Shp2SSAP: conversione completata -> {out_base}")
            return created

        except Exception:
            for p in created:
                try:
                    if p.exists():
                        p.unlink()
                except Exception:
                    pass
            raise

    finally:
        if sf is not None:
            safe_close_reader(sf)
        safe_rmtree(td_path)


# =========================
# Parte B: XY -> Shapefile SSAP
# =========================
_SPLIT_RE = re.compile(r"[;\t:|]+|(?:(?<=\d)\s+(?=-?\d))")


@dataclass(frozen=True)
class LayerValues:
    phi: float = 0.0
    c: float = 0.0
    cu: float = 0.0
    gamma: float = 0.0
    gammasat: float = 0.0


@dataclass(frozen=True)
class ConvertOptions:
    layer_values: LayerValues
    use_pendenza_media: bool
    falda_enabled: bool
    falda_depth: float
    bedrock_enabled: bool
    bedrock_depth: float
    phi_br: float
    c_br: float


# def parse_xy_points(text: str) -> List[List[float]]:
    # points: List[List[float]] = []
    # for raw in text.splitlines():
        # line = raw.strip()
        # if not line:
            # continue
        # line = line.replace(",", ".")
        # parts = [p for p in _SPLIT_RE.split(line) if p and p.strip()]
        # if len(parts) != 2:
            # continue
        # try:
            # x = float(parts[0])
            # y = float(parts[1])
        # except ValueError:
            # continue
        # points.append([x, y])
    # return points


def _parse_dxf_points(text: str) -> List[List[float]]:
    """Estrae punti (x, y) da un file DXF (formato testo).

    Supporta le entità più comuni usate per profili topografici:
    - POLYLINE / VERTEX  (DXF R12 e simili)
    - LWPOLYLINE         (DXF R2000+)
    - LINE               (segmenti singoli, endpoint in sequenza)
    - SPLINE             (punti di controllo, group code 10/20)

    Per POLYLINE/VERTEX e LWPOLYLINE restituisce i punti nell'ordine
    in cui compaiono nel file. Il punto (0, 0) in posizione 0 della
    POLYLINE header viene scartato automaticamente.
    """
    lines_raw = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    pairs: List[tuple] = []
    i = 0
    while i + 1 < len(lines_raw):
        pairs.append((lines_raw[i].strip(), lines_raw[i + 1].strip()))
        i += 2

    in_entities = False
    points: List[List[float]] = []
    entity: Optional[str] = None
    vertex: dict = {}
    lw_x: Optional[float] = None
    line_pending: List[Optional[float]] = []   # x in attesa di y per LINE

    def _f(v: str) -> Optional[float]:
        try:
            return float(v)
        except ValueError:
            return None

    for code, val in pairs:
        if code == "2" and val == "ENTITIES":
            in_entities = True
            continue
        if not in_entities:
            continue
        if code == "0" and val == "ENDSEC":
            break

        if code == "0":
            # Chiudi VERTEX corrente prima di cambiare entità
            if entity == "VERTEX" and "10" in vertex and "20" in vertex:
                x, y = vertex["10"], vertex["20"]
                if not (x == 0.0 and y == 0.0 and len(points) == 0):
                    points.append([x, y])
            vertex = {}
            lw_x = None
            entity = val
            continue

        if entity == "VERTEX":
            if code == "10":
                f = _f(val)
                if f is not None:
                    vertex["10"] = f
            elif code == "20":
                f = _f(val)
                if f is not None:
                    vertex["20"] = f

        elif entity == "LWPOLYLINE":
            if code == "10":
                lw_x = _f(val)
            elif code == "20" and lw_x is not None:
                f = _f(val)
                if f is not None:
                    points.append([lw_x, f])
                lw_x = None

        elif entity == "LINE":
            if code in ("10", "11"):
                f = _f(val)
                if f is not None:
                    line_pending.append(f)
            elif code in ("20", "21"):
                f = _f(val)
                if f is not None and line_pending:
                    x_val = line_pending.pop(0)
                    points.append([x_val, f])

        elif entity == "SPLINE":
            if code == "10":
                lw_x = _f(val)
            elif code == "20" and lw_x is not None:
                f = _f(val)
                if f is not None:
                    points.append([lw_x, f])
                lw_x = None

    return points


def _is_dxf_text(text: str) -> bool:
    """Rileva se il testo è un file DXF."""
    for line in text.splitlines()[:20]:
        if line.strip() == "SECTION":
            return True
    return False


def _is_csv_text(text: str) -> bool:
    """Rileva se il testo è in formato CSV (virgola come separatore di colonne).

    Restituisce True se la prima riga significativa contiene virgole usate come
    separatori di campo (non come separatore decimale in stile italiano).
    Il formato italiano usa di norma il TAB come separatore di colonne, quindi
    la presenza di un TAB esclude il rilevamento CSV.
    """
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        # Se c'è un TAB nella riga, è quasi certamente formato legacy (tab-separated)
        if "\t" in line:
            return False
        parts = line.split(",")
        if len(parts) < 2:
            break
        # Almeno un campo non-numerico (es. nome layer, header) → sicuramente CSV
        for p in parts:
            if p.strip() and not _is_numeric(p.strip()):
                return True
        # Tutti i campi numerici e nessun TAB → virgola usata come separatore CSV
        if all(_is_numeric(p.strip()) for p in parts if p.strip()):
            return True
        break
    return False


def _is_numeric(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def _split_csv_fields(line: str) -> List[str]:
    """Splitta una riga CSV rispettando le virgolette."""
    try:
        return next(_csv.reader(_io.StringIO(line)))
    except Exception:
        return line.split(",")


def parse_xy_points(text: str) -> List[List[float]]:
    # Modalità DXF: delegato al parser dedicato
    if _is_dxf_text(text):
        return _parse_dxf_points(text)

    points: List[List[float]] = []

    use_csv = _is_csv_text(text)

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        if use_csv:
            # Modalità CSV: splitta i campi rispettando le virgolette,
            # poi estrai i valori numerici scartando le stringhe di testo
            fields = _split_csv_fields(line)
        else:
            # Modalità legacy: sostituisce le virgole decimali (es. 1,5 → 1.5),
            # poi tratta le virgole rimanenti come separatori
            line = _DECIMAL_COMMA_RE.sub(r"\1.\2", line)
            line = line.replace(",", " ")
            fields = [p for p in _SPLIT_RE.split(line) if p and p.strip()]

        # Estrai solo i valori numerici, scartando quelli testuali
        numeric_parts = []
        for p in fields:
            p = p.strip()
            try:
                numeric_parts.append(float(p))
            except ValueError:
                continue  # scarta header, nomi layer, ecc.

        if len(numeric_parts) < 2:
            continue

        # Prendi i primi due valori numerici come x, y
        points.append([numeric_parts[0], numeric_parts[1]])

    return points

def compute_pendenza_media(points: List[List[float]]) -> Optional[float]:
    if len(points) < 2:
        return None
    try:
        dy = abs(points[-1][1] - points[0][1])
        dx = abs(points[-1][0] - points[0][0])
        if dx == 0:
            return None
        return round(degrees(atan(dy / dx)), 1)
    except Exception:
        return None


def _ensure_shp_extension(path: str) -> str:
    p = path.strip()
    if not p.lower().endswith(".shp"):
        p += ".shp"
    return p


def _writer_compat(shapeout_shp: str) -> shapefile.Writer:
    try:
        w = shapefile.Writer(shapeout_shp, shapeType=shapefile.POLYLINE)
        w.autoBalance = True
        w._compat_mode = "2x"  # type: ignore[attr-defined]
        return w
    except TypeError:
        w = shapefile.Writer(shapefile.POLYLINE)
        w.autoBalance = 1
        w._compat_mode = "1x"  # type: ignore[attr-defined]
        return w


def _writer_close_compat(w: shapefile.Writer, shapeout_shp: str) -> None:
    mode = getattr(w, "_compat_mode", "2x")
    if mode == "1x":
        base = os.path.splitext(shapeout_shp)[0]
        w.save(base)
    else:
        w.close()


def write_ssap_shapefile(shapeout: str, points: List[List[float]], opts: ConvertOptions) -> str:
    shapeout = _ensure_shp_extension(shapeout)
    w = _writer_compat(shapeout)

    # campi tabella
    w.field("SSAP", "C", 3)
    w.field("SSAP_ID", "N", 2, 0)
    w.field("DR_UNDR", "C", 2)
    w.field("PHI", "N", 6, 2)
    w.field("C", "N", 6, 2)
    w.field("CU", "N", 6, 2)
    w.field("GAMMA", "N", 6, 2)
    w.field("GAMMASAT", "N", 6, 2)
    w.field("SIGCI", "N", 6, 2)
    w.field("GSI", "N", 6, 2)
    w.field("MI", "N", 6, 2)
    w.field("D", "N", 6, 2)
    w.field("VAL1", "N", 11, 2)
    w.field("EXCLUDE", "N", 1, 0)

    # feature dat
    w.line([points])
    lv = opts.layer_values
    w.record(
        SSAP="dat", SSAP_ID=1, DR_UNDR="D",
        PHI=lv.phi, C=lv.c, CU=lv.cu, GAMMA=lv.gamma, GAMMASAT=lv.gammasat,
        SIGCI=0, GSI=0, MI=0, D=0, VAL1=0, EXCLUDE=0,
    )

    # feature falda (fld)
    if opts.falda_enabled:
        blist = [[p[0], p[1] - float(opts.falda_depth)] for p in points]
        w.line([blist])
        w.record(
            SSAP="fld", SSAP_ID=0, DR_UNDR="0",
            PHI=0, C=0, CU=0, GAMMA=0, GAMMASAT=0,
            SIGCI=0, GSI=0, MI=0, D=0, VAL1=0, EXCLUDE=0,
        )

    # feature bedrock
    if opts.bedrock_enabled:
        blist = [[p[0], p[1] - float(opts.bedrock_depth)] for p in points]
        w.line([blist])
        w.record(
            SSAP="dat", SSAP_ID=2, DR_UNDR="0",
            PHI=float(opts.phi_br), C=float(opts.c_br), CU=0,
            GAMMA=22, GAMMASAT=22,
            SIGCI=0, GSI=0, MI=0, D=0, VAL1=0, EXCLUDE=0,
        )

    _writer_close_compat(w, shapeout)

    sf = shapefile.Reader(shapeout)
    try:
        if not sf.shapes() or sf.shapes()[0].shapeType != shapefile.POLYLINE or len(sf.shapeRecords()) == 0:
            raise ValueError("Shapefile creato ma non valido (non lineare o senza features).")
    finally:
        safe_close_reader(sf)

    return shapeout


def convert_shp_to_gpkg(shp_path: str, gpkg_path: str, layer_name: str = "") -> str:
    """Converti uno shapefile esistente in GeoPackage usando QgsVectorFileWriter.
    
    Args:
        shp_path: percorso dello shapefile sorgente (.shp)
        gpkg_path: percorso output (.gpkg)
        layer_name: nome del layer interno al GPKG (default: stem del gpkg_path)
    
    Returns:
        gpkg_path se la conversione ha successo.
    
    Raises:
        RuntimeError: se la conversione fallisce.
    """
    from qgis.core import (
        QgsVectorLayer, QgsVectorFileWriter, QgsProject
    )

    if not layer_name:
        layer_name = Path(gpkg_path).stem

    # Carica lo shapefile temporaneo
    lyr = QgsVectorLayer(shp_path, layer_name, "ogr")
    if not lyr.isValid():
        raise RuntimeError(f"Impossibile caricare lo shapefile temporaneo: {shp_path}")

    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "GPKG"
    options.fileEncoding = "UTF-8"
    options.layerName = layer_name

    transform_context = QgsProject.instance().transformContext()
    ret = QgsVectorFileWriter.writeAsVectorFormatV3(
        lyr,
        gpkg_path,
        transform_context,
        options,
    )

    if isinstance(ret, tuple):
        res, err = ret[0], (ret[1] if len(ret) > 1 else "")
    else:
        res, err = ret, ""

    if res != QgsVectorFileWriter.NoError:
        raise RuntimeError(f"Errore durante la scrittura del GeoPackage: {err}")

    if not Path(gpkg_path).exists():
        raise RuntimeError("GeoPackage non creato (file mancante dopo la scrittura).")

    return gpkg_path


def write_ssap_output(shapeout_base: str, points: List[List[float]], opts: ConvertOptions,
                      output_format: str = "shp") -> str:
    """Wrapper che scrive l'output XY come SHP o GPKG in base a output_format.
    
    Args:
        shapeout_base: percorso base senza estensione (o con .shp/.gpkg)
        points: lista di coordinate XY
        opts: opzioni di conversione
        output_format: 'shp' oppure 'gpkg'
    
    Returns:
        percorso del file creato
    """
    import tempfile

    base = Path(shapeout_base).with_suffix("")

    if output_format == "gpkg":
        gpkg_out = str(base) + ".gpkg"
        layer_name = base.name

        # Scrivi prima come SHP temporaneo, poi converti in GPKG
        tmp_dir = Path(tempfile.gettempdir()) / f"shp2ssap_gpkg_{uuid.uuid4().hex}"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        tmp_shp = str(tmp_dir / (base.name + ".shp"))

        try:
            write_ssap_shapefile(tmp_shp, points, opts)
            result = convert_shp_to_gpkg(tmp_shp, gpkg_out, layer_name=layer_name)
        finally:
            try:
                shutil.rmtree(tmp_dir, ignore_errors=True)
            except Exception:
                pass
        return result
    else:
        return write_ssap_shapefile(str(base) + ".shp", points, opts)


# Wrap public module-level functions for call logging
auto_log_module_functions(globals())
