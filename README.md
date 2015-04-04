fromshp2ssap.py
https://github.com/lsulli/fromshp2ssap
Licenza: http://www.gnu.org/licenses/gpl.html
o \fromshp2ssap\licenza\gpl.txt 

Procedura per la creazione di file .dat, .geo, .fld, .svr e .mod
per SSAP 2010 (www.SSAP.eu) partendo da shapefile polyline.

Richiede Python 3x, incompatibile con Python 2x.
Richiede il modulo shapefile.py (già presente di default nella distribuzione di fromshp2ssap.py)

Necessita di shapefile in input con struttura geometrica 
e attributi compatibili con le specifiche SSAP (vedi manuale utente SSAP).

In particolare è richiesta una struttura dati del tipo seguente, 
rispettando rigidamente ordine e tipologia dei campi:

1° campo utente (User id) :['USER_ID', 'N', 2, 0]

2° campo utente (Tipo file SSAP): ['SSAP', 'C', 3]

3° campo utente (Valore Angolo d'attrito - gradi ): ['PHI', 'N', 2, 0]

4° campo utente (Coesione efficace - kpa): ['C', 'N', 5, 2]

5° campo utente (Coesione non drenata - kpa ): ['CU', 'N', 5, 2]

6° campo utente (Peso di volume insaturo - KN/mc): ['GAMMA', 'N', 5, 2]

7° campo utente (Peso di volume saturo- KN/mc): ['GAMMASAT', 'N', 5, 2]

8° campo utente (Resistenza Compressione Uniassiale Roccia Intatta): ['SIGCI', 'N', 5, 2]

9° campo utente (Geological Strenght Index):['GSI','N', 5, 2]

10° campo utente (Indice litologico ammasso):['MI','N', 5, 2]

11° campo utente (Fattore di disturbo ammasso):['D','N', 5, 2]

12° campo utente (Valore caratteristico file .svr - Kpa):['VAl1','N', 5, 2]


Nel 2° campo utente deve essere indicato a quale file ssap è riferita la polyline.
Valori ammessi: .dat, .fld e .svr. Il fiel .geo è generato in base ai valoridie campi dal 3° al 11°

Nel 12° campo utente è indicato il valore in kpa 

Sono implementate funzioni di contollo della struttura degli shapefile di input.

A procedura conclusa positivamente saranno creati i file SSAP 
.dat, .geo,  e .mod., i file .fld e .svr saranno presenti se richiesti
Il file .mod potrà essere aperto direttamente da SSAP 
senza ulteriori interventi dell'utente.

La procedura distigue tra condzioni drenate e non drenate,  
creando rispettivamente file .geo e .mod [nome_input]_c [nome_input]_cu.

Versione 1.1.6 built 21
Autore: Lorenzo Sulli - lorenzo.sulli@gmail.com
L'uso della procedura fromshp2ssap.py è di esclusiva responsabilità dell'utente, 
In accordo con la licenza l'autore non è responsabile per eventuali risultati errati o effetti dannosi 
su hardware o software dell'utente

Si ringrazia l'autore del modulo shapefile.py, alla base di tutte le funzionalità del presente script.
Crediti e riferimenti: jlawhead<at>geospatialpython.com. http://code.google.com/p/pyshp/
"""
