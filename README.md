fromshp2ssap.py ver 1.1.6 build 36 - Pre-release 
https://github.com/lsulli/fromshp2ssap
Licenza: http://www.gnu.org/licenses/gpl.html
o \fromshp2ssap\licenza\gpl.txt 

Procedura per la creazione di file .dat, .geo, .fld, .svr e .mod
per SSAP 2010 (www.SSAP.eu) partendo da shapefile polyline.

Richiede Python 3x, incompatibile con Python 2x.
Richiede il modulo shapefile.py ultima versione 1.2.3 (https://github.com/GeospatialPython/pyshp) modulo che può essere copiato in .\Python3X\Lib o in una directory .\moduli_py presente nella directory di residenza del presente file .py

Necessita di shapefile in input con struttura geometrica 
e attributi compatibili con le specifiche SSAP (vedi manuale utente SSAP).

In particolare è richiesta una struttura dati del tipo seguente, 
(non è necessario rispettare ordine dei campi ma è necessario rispettare rigidamente il nome del campo):

(User id) :['USER_ID', 'N', 2, 0]

(Tipo file SSAP): ['SSAP', 'C', 3]

(Valore Angolo d'attrito - gradi ): ['PHI', 'N', 2, 0]

(Coesione efficace - kpa): ['C', 'N', 5, 2]

(Coesione non drenata - kpa ): ['CU', 'N', 5, 2]

(Peso di volume insaturo - KN/mc): ['GAMMA', 'N', 5, 2]

(Peso di volume saturo- KN/mc): ['GAMMASAT', 'N', 5, 2]

(Resistenza Compressione Uniassiale Roccia Intatta adimensionale): ['SIGCI', 'N', 5, 2]

(Geological Strenght Index - adimensionale):['GSI','N', 5, 2]

(Indice litologico ammasso - adimensionale):['MI','N', 5, 2]

(Fattore di disturbo ammasso - adimensionale):['D','N', 5, 2]

(Valore caratteristico file .svr - Kpa):['VAl1','N', 5, 2]

Nel campo SSAP deve essere indicato a quale file ssap è riferita la polyline.
Valori ammessi per il campo SSAP: .dat, .fld e .svr. 

Per gli strati con campo SSAP uguale è necessario un insieme di valori USER_ID crescenti dall'alto al basso  e continuo da 1 a n (come da specifiche SSAP).

Le polyline con SSAP = "dat" e SSAP = "svr" possono essere aggiunte anche intercalate a polyline già esistenti (aggiunta di strati a piacere), deve comunque essere rispettata la sequenza crescente e continua dall'alto al basso.

Per SSAP = "fld" è ammesso un solo strato con USER_ID = 0

Il file .geo è generato in base ai valori dei campi dedicati (C, CU etc.)
Se presente un valore SIGCI>0 viene generato un file geo per strati rocciosi

Sono implementate funzioni di contollo della struttura degli shapefile di input (coordinate negative, numero di strati etc.).

A procedura conclusa positivamente saranno creati i file SSAP 
.dat, .geo,  e .mod., i file .fld e .svr saranno presenti se richiesti
Il file .mod potrà essere aperto direttamente da SSAP 
senza ulteriori interventi dell'utente.

La procedura distigue tra condzioni drenate e non drenate,  
creando rispettivamente file .geo e .mod [nome_input]_c [nome_input]_cu.

E'possibile impostare dei riferimenti editando il file default.txt.

Versione 1.1.6 built 36 - 2015.08.10
Autore: Lorenzo Sulli - lorenzo.sulli@gmail.com
L'uso della procedura fromshp2ssap.py è di esclusiva responsabilità dell'utente, 
In accordo con la licenza l'autore non è responsabile per eventuali risultati errati o effetti dannosi 
su hardware o software dell'utente

Si ringrazia l'autore del modulo shapefile.py, alla base di tutte le funzionalità del presente script.
Crediti e riferimenti: jlawhead<at>geospatialpython.com. http://code.google.com/p/pyshp/
"""
