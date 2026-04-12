from __future__ import annotations

import os
import tempfile
import time
import webbrowser
import os
import subprocess

from pathlib import Path
from typing import Union

from qgis.PyQt.QtCore import Qt, QUrl, QProcess
from qgis.PyQt.QtGui import QGuiApplication, QDesktopServices
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QDoubleSpinBox,
    QMessageBox, QFileDialog, QGroupBox, QFormLayout, QProgressDialog
)

from qgis.core import (
    QgsProject, QgsVectorLayer, QgsVectorFileWriter, QgsWkbTypes,
    QgsProviderRegistry, QgsMessageLog, Qgis
)
from . import core_ssap
from .scripts import trimming_clean
from .scripts import simplify_features
from .scripts import info_message

from .logger_utils import auto_log_methods, enable_file_logging
# set True to create file logging with complete and incremental call of function 
# Warning: create a large txt file "qgis_plugin_log.txt" use only for debug
enable_file_logging(False)  

MY_VERSION=core_ssap.LBL.versione#'2.0.8 - build 276'

@auto_log_methods
class Shp2SSAPDialog(QDialog):
    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.iface = iface
        ui_file = Path(__file__).with_name('Shp2SSAPDialog.ui')
        uic.loadUi(str(ui_file), self)
        self.setWindowTitle("Shp2SSAP - Ver. " + MY_VERSION)

        # runtime state
        self._tmp_dirs = []
        self._clipboard_cache = ""
        self._active_input_layer = None

        # last used output folder (for "open output" buttons)
        self._last_output_folder = ""

        # Connessioni segnali / slot
        self._wire_signals()
        self._ensure_output_open_button_state()

        # Carica i valori di default nei controlli XY solo all'apertura
        self._apply_xy_defaults_from_settings()
        self._update_xy_tab_buttons()
        self._update_shp_buttons()
        self._opts_load()

    def closeEvent(self, event):
        for d in self._tmp_dirs:
            try:
                core_ssap.safe_rmtree(d)
            except Exception:
                pass
        self._tmp_dirs.clear()
        super().closeEvent(event)

    # -------------------------
    # Helpers
    # -------------------------

    def _wire_signals(self):
        # --- Tab XY ---
        self.xy_btn_infile.clicked.connect(self._xy_pick_input_file)
        self.xy_btn_clip.clicked.connect(self._xy_use_clipboard)
        self.xy_btn_out.clicked.connect(self._xy_pick_output_shp)
        self.btn_run_xy.clicked.connect(self._xy_run)
        self.xy_btn_info.clicked.connect(info_message._xy_info)
        self.bd_fld_btn_info.clicked.connect(info_message._bd_fld_info)
        self.ba_btn_info.clicked.connect(info_message._ba_info)
        self.trim_btn_info.clicked.connect(info_message._trim_info)
        self.simp_btn_info.clicked.connect(info_message._simp_info)

        self.btn_help.clicked.connect(self.open_readme_md)

        self.chk_phi.toggled.connect(self.sp_phi.setEnabled)
        self.chk_c.toggled.connect(self.sp_c.setEnabled)
        self.chk_cu.toggled.connect(self.sp_cu.setEnabled)
        self.chk_gamma.toggled.connect(self.sp_gamma.setEnabled)
        self.chk_gammasat.toggled.connect(self.sp_gammasat.setEnabled)
        self.chk_falda.toggled.connect(self.sp_falda.setEnabled)
        self.chk_bedrock.toggled.connect(self.sp_bedrock.setEnabled)
        self.chk_back_analysis.toggled.connect(self._xy_backanalysis_toggle)

        # Default checkbox state
        for cb in (self.chk_phi, self.chk_c, self.chk_cu, self.chk_gamma, self.chk_gammasat):
            cb.setChecked(True)

        # Forza stato iniziale controlli
        self.sp_phi.setEnabled(self.chk_phi.isChecked())
        self.sp_c.setEnabled(self.chk_c.isChecked())
        self.sp_cu.setEnabled(self.chk_cu.isChecked())
        self.sp_gamma.setEnabled(self.chk_gamma.isChecked())
        self.sp_gammasat.setEnabled(self.chk_gammasat.isChecked())
        self.sp_falda.setEnabled(self.chk_falda.isChecked())
        self.sp_bedrock.setEnabled(self.chk_bedrock.isChecked())


        self.xy_input.textChanged.connect(self._update_xy_tab_buttons)
        self.xy_output.textChanged.connect(self._update_xy_tab_buttons)

        # --- Tab SHP ---
        self.btn_input_vec.clicked.connect(self._src_pick_vector)
        self.btn_use_active.clicked.connect(self._src_use_active_layer)
        self.btn_output_base.clicked.connect(self._src_pick_output_base)
        self.btn_check_shp.clicked.connect(self._src_check)
        self.btn_conv_shp.clicked.connect(self._src_convert)
        self.btn_help_2.clicked.connect(self.open_readme_md)
        self.bt_open_SSAP.clicked.connect(self.run_ssap)
        self.btn_trim_shp.clicked.connect(self._trim_shp)
        self.btn_simplify_shp.clicked.connect(self._simplify_shp)
        
        self.shp_input.textChanged.connect(self._update_shp_buttons)
        self.shp_output.textChanged.connect(self._update_shp_buttons)

        # --- Tab Opzioni ---
        self.btn_save.clicked.connect(self._opts_save)
        self.btn_reload.clicked.connect(self._opts_load)
        self.btn_reset.clicked.connect(self._opts_reset)

    # ---------------------------------------------------------------------
    # Compatibility / aliases
    #
    # The UI (.ui) and older plugin versions used different slot names.
    # QGIS loads the dialog and wires signals in __init__; if a referenced slot
    # is missing, the whole plugin fails to open. These thin wrappers keep the
    # slot names stable while delegating to the actual implementation.
    # ---------------------------------------------------------------------

    def _xy_pick_input_file(self):
        """UI slot: pick XY input text file."""
        return self._xy_pick_txt()

    def _xy_use_clipboard(self):
        """UI slot: use clipboard as XY input."""
        return self._xy_from_clipboard()

    def _xy_pick_output_shp(self):
        """UI slot: pick output shapefile for XY conversion."""
        return self._xy_pick_out_shp()

    # def _xy_info(self):
        # """UI slot: show a short help for the XY tab."""
        # msg = (
            # "Formato atteso (un punto per riga):\n"
            # "  X  Y\n"
            # "  oppure X;Y oppure X,Y (separatore spazio/;/,)\n\n"
            # "Esempio:\n"
            # "  12.345 45.678\n"
            # "  12.346 45.679\n\n"
            # "Puoi anche incollare i punti dalla clipboard (pulsante Input clipboard)."
        # )
        # QMessageBox.information(self, "XY → Shapefile (aiuto)", msg)

    # def _bd_fld_info(self):
        # """UI slot: show a short help for the bedrock and fld layers """
        # msg = (
            # "Crea uno strato di base (bedrock)\n"
            # "con resistenza elevata (vedi TAB Opzioni)\n"
            # "alla profondità indicata.\n"
            # "Imposta nello Shapefile SSAP = dat e SSAP_ID = 2 \n\n"
            # "Crea il layer falda (fld) alla profondità indicata. \n"
            # "Imposta nello Shapefile SSAP = fld e SSAP_ID = 0 \n\n"
        # )
        # QMessageBox.information(self, "XY → Shapefile (aiuto)", msg)

    # def _ba_info(self):
        # """UI slot: show a short help for back analysis """
        # msg = (
            # "Crea un modello semplificato utile ad impostare una verifica in back analysis.\n"
            # "Impone un angolo d'attrito pari a pendenza media del pendio\n"
            # "e coesione nulla (condizioni residue).\n\n"
        # )
        # QMessageBox.information(self, "XY → Shapefile (aiuto)", msg)

    def open_readme_md(self):
        """UI slot: Open readme file in github plugin repository
        --------------------------"""
        return webbrowser.open(r'https://github.com/lsulli/shp2ssap/blob/master/README.md')
        
    def run_ssap(self, checked=False):
        percorso = (self.opt_def_ssap_path_exe.text() or "").strip()
        cartella = os.path.dirname(percorso)

        if self.is_ssap_running():
            QMessageBox.information(self, "Avvio di SSAP", "SSAP è già aperto")
            return

        if not os.path.exists(percorso):
            QMessageBox.information(self, "Avvio di SSAP", f"EXE non trovato: {percorso}\n Controllare path in Tab Opzioni \n o verificare installazione")
            return

        res = QProcess.startDetached(percorso, [], cartella)

        # PyQt può restituire bool oppure (bool, pid)
        if isinstance(res, tuple):
            ok, pid = res
            QgsMessageLog.logMessage(f"startDetached ok={ok}, pid={pid}", "SSAP", Qgis.Info)
        else:
            ok = bool(res)
            QgsMessageLog.logMessage(f"startDetached ok={ok}", "SSAP", Qgis.Info)

    def is_ssap_running(self):
        try:
            output = subprocess.check_output(
                'tasklist /FI "IMAGENAME eq ssap2010_64bit.exe"',
                shell=True
            ).decode()
            return "ssap2010_64bit.exe" in output.lower()

        except Exception:
            return False

    def _src_use_active_layer(self):
        """UI slot: use currently active QGIS layer as input."""
        return self._use_active_layer_as_input()

    def _src_pick_output_base(self):
        """UI slot: pick output base path for SSAP files."""
        return self._shp_pick_outbase()

    def _update_shp_buttons(self):
        """UI slot: refresh SHP tab buttons enable state."""
        return self._update_shp_tab_buttons()

    def _run_with_progress(self, title: str, fn):
        dlg = QProgressDialog(title, None, 0, 0, self)
        dlg.setWindowModality(Qt.WindowModal)
        dlg.setCancelButton(None)
        dlg.setMinimumDuration(0)
        dlg.show()
        try:
            return fn()
        finally:
            dlg.close()

    def _open_folder(self, folder: Union[str, Path]):
        p = Path(folder)
        if not p.exists():
            QMessageBox.warning(self, "Apri cartella", f"Cartella non trovata:\n{p}")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(p)))

    def _set_last_output_folder(self, path: Union[str, Path]):
        p = Path(path)
        folder = p if p.is_dir() else p.parent
        self._last_output_folder = str(folder)

    def _ensure_output_open_button_state(self):
        enabled = bool(self._last_output_folder) and Path(self._last_output_folder).exists()
        if hasattr(self, "btn_open_out_xy"):
            self.btn_open_out_xy.setEnabled(enabled)
        if hasattr(self, "btn_open_out_shp"):
            self.btn_open_out_shp.setEnabled(enabled)

    def _apply_xy_defaults_from_settings(self):
        """
        Sincronizza i valori di default (tab Opzioni) nei controlli del tab XY.
        Non forza le checkbox: aggiorna solo i valori visualizzati negli spinbox.
        """
        s = core_ssap.get_settings()

        # Se la UI del tab XY non è ancora stata costruita, esci
        if not hasattr(self, "sp_phi"):
            return

        self.sp_phi.setValue(float(s.get("xy_phi_default", 0.0)))
        self.sp_c.setValue(float(s.get("xy_c_default", 0.0)))
        self.sp_cu.setValue(float(s.get("xy_cu_default", 0.0)))
        self.sp_gamma.setValue(float(s.get("xy_gamma_default", 0.0)))
        self.sp_gammasat.setValue(float(s.get("xy_gammasat_default", 0.0)))
        self.sp_falda.setValue(float(s.get("xy_falda_depth_default", 0.0)))
        self.sp_bedrock.setValue(float(s.get("xy_bedrock_depth_default", 5.0)))

    def _pick_dir_into(self, lineedit: QLineEdit):
        d = QFileDialog.getExistingDirectory(self, "Seleziona cartella", lineedit.text().strip() or "")
        if d:
            lineedit.setText(d)



    def _update_xy_tab_buttons(self):
        # Converti e carica in QGIS: attivo solo con input e output validi
        inp = (self.xy_input.text() or "").strip()
        outp = (self.xy_output.text() or "").strip()

        input_ok = False
        if inp:
            # compat: older builds used MSG_CLIPBOARD_B, current UI uses <CLIPBOARD>
            if inp == "<CLIPBOARD>":
                input_ok = True
            else:
                try:
                    input_ok = Path(inp).exists()
                except Exception:
                    input_ok = False

        output_ok = False
        if outp:
            try:
                p = Path(outp)
                # accetta .shp, .gpkg, o senza estensione (verrà aggiunta)
                valid_ext = p.suffix.lower() in ("", ".shp", ".gpkg")
                parent = p.parent
                output_ok = bool(p.stem) and parent.exists() and valid_ext
            except Exception:
                output_ok = False

        if hasattr(self, "btn_run_xy"):
            self.btn_run_xy.setEnabled(bool(input_ok and output_ok))


    def _xy_backanalysis_toggle(self, enabled: bool):
        if enabled:
            self.chk_phi.setChecked(False)
            self.chk_c.setChecked(False)
            self.chk_phi.setEnabled(False)
            self.chk_c.setEnabled(False)
            self.sp_phi.setEnabled(False)
            self.sp_c.setEnabled(False)
        else:
            self.chk_phi.setEnabled(True)
            self.chk_c.setEnabled(True)
            self.sp_phi.setEnabled(self.chk_phi.isChecked())
            self.sp_c.setEnabled(self.chk_c.isChecked())

    def _xy_pick_txt(self):
        settings = core_ssap.get_settings()
        initial = settings.get("def_shp_dir", "") or ""
        p, _ = QFileDialog.getOpenFileName(self, "Seleziona file di testo", initial, "Text/CSV/DXF (*.txt *.csv *.dxf);;All (*.*)")
        if p:
            self.xy_input.setText(p)

    def _xy_from_clipboard(self):
        txt = QGuiApplication.clipboard().text() or ""
        if not txt.strip():
            QMessageBox.warning(self, "Clipboard", "Clipboard vuota.")
            return
        self._clipboard_cache = txt
        self.xy_input.setText("<CLIPBOARD>")

    def _xy_pick_out_shp(self):
        settings = core_ssap.get_settings()
        initial = settings.get("def_shp_dir", "") or ""
        p, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Output file vettoriale SSAP",
            initial,
            "Shapefile (*.shp);;GeoPackage (*.gpkg);;All (*.*)"
        )
        if p:
            # Aggiunge l'estensione corretta in base al filtro scelto se mancante
            if "gpkg" in selected_filter.lower() and not p.lower().endswith(".gpkg"):
                p += ".gpkg"
            elif "shp" in selected_filter.lower() and not p.lower().endswith((".shp", ".gpkg")):
                p += ".shp"
            self.xy_output.setText(p)


    def _xy_run(self):
        try:
            def work():
                src = self.xy_input.text().strip()
                out = self.xy_output.text().strip()
                if not out:
                    raise RuntimeError("Seleziona un output.")

                # Formato derivato dall'estensione scelta nel file dialog
                fmt = "gpkg" if out.lower().endswith(".gpkg") else "shp"

                if src == "<CLIPBOARD>":
                    text = self._clipboard_cache
                else:
                    p = Path(src)
                    if not p.exists():
                        raise RuntimeError("Input non valido: scegli un file TXT o usa clipboard.")
                    text = p.read_text(encoding="utf-8", errors="replace")

                points = core_ssap.parse_xy_points(text)
                if len(points) < 2:
                    raise RuntimeError("Dati XY insufficienti: servono almeno 2 punti.")

                pendenza = core_ssap.compute_pendenza_media(points)
                use_pendenza = self.chk_back_analysis.isChecked()

                if use_pendenza and pendenza is not None:
                    phi = float(pendenza)
                    c = 0.0
                else:
                    phi = float(self.sp_phi.value()) if self.chk_phi.isChecked() else 0.0
                    c = float(self.sp_c.value()) if self.chk_c.isChecked() else 0.0

                lv = core_ssap.LayerValues(
                    phi=round(phi, 1),
                    c=round(c, 1),
                    cu=round(float(self.sp_cu.value()), 1) if self.chk_cu.isChecked() else 0.0,
                    gamma=round(float(self.sp_gamma.value()), 1) if self.chk_gamma.isChecked() else 0.0,
                    gammasat=round(float(self.sp_gammasat.value()), 1) if self.chk_gammasat.isChecked() else 0.0,
                )

                opts = core_ssap.ConvertOptions(
                    layer_values=lv,
                    use_pendenza_media=use_pendenza,
                    falda_enabled=self.chk_falda.isChecked(),
                    falda_depth=float(self.sp_falda.value()),
                    bedrock_enabled=self.chk_bedrock.isChecked(),
                    bedrock_depth=float(self.sp_bedrock.value()),
                    phi_br=50.0,
                    c_br=500.0,
                )

                return core_ssap.write_ssap_output(out, points, opts, output_format=fmt)

            created = self._run_with_progress("Creazione file SSAP in corso…", work)

            vlayer = QgsVectorLayer(created, Path(created).stem, "ogr")
            if not vlayer.isValid():
                raise RuntimeError("File creato ma QGIS non riesce a caricarlo.")
            QgsProject.instance().addMapLayer(vlayer)

            self._set_last_output_folder(created)
            self._ensure_output_open_button_state()

            fmt_label = "GeoPackage" if created.lower().endswith(".gpkg") else "Shapefile"
            QMessageBox.information(self, f"XY → {fmt_label}", f"Creato e caricato:\n{created}")

        except Exception as e:
            core_ssap.qgis_log_error(f"XY→output error: {type(e).__name__}: {e}")
            QMessageBox.critical(self, "Errore", f"{type(e).__name__}: {e}")


    # -------------------------
    # TAB 2: Vettoriale -> SSAP files
    # -------------------------

    def _update_shp_tab_buttons(self):
        # Verifica preliminare: attiva solo se esiste un input (file o layer attivo)
        inp = (self.shp_input.text() or "").strip()
        input_ok = False
        if inp.startswith("<ACTIVE>"):
            lyr = getattr(self, "_active_input_layer", None)
            input_ok = bool(lyr is not None and lyr.isValid())
        elif inp:
            try:
                p = Path(inp)
                input_ok = p.exists()
            except Exception:
                input_ok = False

        # Converti: richiede anche un output base valido
        outb = (self.shp_output.text() or "").strip()
        output_ok = False
        if outb:
            try:
                p = Path(outb)
                output_ok = bool(p.name) and (p.parent.exists() or str(p.parent) in ("", "."))
            except Exception:
                output_ok = False

        # Applica stati
        if hasattr(self, "btn_simplify_shp"):
            self.btn_simplify_shp.setEnabled(bool(input_ok))
        if hasattr(self, "btn_trim_shp"):
            self.btn_trim_shp.setEnabled(bool(input_ok))
        if hasattr(self, "btn_check_shp"):
            self.btn_check_shp.setEnabled(bool(input_ok))
        if hasattr(self, "btn_conv_shp"):
            self.btn_conv_shp.setEnabled(bool(input_ok and output_ok))

    def _use_active_layer_as_input(self):
        layer = self.iface.activeLayer()
        if layer is None or not isinstance(layer, QgsVectorLayer) or not layer.isValid():
            QMessageBox.warning(self, "Layer attivo", "Nessun layer vettoriale attivo valido.")
            return
        self._active_input_layer = layer
        self.shp_input.setText(f"<ACTIVE> {layer.name()}")
        self._update_shp_tab_buttons()

    def _src_pick_vector(self):
        settings = core_ssap.get_settings()
        initial = settings.get("def_shp_dir", "") or ""
        p, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona layer vettoriale (SHP, GPKG, GeoJSON, …)",
            initial,
            "Vector data (*.shp *.gpkg *.geojson *.json *.gml *.kml *.tab *.mif *.sqlite);;All (*.*)"
        )
        if p:
            self._active_input_layer = None
            self.shp_input.setText(p)

    def _shp_pick_outbase(self):
        settings = core_ssap.get_settings()
        initial = settings.get("def_ssap_dir", "") or ""
        p, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Output SSAP (base nome file)",
            initial,
            "SSAP MOD (*.mod);;GeoPackage (*.gpkg);;All (*.*)"
        )
        if p:
            # Memorizza il formato scelto per usarlo in _src_convert
            self._shp_out_fmt = "gpkg" if "gpkg" in selected_filter.lower() else "shp"
            # Salva solo il nome base senza estensione
            self.shp_output.setText(str(Path(p).with_suffix("")))


    def _layer_from_path(self, path: str) -> QgsVectorLayer:
        p = Path(path)
        if not p.exists():
            raise RuntimeError("File input non trovato.")

        lyr = QgsVectorLayer(path, p.stem, "ogr")
        if lyr.isValid():
            return lyr

        if p.suffix.lower() == ".gpkg":
            # Tentativo: query sublayers tramite provider metadata
            try:
                md = QgsProviderRegistry.instance().providerMetadata("ogr")
                subs = md.querySublayers(path)
                names = []
                for s in subs or []:
                    name = None
                    if isinstance(s, dict):
                        name = s.get("name") or s.get("layerName")
                    else:
                        name = getattr(s, "name", None) or getattr(s, "layerName", None)
                    if name:
                        names.append(str(name))

                if len(names) == 1:
                    uri = f"{path}|layername={names[0]}"
                    lyr2 = QgsVectorLayer(uri, names[0], "ogr")
                    if lyr2.isValid():
                        return lyr2

                raise RuntimeError(
                    "GeoPackage con più layer o non risolvibile automaticamente.\n"
                    "Carica il layer desiderato in QGIS e usa 'Usa layer attivo',\n"
                    "oppure esportalo come SHP."
                )
            except Exception:
                raise RuntimeError(
                    "Impossibile determinare i layer interni del GeoPackage.\n"
                    "Carica il layer desiderato in QGIS e usa 'Usa layer attivo',\n"
                    "oppure esportalo come SHP."
                )

        raise RuntimeError("Impossibile caricare il layer. Prova a caricarlo in QGIS e usa 'Usa layer attivo'.")

    def _export_layer_to_temp_shp(self, layer: QgsVectorLayer) -> Path:
        if QgsWkbTypes.geometryType(layer.wkbType()) != QgsWkbTypes.LineGeometry:
            raise RuntimeError("Il layer deve essere lineare (Polyline).")

        tmp_dir = Path(tempfile.gettempdir()) / f"shp2ssap_qgis_{os.getpid()}_{int(time.time())}"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        self._tmp_dirs.append(tmp_dir)

        out_shp = tmp_dir / "input_export.shp"

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        options.fileEncoding = "UTF-8"

        transform_context = QgsProject.instance().transformContext()
        ret = QgsVectorFileWriter.writeAsVectorFormatV3(
            layer,
            str(out_shp),
            transform_context,
            options
        )
        # QGIS cambia la signature tra versioni: può ritornare 2, 3 o più valori.
        if isinstance(ret, tuple):
            res = ret[0]
            err = ret[1] if len(ret) > 1 else ""
        else:
            res = ret
            err = ""
        if res != QgsVectorFileWriter.NoError:
            raise RuntimeError(f"Errore export a SHP: {err}")

        if not out_shp.exists():
            raise RuntimeError("Export a shapefile non riuscito (file mancante).")

        return out_shp

    def _resolve_input_to_shp(self) -> Path:
        src = self.shp_input.text().strip()
        if not src:
            raise RuntimeError("Scegli un input (SHP/GPKG/…).")

        if src.startswith("<ACTIVE>"):
            layer = self._active_input_layer
            if layer is None or not layer.isValid():
                raise RuntimeError("Layer attivo non disponibile.")
            return self._export_layer_to_temp_shp(layer)

        p = Path(src)
        if not p.exists():
            raise RuntimeError("File input non trovato.")

        if p.suffix.lower() == ".shp":
            return p

        layer = self._layer_from_path(src)
        return self._export_layer_to_temp_shp(layer)

    def _src_check(self):
        try:
            def work():
                shp = self._resolve_input_to_shp()
                sf = core_ssap.shapefile.Reader(str(shp))
                try:
                    fi, _ = core_ssap.get_field_index(sf)
                    feats = core_ssap.iter_features(sf, fi)
                    core_ssap.run_precheck(
                        sf, feats,
                        check_topbottom=self.opt_check_topbottom.isChecked(),
                    )
                finally:
                    core_ssap.safe_close_reader(sf)
                return shp

            shp = self._run_with_progress("Verifica preliminare in corso…", work)
            QMessageBox.information(self, "Verifica", f"Layer OK per SSAP:\n{shp}")

        except Exception as e:
            core_ssap.qgis_log_error(f"Check error: {type(e).__name__}: {e}")
            QMessageBox.critical(self, "Errore", f"{type(e).__name__}: {e}")

    def _src_convert(self):
        try:
            # Formato determinato dall'ultima selezione in _shp_pick_outbase
            fmt = getattr(self, "_shp_out_fmt", "shp")

            def work():
                shp = self._resolve_input_to_shp()
                outb = Path(self.shp_output.text().strip())
                if not outb.name:
                    raise RuntimeError("Imposta un output base.")
                if not outb.parent.exists():
                    raise RuntimeError("Cartella output non valida.")

                created = core_ssap.write_ssap_files(
                    shp_path=shp,
                    out_base=outb,
                    check_topbottom=self.opt_check_topbottom.isChecked(),
                )

                # Se richiesto GPKG, esporta anche il layer in GeoPackage
                if fmt == "gpkg":
                    gpkg_out = str(outb) + ".gpkg"
                    layer_name = outb.name
                    core_ssap.convert_shp_to_gpkg(str(shp), gpkg_out, layer_name=layer_name)
                    created.append(Path(gpkg_out))

                return created

            created = self._run_with_progress("Conversione SSAP in corso…", work)

            outb = Path(self.shp_output.text().strip())
            self._set_last_output_folder(outb)
            self._ensure_output_open_button_state()

            QMessageBox.information(self, "Conversione", "Creati:\n" + "\n".join(str(p) for p in created))

        except Exception as e:
            core_ssap.qgis_log_error(f"Convert error: {type(e).__name__}: {e}")
            QMessageBox.critical(self, "Errore", f"{type(e).__name__}: {e}")


    # -------------------------
    # TAB 3: Opzioni (QSettings)
    # -------------------------

    def _opts_save(self):
        try:
            values = {
                "def_shp_dir": (self.opt_def_shp_dir.text() or "").strip(),
                "def_ssap_dir": (self.opt_def_ssap_dir.text() or "").strip(),
                "def_ssap_path_exe":(self.opt_def_ssap_path_exe.text() or "").strip(),
                "num_max_nodi_default":int(self.sp_max_node_number.value()),

                # default valori tab XY
                "xy_phi_default": float(self.opt_xy_phi.value()),
                "xy_c_default": float(self.opt_xy_c.value()),
                "xy_cu_default": float(self.opt_xy_cu.value()),
                "xy_gamma_default": float(self.opt_xy_gamma.value()),
                "xy_gammasat_default": float(self.opt_xy_gammasat.value()),
                "xy_falda_depth_default": float(self.opt_xy_falda.value()),
                "xy_bedrock_depth_default": float(self.opt_xy_bedrock.value()),
                "xy_phi_br_default": float(self.opt_xy_phi_br.value()),
                "xy_c_br_default": float(self.opt_xy_c_br.value()),
            }
            core_ssap.save_settings(values)
            self._opts_load()  # rilegge e applica anche alla tab XY (solo su ricarica esplicita)
        except Exception as e:
            core_ssap.qgis_log_error(f"Options save error: {type(e).__name__}: {e}")
            QMessageBox.critical(self, "Errore", f"{type(e).__name__}: {e}")

    def _opts_load(self):
        try:
            s = core_ssap.get_settings()
            self.opt_def_shp_dir.setText(s.get("def_shp_dir", ""))
            self.opt_def_ssap_dir.setText(s.get("def_ssap_dir", ""))
            self.opt_def_ssap_path_exe.setText(s.get("def_ssap_path_exe", r"C:\SSAP2010\ssap2010_64bit.exe"))
            self.sp_max_node_number.setValue(int(s.get("num_max_nodi_default", 99)))
            
            self.opt_xy_phi.setValue(float(s.get("xy_phi_default", 0.0)))
            self.opt_xy_c.setValue(float(s.get("xy_c_default", 0.0)))
            self.opt_xy_cu.setValue(float(s.get("xy_cu_default", 0.0)))
            self.opt_xy_gamma.setValue(float(s.get("xy_gamma_default", 0.0)))
            self.opt_xy_gammasat.setValue(float(s.get("xy_gammasat_default", 0.0)))
            self.opt_xy_falda.setValue(float(s.get("xy_falda_depth_default", 0.0)))
            self.opt_xy_bedrock.setValue(float(s.get("xy_bedrock_depth_default", 5.0)))
            self.opt_xy_phi_br.setValue(float(s.get("xy_phi_br_default", 50.0)))
            self.opt_xy_c_br.setValue(float(s.get("xy_c_br_default", 500.0)))

            # Applica ai controlli XY solo quando l'utente preme "Ricarica"
            self._apply_xy_defaults_from_settings()
        except Exception as e:
            core_ssap.qgis_log_error(f"Options load error: {type(e).__name__}: {e}")
            QMessageBox.critical(self, "Errore", f"{type(e).__name__}: {e}")




    def _opts_reset(self):
        try:
            core_ssap.save_settings(core_ssap.DEFAULTS_FALLBACK)
            self._opts_load()
        except Exception as e:
            core_ssap.qgis_log_error(f"Options reset error: {type(e).__name__}: {e}")
            QMessageBox.critical(self, "Errore", f"{type(e).__name__}: {e}")


    def _resolve_shp_input_to_layer(self):
        """Risolvi il contenuto di shp_input in un QgsVectorLayer valido."""
        from qgis.core import QgsProject, QgsVectorLayer

        src = (self.shp_input.text() or "").strip()
        if not src:
            raise RuntimeError("Input mancante: compila il campo 'shp_input'.")

        # Caso '<ACTIVE>' (se usato dal plugin)
        if src.startswith("<ACTIVE>"):
            layer = getattr(self, "_active_input_layer", None) or self.iface.activeLayer()
            if layer is None or not isinstance(layer, QgsVectorLayer) or not layer.isValid():
                raise RuntimeError("Layer attivo non disponibile o non valido.")
            return layer

        # Se è già in progetto con stessa source, riusa
        try:
            from pathlib import Path
            p = Path(src).resolve()
        except Exception:
            p = None

        if p is not None:
            for lyr in QgsProject.instance().mapLayers().values():
                if isinstance(lyr, QgsVectorLayer) and lyr.isValid():
                    try:
                        if Path(lyr.source()).resolve() == p:
                            return lyr
                    except Exception:
                        pass

        # Altrimenti carica da path
        layer = self._layer_from_path(src)
        if layer is None or not layer.isValid():
            raise RuntimeError("Impossibile caricare il layer da 'shp_input'.")
        QgsProject.instance().addMapLayer(layer)
        return layer


    def _trim_shp(self):
        """Esegue trimming su layer indicato in shp_input (crea copia memory)."""
        from qgis.core import QgsMessageLog, Qgis
        from qgis.PyQt.QtWidgets import QMessageBox

        try:
            layer = self._resolve_shp_input_to_layer()

            # Esegui trimming: di default NON in-place → crea layer memory
            out_name = f"{layer.name()}_trim"
            if self.chk_edit_shp.isChecked():
                edit_shp = True
                edit_shp_msg = 'modificato: '
            else: 
                edit_shp = False
                edit_shp_msg = 'creato: '
            out_layer = trimming_clean.clip_lines_by_x_range(
                layer=layer,
                id_field="SSAP_ID",
                topo_id_value=1,
                edit_in_place=edit_shp,
                output_name=out_name,
                delete_if_empty=False
            )

            QMessageBox.information(
                self,
                "Trimming",
                f"Trimming completato.\nLayer {edit_shp_msg} {out_layer.name()}"
            )

        except Exception as e:
            QgsMessageLog.logMessage(str(e), "Shp2SSAP_Trim", Qgis.Critical)
            QMessageBox.critical(
                self,
                "Errore trimming",
                f"{type(e).__name__}: {e}"
            )

    def _simplify_shp(self):
        """Esegue semplificazione delle singole feature in base al numero di nodi impostato (massimo 99)"""
        from qgis.core import QgsMessageLog, Qgis
        from qgis.PyQt.QtWidgets import QMessageBox

        try:
            layer = self._resolve_shp_input_to_layer()
            num_points = int(self.sp_max_node_number.value())

            # Esegui simplify→ crea layer memory
            out_name = f"{layer.name()}_simply"
            
            if self.chk_simplify_shp.isChecked():
                edit_shp = True
                edit_shp_msg = 'modificato: '
            else: 
                edit_shp = False
                edit_shp_msg = 'creato: '
            out_layer = simplify_features.simplify_geometries(layer= layer, edit_original=edit_shp, max_points=num_points)

            QMessageBox.information(
                self,
                "Simplify features",
                f"Semplificazione completata.\nLayer {edit_shp_msg} {out_layer.name()}"
            )

        except Exception as e:
            QgsMessageLog.logMessage(str(e), "Shp2SSAP_Simplify", Qgis.Critical)
            QMessageBox.critical(
                self,
                "Errore Simplify features",
                f"{type(e).__name__}: {e}"
            )

