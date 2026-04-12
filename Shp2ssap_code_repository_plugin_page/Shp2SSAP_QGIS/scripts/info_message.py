
from qgis.PyQt.QtWidgets import QMessageBox, QSpacerItem, QSizePolicy
from qgis.PyQt.QtCore import Qt

MSG_WIDTH = 350  # larghezza in pixel delle finestre di messaggio

def _set_msg_width(msg, width=MSG_WIDTH):
    """Forza la larghezza minima di un QMessageBox tramite uno spacer nel layout."""
    layout = msg.layout()
    layout.addItem(
        QSpacerItem(width, 0, QSizePolicy.Minimum, QSizePolicy.Expanding),
        layout.rowCount(), 0, 1, layout.columnCount()
    )


def _xy_info():
    """UI slot: show a short help for the XY import"""
    msg = QMessageBox()
    msg.setWindowTitle("XY → Shapefile (aiuto)")
    msg.setTextFormat(Qt.RichText)
    msg.setText(
        '<p align="justify">'
        "Formato tipo (un punto per riga): X;Y <br>"
        "Separatore: spazio, virgola, semicolon, tab <br>"
        "Esclude automaticamente testo e righe vuote <br>"
        "Esempio:<br>"
        "  12.345;45.678 <br>"
        "  12.346;45.679 <br><br>"
        "File tipo ammessi: <br>"
        "- dxf 2D generati da Elevation Profile o Profile Plugin <br>"
        "- csv generati da Elevation Profile <br>"
        "E' possibile incollare i valori dalla clipboard " 
        "(pulsante <i>Input clipboard</i>)<br>"
        "copiati da Profile Plugin <br>"
        "</p>"
    )
    msg.setStandardButtons(QMessageBox.Ok)
    _set_msg_width(msg)
    msg.exec_()

def _bd_fld_info():
    """UI slot: show a short help for the bedrock and fld layers """
    msg = QMessageBox()
    msg.setWindowTitle("XY → Shapefile (aiuto)")
    msg.setTextFormat(Qt.RichText)
    msg.setText(
        '<p align="justify">'
        "Crea uno strato di base (bedrock) con resistenza elevata alla profondità indicata <br>"
        "Imposta nello Shapefile <i>SSAP</i> = dat e <i>SSAP_ID</i> = 2 <br><br>"
        "Crea il layer falda alla profondità indicata.<br>"
        "Imposta nello Shapefile <i>SSAP</i> = fld e <i>SSAP_ID</i> = 0 <br>"
        "</p>"
    )
    msg.setStandardButtons(QMessageBox.Ok)
    _set_msg_width(msg)
    msg.exec_()

def _ba_info():
    """UI slot: show a short help for back analysis """
    msg = QMessageBox()
    msg.setWindowTitle("XY → Shapefile (aiuto)")
    msg.setTextFormat(Qt.RichText)
    msg.setText(
        '<p align="justify">'
        "Crea un modello semplificato utile ad impostare una verifica in back analysis.<br>"
        "Impone un angolo d'attrito pari a pendenza media del pendio<br>"
        "e coesione nulla (condizioni residue).<br><br>"
        "</p>"
    )
    msg.setStandardButtons(QMessageBox.Ok)
    _set_msg_width(msg)
    msg.exec_()
    
def _simp_info():
    """UI slot: show a short help for simplify feature """
    msg = QMessageBox()
    msg.setWindowTitle("Vettoriale → files SSAP (aiuto)")
    msg.setTextFormat(Qt.RichText)
    msg.setText(
        '<p align="justify">'
        "Semplifica tutte le polyline del layer riducendo il numero di nodi al valore indicato. "
        "Comando necessario nel caso di polyline con più di 100 vertici (limite di SSAP) "
        "come nel caso di profili estratti da dtm.<br><br>"
        "Crea di default un nuovo layer '<i>nomelayer_semplificato'</i>"
        "</p>"
    )
    msg.setStandardButtons(QMessageBox.Ok)
    _set_msg_width(msg)
    msg.exec_()
    
def _trim_info():
    """UI slot: show a short help for trimming feature """
    msg = QMessageBox()
    msg.setWindowTitle("Vettoriale → files SSAP (aiuto)")
    msg.setTextFormat(Qt.RichText)
    msg.setText(
        '<p align="justify">'
        "Taglia tutte le polyline con estremi esterni ai limiti Xmin e Xmax della superficie topografica."
        "Comando utile nel caso di editing con inserimento di nuovi strati: "
        "è infatti sufficiente estendere la polyline oltre i limiti della superficie topografica "
        "senza curarsi di posizionare esattamente i nodi esterni<br><br>"
        "Crea di default un nuovo layer <i>'nomelayer_trim'</i>"
        "</p>"
    )
    msg.setStandardButtons(QMessageBox.Ok)
    _set_msg_width(msg)
    msg.exec_()
