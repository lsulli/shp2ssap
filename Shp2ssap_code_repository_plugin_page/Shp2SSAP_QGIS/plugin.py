import os

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .dialog import Shp2SSAPDialog


from .logger_utils import auto_log_methods

@auto_log_methods
class Shp2SSAPPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dlg = None
        self.plugin_dir = os.path.dirname(__file__)

    def tr(self, msg: str) -> str:
        return QCoreApplication.translate("Shp2SSAP", msg)

    def initGui(self):
        self.action = QAction(QIcon(os.path.join(self.plugin_dir, "icons/xy2Shp_forSSAP.ico")), self.tr("Shp2SSAP"), self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.action.setToolTip(self.tr("Shp2SSAP (XY↔SHP↔SSAP)"))
        self.action.setStatusTip(self.tr("Converti XY↔Shapefile↔SSAP"))
        self.iface.addPluginToMenu(self.tr("&Shp2SSAP"), self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
    # chiude il file di log così Windows permette l'eliminazione
        import logging

        for handler in logging.root.handlers[:]:
            handler.close()
            logging.root.removeHandler(handler)
        if self.action:
            self.iface.removePluginMenu(self.tr("&Shp2SSAP"), self.action)
            self.iface.removeToolBarIcon(self.action)

    def run(self):
        if self.dlg is None:
            self.dlg = Shp2SSAPDialog(self.iface)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()
