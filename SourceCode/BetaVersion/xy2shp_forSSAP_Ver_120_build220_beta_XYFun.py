
#!/usr/bin/env pythonw

"""
xy2shp_forSSAP_095_028.py file sorgente per xy2Shp_forSSAP.exe ver 0.9.5 build 28

AUTORE: Lorenzo Sulli - lorenzo.sulli@gmail.com

INDIRIZZO DOWNLOAD: https://github.com/lsulli/shp2ssap

LICENZA: http://www.gnu.org/licenses/gpl.html

Le procedure fondamentali utilizzano il modulo shapefile.py (credit - https://github.com/GeospatialPython/pyshp)

Per il software SSAP2010 vedi termini di licenza riportati in www.SSAP.eu

Per la guida all'uso dello script vedi https://github.com/lsulli/shp2ssap

"""

# history
# 2018.04.12 - build 28 beta
#            - Modifica controllo diritti di scrittura Directory di lavoro
#            - Modifica per recupero dati da default.txt
#            - Risolto bug su estensione sahpefile di output
# 2018.04.11 - Modifica per recupero dati da default.txt
# 2018.04.04 - Gestione icona finestra
# 2018.04.03 - Versione per setup, risolto problema di scrittura file temporaneo
# 2018.03.18 - Aggiunto input da clipboard
#            - Sostituito tab con 4 punti
# 2018.03.16 - Aggiunto substrato a resistenza infinita
# 2017.11.11 - Migliorato il codice per la sostituzione dei caratteri separatori di colonna, ora ammessi (; : | - )
#            - Migliorato il codice per saltare le righe ascii di input con più di due colonne
#            - Variato il messaggio d'errore in caso di dati inutilizzabili
# 2017.05.11 - Cambiata la sequenza di costruzione dei campi tabella dello shapefile

import shapefile
import csv
import os
import tkinter.messagebox
import linecache
from tkinter.filedialog import asksaveasfilename
from tkinter import *
from tkinter import ttk
import inspect
import pyperclip
from math import atan, degrees, radians
versione = "0.9.5 build 28 beta]"
msg_title_error = "Gestione Errori"
msg_title = "xy2Shp_forSSAP"
root_title = "Crea shapefile monostrato  da XY - xy2Shp_forSSAP [ver. "
msg_clipboard = "Sorgente dati: appunti"
defpathshape = ""

# get default value from default.txt file
default_gamma = "0.0"
default_gammasat = "0.0"
default_deep_bedrock = "5.0"
default_c="0.0"
default_cu="0.0"
default_phi="0.0"
default_falda_deep="0.0"
default_phi_br=50
default_c_br=500

try:
    if os.path.exists("default.txt"):

        try:
            default_phi = linecache.getline("default.txt", 12)
            default_c = linecache.getline("default.txt", 14)
            default_cu = linecache.getline("default.txt", 16)
            default_phi = float(default_phi)
            default_c = float(default_c)
            default_cu = float(default_cu)
        except:
            default_c = "0.0"
            default_cu = "0.0"
            default_phi = "0.0"
        try:
            default_gamma = linecache.getline("default.txt", 18)
            default_gammasat = linecache.getline("default.txt", 20)
            default_gamma=float(default_gamma)
            default_gammasat=float(default_gammasat)
        except:
            default_gamma = "0.0"
            default_gammasat = "0.0"
        try:
            default_deep_falda = linecache.getline("default.txt", 22)
            default_deep_falda=float(default_deep_falda)
        except:
            default_falda_deep = "0.0"

        try:
            default_deep_bedrock = linecache.getline("default.txt", 24)
            default_deep_bedrock=float(default_deep_bedrock)
        except:
            default_deep_bedrock = "5.0"
        try:
            default_phi_br = linecache.getline("default.txt", 26)
            default_c_br = linecache.getline("default.txt", 28)
            default_phi_br = float(default_phi_br)
            default_c_br = float(default_c_br)
        except:
            default_phi_br = 50
            default_c_br = 500

except:    tkinter.messagebox.showinfo(msg_title_error, "L'assegnazione dei valori di default ha generato un errore.\n " +
                                "Controllare contenuto file default.txt \n\n"
                                "Contattare lorenzo.sulli@gmail.com")

def convert_txt2shp():
    try:
        if str_path_txt.get()==msg_clipboard:
            filedata = pyperclip.paste()
        else:
            infile = str_path_txt.get()
            f1 = open(infile, 'r')
            filedata = f1.read()
            f1.close()
        
        if os.access('.\ProfiliXY_Input', os.W_OK):
            work_tmp_file = '.\ProfiliXY_Input\out_tmp.txt'
        elif os.access (".", os.W_OK):
            work_tmp_file = 'out_tmp.txt'
        else:
            tkinter.messagebox.showerror(msg_title_error, "Il programma è stato installato in una directory con limitazioni di scrittura. \n"
                                                          + "Non posso essere creati i file temporanei di lavoro. \n"
                                                          + "Spostare la cartella di installazione in una directory con diritti di scrittura completi.")
        shapeout = str_path_shape.get()
        checkerr = 0
# replace string in input file without writing original
        f2 = open(work_tmp_file,'w')
        mydict = {':': '\t', ';': '\t', '|': '\t', ',': '.','-': '\t', '\t\t': '\t',' \t': ' '}
        for key, value in mydict.items():
            filedata = filedata.replace(key, value)
        f2.write(filedata)
        f2.close()
# end replacement

        polylinelist = []
        coordlist = []
        clonepolylinelist1 = []
        clonepolylinelist2 = []
        c = []
        mycount = 0


        with open(work_tmp_file, newline='') as inputfile:
            # opera riga per riga e nel caso di stringhe non convertibili in decimali passa a quella successiva
            # la sostituzione degli spazi per separatori di colonna si esegue riga per riga invece che per tutto il file
            for row in csv.reader(inputfile):
                try:
                    s = (row[0])
                    a = s.strip()  # elimina spazi all'inzio e alla fine della riga
            # converte separatore di colonna - spazio in TAB
                    if a.count(" ") == 1:
                        b = a.replace(" ", "\t")
                    else:
                        b = a
            # recupera gli indici del separatore di colonna,
            # ATTENZIONE: salta se è sono presenti 2 o più separatori di colonna
                    if b.count ("\t") == 1:
                        c = (b.find("\t"))  # indice della posizione stringa del primo carattere TAB
                        d = (b.rfind("\t"))  # indice della posizione stringa immediatamente a destra del carattere TAB
                        x = float(b[:c])
                        y = float(b[d:])
                        coordlist = [x,y]
                        polylinelist.append(coordlist)
                    else:
                        pass

                except:
                    pass
                mycount += 1

        if mycount > 100:
            tkinter.messagebox.showinfo(msg_title_error, "Il numero di punti che verrà generato per lo strato dat è maggiore di 100, "+
                                                          "limite previsto da SSAP. \n"
                                         + " Modificare lo shapefile che viene generato.")

        if polylinelist == [] or len(polylinelist) == 1:
            tkinter.messagebox.showerror(msg_title_error, "Si è verificato un errore, non ci sono dati utili "
                                                          "per creare uno shapefile lineare. \n"
                                                        + "Controllare la formattazione dei dati ascii di input")
            checkerr = 1
            sys.exit()
# copia profonda di polylinelist
        for n in polylinelist:
            c = n[:]
            clonepolylinelist1.append(c)


        for n in polylinelist:
            c = n[:]
            clonepolylinelist2.append(c)

        # calcola la pendenza media del versante per una stima dell'angolo di riposo del materiale
        # ovvero dell'angolo di attrito interno in condizioni residue
        try:
            cateto_opposto = abs((polylinelist[-1][-1])-(polylinelist[0][-1]))
            cateto_addiacente = abs((polylinelist[-1][0]-polylinelist[0][0]))
            tangente = cateto_opposto/cateto_addiacente
            pendenza_media = round(degrees(atan(tangente)), 1)
        except:
            pass

        if check_phi.get() == 1:
            try:
                phi_default = round(var_phi.get(),1)
            except:
                tkinter.messagebox.showinfo(msg_title_error, "Il valore impostato per l'angolo d'attrito ha generato un errore, "+
                                        "viene assegnato il valore di default 0.0.")
                var_phi.set(0.0)
                phi_default = var_phi.get()
        else:
            phi_default = 0

        if check_pendenza_media.get() == 1:
            var_phi.set(pendenza_media)
            phi_default = var_phi.get()

        if check_c.get() == 1:
            try:
                c_default = round(var_c.get(),1)
            except:
                tkinter.messagebox.showinfo(msg_title_error, "Il valore impostato per la coesione drenata ha generato un errore, "+
                                        "viene assegnato il valore di default 0.0.")
                var_c.set(0.0)
                c_default = var_c.get()
        else:
            c_default = 0

        if check_pendenza_media.get() == 1:
            var_c.set(0.0)
            c_default = var_c.get()

        if check_cu.get() == 1:
            try:
                cu_default = round(var_cu.get(),1)
            except:
                tkinter.messagebox.showinfo(msg_title_error, "Il valore impostato per la coesione non drenata ha generato un errore, "+
                                        "viene assegnato il valore di default 0.0.")
                var_cu.set(0.0)
                cu_default = var_cu.get()
        else:
            cu_default=0.0

        if check_gamma.get() == 1:
            try:
                gamma_default=round(var_gamma.get(),1)
            except:
                tkinter.messagebox.showinfo(msg_title_error, "Il valore impostato per il peso di volume naturale ha generato un errore, "+
                                        "viene assegnato il valore di default 0.0.")
                gamma_default = var_gamma.set(0.0)
        else:
            gamma_default = 0.0

        if check_gammasat.get() == 1:
            try:
                gammasat_default=round(var_gammasat.get(),1)
            except:
                tkinter.messagebox.showinfo(msg_title_error, "Il valore impostato per il peso di volume saturo ha generato un errore, "+
                                        "viene assegnato il valore di default 0.0.")
                gammasat_default = var_gammasat.set(0.0)
        else:
            gammasat_default = 0.0

    # create polyline shapefile. n.b.: per il posto alla virgola per il modulo shapefile.py è necessario impostare
    # la dimensione del campo double +1 rispetto a quanto previsto
        w = shapefile.Writer(shapefile.POLYLINE)
        w.line(parts=[polylinelist])
        w.field('SSAP', 'C', '3')
        w.field('SSAP_ID', 'N', '2', 0)
        w.field('DR_UNDR', 'C', '2')
        w.field('PHI', 'N', '6', 2)
        w.field('C', 'N', '6', 2)
        w.field('CU', 'N', '6', 2)
        w.field('GAMMA', 'N', '6', 2)
        w.field('GAMMASAT', 'N', '6', 2)
        w.field('SIGCI', 'N', '6', 2)
        w.field('GSI','N', '6', 2)
        w.field('MI','N', '6', 2)
        w.field('D','N', '6', 2)
        w.field('VAL1','N', '11', 2)
        w.field('EXCLUDE', 'N', '1', 0)
        w.record(SSAP_ID=1, SSAP='dat', DR_UNDR='D', PHI=phi_default, C=c_default, CU=cu_default, GAMMA=gamma_default, GAMMASAT=gammasat_default, SIGCI = 0,GSI=0,MI=0,
                 D=0, VAL1= 0,EXCLUDE=0)
        if check_falda.get() == 1:
            try:
                blist = []
                xsogg = float(var_falda.get())

                for n in clonepolylinelist1:

                    a = n[-1] - xsogg
                    n[-1] = a
                    blist.append(n)

                w.line(parts=[blist])
                w.record(SSAP_ID=0, SSAP='fld', DR_UNDR='0', PHI=0, C=0, CU=0, GAMMA=0, GAMMASAT=0, SIGCI = 0,GSI=0,MI=0,
                     D=0, VAL1= 0,EXCLUDE=0)
            except:
                tkinter.messagebox.showinfo(msg_title_error, "Il valore impostato per la falda ha generato un errore, "+
                                        "viene ripristinato il valore di default 0.0 .")
                var_falda.set(0.0)

        if check_bedrock.get() == 1:
            try:
                blist = []
                xsogg = float(var_bedrock.get())

                for n in clonepolylinelist2:

                    a = n[-1] - xsogg
                    n[-1] = a
                    blist.append(n)

                w.line(parts=[blist])
                w.record(SSAP_ID=2, SSAP='dat', DR_UNDR='0', PHI=default_phi_br, C=default_c_br, CU=0, GAMMA=22, GAMMASAT=22, SIGCI = 0,GSI=0,MI=0,
                     D=0, VAL1= 0,EXCLUDE=0)
            except:
                tkinter.messagebox.showinfo(msg_title_error, "Il valore impostato per il bedrock ha generato un errore, "+
                                        "viene ripristinato il valore di default 0.0 .")
                var_bedrock.set(0.0)
        w.autoBalance = 1
        try:
            w.save(shapeout)
            sf = shapefile.Reader(shapeout)
        except:
            tkinter.messagebox.showerror(msg_title_error, "Si è verificato un errore, lo shapefile creato è corrotto. \n"
                                                        + "Probabilmente i dati di input non rispettano i criteri minimi di formattazione")
            checkerr = 1
            sys.exit()


        if sf.shapes()[0].shapeType == 3 and len(sf.shapeRecords())>0:
            tkinter.messagebox.showinfo(msg_title, "Procedura conclusa è stato creato il file: \n" + shapeout + "\n")
        else:
            tkinter.messagebox.showerror(msg_title_error, "Si è verificato un errore, lo shapefile creato è corrotto. \n"
                                                        + "Lo shapefile non è lineare o è privo di features. \n"
                                                        +  "Controllare i dati di imput \n"
                                                         + + return_line_code_number()+ "\n"
                                                         + "\n\n Contattare l'autore: lorenzo.sulli@gmail.com")
            checkerr = 1
            sys.exit()

        os.remove(work_tmp_file)#elimina il file temporaneo
    except:
        if checkerr==1:
            pass
        else:
            tkinter.messagebox.showerror(msg_title_error,
                                     " Si e' verificato un errore sconosciuto. \n"
                                     + "La procedura termina \n\n Descrizione dell'errore: \n"
                                     + str(sys.exc_info()[0]) + "\n" + str(sys.exc_info()[1])+"\n"
                                     + return_line_code_number()
                                     + "\n\n Contattare l'autore: lorenzo.sulli@gmail.com")

def return_line_code_number():
        """
        Returns the current line number in this code
        """
        return "Errore riscontrato alla condizione except alla linea n.: " + str(inspect.currentframe().f_back.f_lineno) + "\t"

# ############# - tkinter/ttk code - ###################

def load_textfile():
    """
    Funzione di caricamento file di testo di input.
    Funzione richiamata dall'interfaccia tkinter
    """
    try:
        # load default path value from default.txt file
        str_path_txt.configure(state=NORMAL)
        defpathtxt = os.getcwd()+linecache.getline("default.txt", 10)
        defpathtxt = defpathtxt[:-1]  # remove /n special character
        str_path_txt.delete(0, END)# pulisco il campo di input
        if os.path.exists(defpathtxt) == False:
            defpathtxt = ""
        txt_filename = tkinter.filedialog.askopenfilename(filetypes=(("txt file", "*.txt"), ("All files", "*.*")),
                                                      initialdir=defpathtxt)
        str_path_txt.insert(10, txt_filename)
        linecache.clearcache()
    except:
        pass

def load_clipboard():
    try:
        str_path_txt.delete(0, END)# pulisco il campo di input
        str_path_txt.insert(10, msg_clipboard)
        str_path_txt.configure(state=DISABLED)
    except:
        pass


def save_shapefile():
    """
    Funzione di definzione dei file SSAP di output.
    Funzione richiamata dall'interfaccia tkinter
    """
    try:
        if os.access("default.txt", os.F_OK):
            defpathshape = os.getcwd()+linecache.getline("default.txt", 2)
            defpathshape = defpathshape[:-1]  # remove /n special character
            str_path_shape.delete(0, END)
        SHP_name = tkinter.filedialog.asksaveasfilename(filetypes=(("Shapefile", ".shp"), ("All files", "*.*")),
                                                         initialdir=defpathshape)
        # shape_text_pathname = os.path.splitext(SHP_name)[0]
        if SHP_name.split(".")[-1]=="shp":
            str_path_shape.insert(10, SHP_name)
        else:
            str_path_shape.insert(10, SHP_name+".shp")
        linecache.clearcache()
    except:
        pass


def active_disable_button(*args):
    """
    active or disable button 'Converti' by input and output entry
    """
    x = var_str_input.get()
    y = var_str_output.get()
    if os.path.exists(x) or x == msg_clipboard:
        if os.path.isdir(os.path.dirname(y)) and os.path.basename(y):
            Conv_Button.configure(state='normal')
    else:
        Conv_Button.configure(state='disabled')


def active_disable_str_cu (*args):
    try:
        if check_cu.get() == 0:
            str_cu.configure(state = DISABLED)
        else:
            str_cu.configure(state = NORMAL)
    except:
        pass

def active_disable_str_c (*args):
    try:
        if check_c.get() == 0:
            str_c.configure(state = DISABLED)
        else:
            str_c.configure(state = NORMAL)
    except:
        pass

def active_disable_str_phi (*args):
    try:
        if check_phi.get() == 0:
            str_phi.configure(state = DISABLED)
        else:
            str_phi.configure(state = NORMAL)
    except:
        pass

def active_disable_str_gamma (*args):
    try:
        if check_gamma.get() == 0:
            str_gamma.configure(state = DISABLED)
        else:
            str_gamma.configure(state = NORMAL)
    except:
        pass

def active_disable_str_gammasat (*args):
    try:
        if check_gammasat.get() == 0:
            str_gammasat.configure(state = DISABLED)
        else:
            str_gammasat.configure(state = NORMAL)
    except:
        pass

def active_disable_str_falda (*args):
    try:
        if check_falda.get() == 0:
            str_falda.configure(state = DISABLED)
        else:
            str_falda.configure(state = NORMAL)
    except:
        pass

def active_disable_str_bedrock (*args):
    try:
        if check_bedrock.get() == 0:
            str_bedrock.configure(state = DISABLED)
        else:
            str_bedrock.configure(state = NORMAL)
    except:
        pass


def active_disable_chkb_backanalysis (*args):
    try:
        if check_pendenza_media.get() == 1:
            c1.deselect()
            c1.configure(state = DISABLED)
            str_phi.configure(state = DISABLED)
            c2.deselect()
            c2.configure(state = DISABLED)
            str_c.configure(state = DISABLED)
        else:
            c1.configure(state = NORMAL)
            c2.configure(state = NORMAL)
    except:
        pass

