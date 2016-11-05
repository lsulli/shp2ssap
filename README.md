##**Shp2SSAP.exe ver 1.1.7 build 174**##

Applicazione per creare shapefile polyline di un modello del pendio partendo da un elenco coordinate e convertire lo shapefile in file per SSAP2010 (www.ssap.eu).

**AUTORE**

Lorenzo Sulli - lorenzo.sulli@gmail.com

**INDIRIZZO DOWNLOAD**

https://github.com/lsulli/shp2ssap

**UPGRADE**

Versione 1.1: aggiunto e integrato tool xy2shp_forSSAP.exe

**LICENZA**

http://www.gnu.org/licenses/gpl.html

Le procedure fondamentali utilizzano il modulo shapefile.py (credit. https://github.com/GeospatialPython/pyshp)

Per il software SSAP2010 vedi termini di licenza riportati in www.SSAP.eu. (Autore Lorenzo Borselli)

**REQUISITI SISTEMA**

Applicativo sviluppato con Python 3x a 32 bit, S.O. Windows 32 o 64 bit (richiesti con Windows 7 o superiore, Windows 8x, windows 10, non è stato testato per Windows Vista, incompatibil econ Windows xp). Il file eseguibile non richiede librerie preinstallate (tutti i moduli e le librerie di python sono comprese nel file eseguibile) nè è richiesta l'installazione di software GIS specifici, qualsiasi strumento GIS che permette la modifica degli shapefile è ammesso. Testato con ArcGis 9.2, 10.0, Arcview 3.2 e Qgis 2.1x.
Non è strettamente necessario che sia installato SSAP2010 ma è vivamente consigliato per la verifica dei file creati.
    
    ATTENZIONE: per il corretto uso di questo applicativo è necessario conoscere le nozioni fondamentali 
    di SSAP2010, in particolare i criteri di costruzione dei file .dat.

**FUNZIONALITA' PRINCIPALI**

Eseguibile per windows per la creazione di file .dat, .geo, .fld, .svr, .sin e .mod per SSAP2010 (www.SSAP.eu) partendo da un unico shapefile polyline. Sfruttando le funzionalità GIS è possibile gestire in forma integrata l'editing della geometria per i file .dat, .fld, .svr  e .sin e i dati delle informazioni per il file .geo e .svr. 

Direttamente dall'interfaccia dell'eseguibile Shp2SSAP.exe è attivabile un tool specifico (xy2shp_forSSAP.exe) per creare uno shapefile monostrato (già strutturato per la creazione di file per SSAP) partendo da un elenco di coordinate cartesiane xy descriventi il profilo morfologico del terreno. Lo shapefile descrive il modello geometrico (ovvero i dati per il file .dat), comprensivo di falda (dati per il file .fld) se impostato dall'utente, alle polyline che descrivono il modello geometrico sono associati gli attributi per la creazione del file .geo. Editando lo Shapefile in ambiente GIS Possono essere modificati gli attributi per il file .geo, aggiunte altre polyline che descrivono altri strati, carichi (dati per file .svr) e una superficie di verifica singola (per file .sin).

**INSTALLAZIONE**

Il file **Shp2SSAP_setup.exe** è un file compresso auto-estraente con procedura guidata. Non vengono modificate le chiavi di registro nè creati file all'esterno della directory di installazione. Vengono copiati nella directory scelta vari file e subdirectory. Si consiglia di non spostare nessun file dalle directory d'installazione, in ogni caso i file **Shp2SSAP.exe** e **xy2Shp_forSSAP.exe** devono risiedere nella stessa directory per la corretta funzionalità dell'applicazione.

**GUIDA All'USO**

Una volta completata l'installazione individuare la directory d'installazione e avviare il file **Shp2SSAP.exe**; il collegamento sul desktop deve essere creato dall'utente.

    ATTENZIONE: l'antivirus al primo avvio può eseguire un controllo dell'eseguibile.
    Il controllo può richiedere alcuni secondi e viene eseguito di norma solo al primo avvio.

Si aprirà un interfaccia GUI (Graphic User Interface) dal quale sarà possibile aprire un file shapefile polyline esistente (tasto *Input Shapefile*) e indicare i file SSAP2010 di output (tasto *Output SSAP files*). Di default vengono lette le directory indicate nel file *default.txt* che può essere modificato a piacimento.

Gli shapefile secondo i requisiti richiesti possono essere creati tramite il tool **xy2Shp_forSSAP.exe** avviabile direttamente dall'interfaccia di Shp2SSAP (tasto *Crea Shape da XY*) e quindi modificati ed integrati in ambiente GIS.  

    ATTENZIONE: Nel caso venga aperta una sezione ex-novo in ambiente GIS fare molta attenzione ad impostare 
    unità di misura metriche. Il sistema di coordinate scelto può deve essere anch'esso metrico. 
    L'uso del sistema EPSG 3003 (Monte Mario Italy 1) o di altri sistemi metrici validi per l'Italia 
    è perfettamente compatibile, se il modello del pendio utilizza coordinate cartesiane assolute per le ascisse 
    lo shapefile del modello pendio sarà proiettato in basso a sinistra rispetto all'Italia.

Una volta aperto lo shapefile in ambiente GIS potranno essere aggiunti gli strati per .dat, carichi per .svr, la falda per .fld e una superficie per la verifica singola (.sin). 

    ATTENZIONE: la geometria della polyline .sin è particolarmente critica per le compatibilità 
    richieste da SSAP, deve quindi essere editata con criterio.
    
La diversa tipologia di strato è identificata dall'attributo nel campo **SSAP**. I valori dei parametri geotecnici per terre e rocce dovranno essere aggiunti nei campi dedicati (PHI, C, ....vedi oltre per i dettagli). La condizione drenata / non drenata deve essere impostata nel campo **DR_UNDR**. Se **SSAP** = svr i carichi devono essere specificati nel campo **VAL**. Particolare attenzione deve essere posta all'assegnazione dell'indice (campo **SSAP_ID**) che deve rispettare i requisiti per SSAP2010, ovvero essere univoco, continuo e crescente dall'alto verso il basso. 
Leggere con attenzione i dettagli nel paragrafo "CARATTERISTICHE DELLO SHAPEFILE MODELLO PENDIO".
Nella cartella **Shapefile_ModelliPendio** sono disponibili shapefile di alcuni modelli di pendio completi.

    ATTENZIONE: Una volta editato lo shapefile è indispensabile chiudere la sezione di editing. 
    Talvolta è necessario chiudere l'applicativo GIS o esportare lo shapefile modificato come copia, 
    la conversione dello shapefile in file SSAP può generare errori nei file di output quando 
    gli shapefile sono letti contemporaneamente da due applicativi, casistica che si presenta frequentemente 
    con Qgis e più raramente con ArcGIS.    

Con il tasto *Verifica Preliminare Shape* è possibile eseguire un controllo dello shapefile di input senza generare file SSAP2010, verranno indicati eventuali errori rispetto alle specifiche SSAP2010 o indicate informazioni generali se il file risulta corretto. Il tasto *Converti* esegue la conversione da shapefile a file per SSA2010, nel caso di errori nel file di input questi vengono comunicati (come per la verifica preliminare) e la conversione è interrotta, se lo shapefile rispetta le specifiche SSAP2010 verranno generati sempre file .mod, .dat, .geo. I file .fld, .svr e .sin sono presenti se sono inserite le relative polyline nello shapefile. In fase di generazione dei file SSAP2010 possono essere attivate opzioni per il controllo avanzato delle sequenza verticale degli strati e per forzare l'estensione degli strati ai limiti della superficie topografica.
    
Il tasto *Crea Shape da XY* permette di avviare il tool **xy2Shp_forSSAP.exe** per creare uno shapefile polyline della superficie topografica da un elenco di coordinate xy (in SSAP2010 strato unico con **SSAP_ID** = 1), le coordinate dovranno avere valori e ordinamento secondo gli standard del file .dat per SSAP. Lo Shapefile avrà tutte le caratteristiche per generare con Shp2SSAP.exe un modello di pendio monostrato per SSAP. Nella cartella **ProfiliXY_Input** è riportato un profilo d'esempio.

    ATTENZIONE: La struttura tipo del file XY ammessa è quella tipica generata dagli strumenti GIS 
    per la creazione di profili da DTM. Il file deve essere un file ascii (.txt per default). 
    Le due colonne di coordinate dovranno essere separate dai caratteri TAB, punto e virgola 
    o barra verticale. Per il decimale è ammesso sia il punto che la virgola. 
    Vengono automaticamente saltate le righe con caratteri non numerici. 
    
Nel tool xy2Shp_forSSAP.exe sono presenti opzioni per aggiungere una falda parallela alla superficie e impostare i parametri geotecnici per le terre. Per una back analysis speditiva in condIzioni residue può essere approssimato l'angolo d'attrito interno alla pendenza media del pendio e imposto zero alla coesione dreanata (ovvero all'angolo di riposo di materiali granulari non coesivi).

    SUGGERIMENTO: Non vi sono limitazioni alla generazione di una singola polyline a partire 
    da un elenco coordinate, pertanto  è possibile, rispettando rigidamente le specifiche SSAP,
    creare polyline dei carichi o di singoli strati (ad esempio di un muro) per poi integrarli 
    nel modello pendio in ambiemte GIS.

**CARATTERISTICHE DELLO SHAPEFILE MODELLO PENDIO**

Sono ammessi solo shapefile del tipo polyline "singol part". Nel caso venga caricato uno shapefile di geometria differente verrà generato un errore. 

    ATTENZIONE: La geometria deve rispettare rigidamente le specifiche SSAP per i file .dat 
    così come specificato nel manuale SSAP 4.7.2 al capitolo 3.3.

La struttura degli attributi dello shapefile è riportata sotto. Non è richiesto un ordine prestabilito dei campi, è invece obbligatorio l'uso dei nomi di campo e del tipo e lunghezza minima indicata. 

    ATTENZIONE: non sono ammessi valori nulli, la loro presenza genererà un errore in fase di conversione.

['SSAP_ID', 'N', 2, 0] Indice dello strato (campo richiesto)

['SSAP', 'C', 3] Tipo file SSAP. Valori ammessi dat, geo, fld, svr, sin (campo richiesto)

['PHI', 'N', 4, 2] Valore Angolo d'attrito - gradi (campo richiesto)

['C', 'N', 5, 2] Coesione efficace - kpa (campo richiesto)

['CU', 'N', 5, 2] Coesione non drenata - kpa (campo richiesto)

['GAMMA', 'N', 5, 2] Peso di volume naturale - KN/mc (campo richiesto)

['GAMMASAT', 'N', 5, 2] Peso di volume saturo - KN/mc  (campo richiesto)

['EXCLUDE', 'N', 1, 0] Campo booleano per escludere strato. Valori ammessi: 1 escludi (valore predefinito), <> 1 converti (campo richiesto)

['DR_UNDR', 'C', 1, 0] Campo scelta verifica condizioni drenate/non drenate. Valori ammessi:  D o <> U drenato (valore predefinito), U non drenato (Undrained) (campo richiesto)

['SIGCI', 'N', 5, 2] Resistenza Compressione Uniassiale Roccia Intatta  - Mpa (campo opzionale)

['GSI','N', 5, 2] Geological Strenght Index - adimensionale (campo opzionale)

['MI','N', 5, 2] Indice litologico ammasso - adimensionale (campo opzionale)

['D','N', 5, 2] Fattore di disturbo ammasso - adimensionale (campo opzionale)

['VAl1','N', 10, 2] Valore caratteristico file .svr - Kpa (campo opzionale)

Nel campo SSAP deve essere indicato a quale file ssap è riferita la polyline.

Per gli strati con campo **SSAP** = "dat" e **SSAP** = "svr" è obbligatorio un insieme di valori **SSAP_ID** crescenti dall'alto al basso e continuo da 1 a n (n = 20 per **SSAP** = "dat" e n = 10 per **SSAP** = "svr" n). Per queste polyline **non** sono ammessi valori di **SSAP_ID** = 0

Le polyline con **SSAP** = "dat" e **SSAP** = "svr" possono essere aggiunte anche intercalate a polyline dello stesso tipo già esistenti (aggiunta di strati a piacere), deve comunque essere rispettata la sequenza crescente e continua dall'alto al basso del campo **SSAP_ID**: quindi nel caso dell'inserimento di un nuovo strato tra due esistenti deve essere aggiornato il campo **SSAP_ID**. 

Per **SSAP** = "fld" (falda) è ammesso un solo strato con **SSAP_ID** = 0: questo valore identifica univocamente la falda.
Per **SSAP** = "sin" (superficie singola di verifivca) è ammesso un solo strato con **SSAP_ID** > 0

Il file .geo è generato in base ai valori dei campi dedicati (PHI, C, CU etc.), possono essere presenti contemporaneamente valori di C e Cu > 0, l'utente può scegliere se imporre condizioni drenate e non drenate valide per il singolo strato impostando D (dreained) o U (undrained) nel campo **DR_UNDR** i file per SSAP2010 verranno creati di conseguenza.

Il campo **EXCLUDE** permette di escludere singoli strati (ad esempio **SSAP** = svr, fld o sin) che non verranno considerati nella conversione nei file per SSAP2010.

    ATTENZIONE: nel caso siano escluse singole polyline **SSAP** = dat o **SSAP** = svr è necessario 
    editare e cambiare i valori del campo USER_ID per ripristinare la sequenza continua e crescente 
    1 - n dall'alto verso il basso

Se presente un valore **SIGCI** > 0 viene generato un file .geo per strati rocciosi e vengono ignorati i valori dei campi per le terre che SSAP richiede siano impostati a zero.

Sono implementate funzioni di controllo della struttura degli shapefile di input (coordinate negative, numero di strati, sequenza corretta ID strati, etc.) che interrompe la procedura e genera un avviso d'errore che esplicita la tipologia d'errore intercettata.

    ATTENZIONE: nel caso di modelli di pendio complessi, in particolare quando sono presenti lenti, 
    la procedura di controllo della sequenza verticale può generare falsi errori, nel caso deve essere esclusa.

In fase doi conversione è implementata procedura di triming degli strati che eccedono i valori di ascissa minimo e massimo dell'ascissa della superficie topografica o sono leggermente inferiori ad essa, utile per editare gli strati senza preoccuparsi della precisione dei punti di inizio e fine. E'possibile variare la tolleranza della procedura di triming editando il file default.txt.


"""
