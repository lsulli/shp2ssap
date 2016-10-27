Shp2SSAP.exe ver 1.1.7 build 180 

AUTORE

Lorenzo Sulli -lorenzo.sulli@gmail.com

INDIRIZZO DOWNLOAD

https://github.com/lsulli/shp2ssap

LICENZA

http://www.gnu.org/licenses/gpl.html
o \fromshp2ssap\licenza\gpl.txt

Le procedure fondamentali utilizzano il modulo shapefile.py (credit. https://github.com/GeospatialPython/pyshp)

FUNZIONALITA' PRINCIPALI

Eseguibile per windows per la creazione di file .dat, .geo, .fld, .svr, .sin e .mod per SSAP 2010 (www.SSAP.eu) partendo da shapefile polyline. Integrato tool dedicato per creare uno shapefile monostrato (già strutturato per la creazione di file per SSAP) partendo da un elenco di coordinate cartesiane xy descriventi il profilo morfologico del terreno.

Lo shapefile descrive il modello geometrico (ovvero i dati per il file .dat), comprensivo di falda (dati per il file .fld) se impostat, ai segmenti che descrivono il modello geometrico sono associati gli attributi per la creazione del file .geo. Possono essere inseriti segmenti che descrivono i carichi (dati per file .svr) e polyline ch edescrivono una superficie di verifica singola (per file .sin).

REQUISITI SISTEMA

Windows 32 o 64 bit.
Il file eseguibile non richiede librerie preinstallate (tutti i moduli e le librerie di python sono comprese nel file eseguibile) nè è richiesta l'installazione di software GIS specifici, qualsiasi strumento GIS che permette la modifica degli shapefile è ammesso. Testato con ArcGis 9.2, 10.0, Arcview 3.2 e Qgis 3.1x.

INSTALLAZIONE

Il file Shp2SSAP.exe è un file compresso auto-estraente che può essere installato in qualsiasi directory. Non vengono modificate le chiavi di registro nè creati file all'esterno della directory di installazione. 



In ogni caso prestare particolare attenzione al settaggio delle unità di misura.

Necessita di shapefile in input con struttura geometrica 
e attributi compatibili con le specifiche SSAP (vedi manuale utente SSAP e shapefile modello scaricabile dalla sezione release).

In particolare è richiesta una struttura dati del tipo seguente, 
(non è necessario rispettare ordine dei campi ma è necessario rispettare rigidamente il nome del campo):

(User id) :['USER_ID', 'N', 2, 0]

(Tipo file SSAP): ['SSAP', 'C', 3]

(Valore Angolo d'attrito - gradi ): ['PHI', 'N', 2, 0]

(Coesione efficace - kpa): ['C', 'N', 5, 2]

(Coesione non drenata - kpa ): ['CU', 'N', 5, 2]

(Peso di volume insaturo - KN/mc): ['GAMMA', 'N', 5, 2]

(Peso di volume saturo- KN/mc): ['GAMMASAT', 'N', 5, 2]

(Resistenza Compressione Uniassiale Roccia Intatta - adimensionale): ['SIGCI', 'N', 5, 2]

(Geological Strenght Index - adimensionale):['GSI','N', 5, 2]

(Indice litologico ammasso - adimensionale):['MI','N', 5, 2]

(Fattore di disturbo ammasso - adimensionale):['D','N', 5, 2]

(Valore caratteristico file .svr - Kpa):['VAl1','N', 5, 2]

Nel campo SSAP deve essere indicato a quale file ssap è riferita la polyline.
Valori ammessi per il campo SSAP: .dat, .fld e .svr. 

Per gli strati con campo SSAP uguale è necessario un insieme di valori USER_ID crescenti dall'alto al basso  e continuo da 1 a 20 (come da specifiche SSAP).

Le polyline con SSAP = "dat" e SSAP = "svr" possono essere aggiunte anche intercalate a polyline già esistenti (aggiunta di strati a piacere), deve comunque essere rispettata la sequenza crescente e continua dall'alto al basso del campo USER_ID: quindi nel caso dell'inserimento di un nuovo strato tra due esistenti deve essere aggiornato il campo USER_ID .

Per SSAP = "fld" è ammesso un solo strato con USER_ID = 0

Il file .geo è generato in base ai valori dei campi dedicati (PHI, C, CU etc.), possono essere presenti contemporaneamente valori di C e Cu > 0, l'utente può scegliere se imporre condizioni drenate e non drenate valide per l'intero modello,  
creando rispettivamente file .geo e .mod [nome_input]_c [nome_input]_cu.

Se presente un valore SIGCI>0 viene generato un file geo per strati rocciosi e vengono ignorati i valori dei campi per le terre.

Sono implementate funzioni di contollo della struttura degli shapefile di input (coordinate negative, numero di strati, sequenza corretta ID strati ) che interrompe la procedura e genera un avviso d'errore.

Implementata procedura di triming degli strati che eccedono i valori minimo e massimo dell'ascissa della superficie topografica o sono leggermente inferiori ad essa, utile per editare gli strati senza preoccuparsi della precisione dei punti di inizio e fine. 

A procedura conclusa positivamente saranno creati i file SSAP 
.dat, .geo,  e .mod., i file .fld e .svr saranno presenti se richiesti
Il file .mod potrà essere aperto direttamente da SSAP 
senza ulteriori interventi dell'utente.

E'possibile variare alcuni riferimenti di default editando il file default.txt.

Versione 1.1.6 built 36 - 2015.08.10
Autore: Lorenzo Sulli - lorenzo.sulli@gmail.com
L'uso della procedura fromshp2ssap.py è di esclusiva responsabilità dell'utente, 
In accordo con la licenza l'autore non è responsabile per eventuali risultati errati o effetti dannosi 
su hardware o software dell'utente

Si ringrazia l'autore del modulo shapefile.py, alla base di tutte le funzionalità del presente script.
Crediti e riferimenti: jlawhead<at>geospatialpython.com. http://code.google.com/p/pyshp/
"""
