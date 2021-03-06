
#!/usr/bin/env pythonw

"""
xy2shp_forSSAP_095_025.py file sorgente per xy2Shp_forSSAP.exe ver 0.9.5 build 25

AUTORE: Lorenzo Sulli - lorenzo.sulli@gmail.com

INDIRIZZO DOWNLOAD: https://github.com/lsulli/shp2ssap

LICENZA: http://www.gnu.org/licenses/gpl.html

Le procedure fondamentali utilizzano il modulo shapefile.py (credit - https://github.com/GeospatialPython/pyshp)

Per il software SSAP2010 vedi termini di licenza riportati in www.SSAP.eu

Per la guida all'uso dello script vedi https://github.com/lsulli/shp2ssap

"""

# history
# 2018.04.03 - Versione per setup
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
versione = "0.9.5 build 25]"
msg_title_error = "Gestione Errori"
msg_title = "xy2Shp_forSSAP"
root_title = "Crea shapefile monostrato  da XY - xy2Shp_forSSAP [ver. "
msg_clipboard = "Sorgente dati: appunti"

def convert_txt2shp():
    try:
        if str_path_txt.get()==msg_clipboard:
            filedata = pyperclip.paste()
        else:
            infile = str_path_txt.get()
            f1 = open(infile, 'r')
            filedata = f1.read()
            f1.close()
        
        if os.path.exists('.\ProfiliXY_Input'):
            work_tmp_file = '.\ProfiliXY_Input\out_tmp.txt'
        else:
            work_tmp_file = 'out_tmp.txt'
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
                w.record(SSAP_ID=2, SSAP='dat', DR_UNDR='0', PHI=45, C=250, CU=0, GAMMA=22, GAMMASAT=22, SIGCI = 0,GSI=0,MI=0,
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
        defpathshape = os.getcwd()+linecache.getline("default.txt", 2)
        defpathshape = defpathshape[:-1]  # remove /n special character
        str_path_shape.delete(0, END)
        if not os.path.exists(defpathshape):
            defpathshape = ""
        SHP_name = tkinter.filedialog.asksaveasfilename(filetypes=(("Shapefile", ".shp"), ("All files", "*.*")),
                                                         initialdir=defpathshape)
        # shape_text_pathname = os.path.splitext(SHP_name)[0]
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

# tkinter code

try:
    root = tkinter.Tk()
    root.title(root_title + versione)
    root.resizable(FALSE,FALSE)    
    if os.path.exists('C:\\SSAP2010\\PythonSSAP\\Shp2SSAP_exe\\xy2Shp_forSSAP_CreateEXE\\xy2Shp_forSSAP.ico'):
            root.iconbitmap('C:\SSAP2010\\PythonSSAP\\Shp2SSAP_exe\\xy2Shp_forSSAP_CreateEXE\\xy2Shp_forSSAP.ico')
    master = ttk.Frame(root, padding="12 12 12 12")
    master.grid(column=0, row=0, sticky=(N, W, E, S))
    master.columnconfigure(0, weight=1)
    master.rowconfigure(0, weight=1)
    master['borderwidth'] = 2
    master['relief'] = 'sunken'
    # variable for trace method
    Button(master, text='Input file di testo', command=load_textfile).grid(row=0, column=0, sticky=(W), pady=4, padx=8)
    Button(master, text='Input appunti', command=load_clipboard).grid(row=0, column=0, sticky=(E), pady=4, padx=8)
    var_str_input = tkinter.StringVar(root)
    str_path_txt = tkinter.Entry(master, width=70,textvariable=var_str_input)
    Button(master, text='Output Shapefile per SSAP', command=save_shapefile).grid(row=1, column=0, sticky=(W, E), pady=4, padx=8)
    var_str_output = tkinter.StringVar(root)
    str_path_shape = tkinter.Entry(master, width=70, textvariable=var_str_output)
    str_path_txt.grid(row=0, column=1, sticky=(E,W),columnspan=1)
    str_path_shape.grid(row=1, column=1, sticky=(E,W),columnspan=1)
    Conv_Button = Button(master, text='Converti', command=convert_txt2shp)
    Conv_Button.grid(row=14, column=0, sticky=W, pady=4)
    Conv_Button.configure(state=DISABLED)
    Button(master, text='Esci', command=master.quit).grid(row=14, column=1, sticky=E, pady=4)
    var_str_input.trace("w", active_disable_button)
    var_str_output.trace("w", active_disable_button)

    #separator
    s1_0 = ttk.Separator(master, orient=HORIZONTAL).grid(column=1, row=3, sticky=(E, W), pady=10, columnspan=2)
    s2_0 = ttk.Separator(master, orient=HORIZONTAL).grid(column=0, row=9, sticky=(E, W), pady=10, columnspan=3)
    s3_0 = ttk.Separator(master, orient=HORIZONTAL).grid(column=0, row=13, sticky=(E, W), pady=10, columnspan=3)

    #label
    l1 = ttk.Label(master, text='                  Assegna valori a strato', borderwidth=5, relief=GROOVE,
                   foreground='black')
    l1.grid(column=0, row=3, pady=10, ipadx=5, ipady=3,sticky = (W,E))

    #checkbutton
    width_cb=30
    check_phi = IntVar()
    c1 = Checkbutton(master, text = "Angolo d'attrito", variable = check_phi, onvalue = 1,
                             offvalue = 0, height=1, width = width_cb, anchor=W)
    c1.grid(row=4, column=0, sticky=W)
    c1.deselect()

    var_phi = tkinter.DoubleVar(root)
    str_phi = tkinter.Entry(master, width=5, textvariable=var_phi, state = DISABLED)
    str_phi.grid(row=4, column=0, sticky=E)
    var_phi.set(0.0)

    check_phi.trace("w", active_disable_str_phi)

    check_c = IntVar()
    c2 = Checkbutton(master, text = "Coesione drenata (Kpa)", variable = check_c, onvalue = 1,
                             offvalue = 0, height=1, width = width_cb, anchor=W)
    c2.grid(row=5, column=0, sticky=W)
    c2.deselect()

    var_c = tkinter.DoubleVar(root)
    str_c = tkinter.Entry(master, width=5, textvariable=var_c, state = DISABLED)
    str_c.grid(row=5, column=0, sticky=E)
    var_c.set(0.0)

    check_c.trace("w", active_disable_str_c)

    check_cu = IntVar()
    c3 = Checkbutton(master, text = "Coesione non drenata (Kpa)", variable = check_cu, onvalue = 1,
                             offvalue = 0, height=1, width = width_cb, anchor=W)
    c3.grid(row=6, column=0, sticky=W)
    c3.deselect()

    var_cu = tkinter.DoubleVar(root)
    str_cu = tkinter.Entry(master, width=5, textvariable=var_cu, state = DISABLED)
    str_cu.grid(row=6, column=0, sticky=E)
    var_cu.set(0.0)

    check_cu.trace("w", active_disable_str_cu)

    check_gamma = IntVar()
    c4 = Checkbutton(master, text = "Peso di volume naturale (KN/mc):", variable = check_gamma, onvalue = 1,
                             offvalue = 0, height=1, width=width_cb,anchor=W)
    c4.grid(row=4, column=1, sticky=W, padx=50)
    c4.deselect()

    var_gamma = tkinter.DoubleVar(root)
    str_gamma = tkinter.Entry(master, width=5, textvariable=var_gamma, state = DISABLED)
    str_gamma.grid(row=4, column=1, sticky=E)
    var_gamma.set(0.0)

    check_gamma.trace("w", active_disable_str_gamma)

    check_gammasat = IntVar()
    c5 = Checkbutton(master, text = "Peso di volume saturo (KN/mc):", variable = check_gammasat, onvalue = 1,
                             offvalue = 0, height=1, width=width_cb,anchor=W)
    c5.grid(row=5, column=1, sticky=(W,E), padx=50)
    c5.deselect()

    var_gammasat = tkinter.DoubleVar(root)
    str_gammasat = tkinter.Entry(master, width=5, textvariable=var_gammasat, state = DISABLED)
    str_gammasat.grid(row=5, column=1, sticky=E)
    var_gammasat.set(0.0)

    check_gammasat.trace("w", active_disable_str_gammasat)

    check_falda = IntVar()
    c6 = Checkbutton(master, text = "Superficie si saturazione parallela alla topografia a profondità di metri:", variable = check_falda, onvalue = 1,
                             offvalue = 0, height=1, width=60,anchor=W)
    c6.grid(row=10, column=0, sticky=W, columnspan=2)
    c6.deselect()

    var_falda = tkinter.DoubleVar(root)
    str_falda = tkinter.Entry(master, width=5, textvariable=var_falda, state = DISABLED)
    str_falda.grid(row=10, column=1, sticky=E)
    var_falda.set(0.0)

    check_falda.trace("w", active_disable_str_falda)

    check_pendenza_media = IntVar()
    c7 = Checkbutton(master, text = "Angolo d'attrito = pendenza media pendio e coesione = 0 kpa (back analysis condizioni residue)", variable=check_pendenza_media, onvalue = 1,
                             offvalue = 0, height=1, width=80,anchor=W)
    c7.grid(row=11, column=0, sticky=W, columnspan=2)
    c7.deselect()

    check_pendenza_media.trace("w", active_disable_chkb_backanalysis)
    check_phi.trace("w", active_disable_chkb_backanalysis)
    check_c.trace("w", active_disable_chkb_backanalysis)

    check_bedrock = IntVar()
    c8 = Checkbutton(master, text = "Substrato con resistenza infinita parallelo alla topografia  a profondità di metri:", variable = check_bedrock, onvalue = 1,
                             offvalue = 0, height=1, width=60,anchor=W)
    c8.grid(row=12, column=0, sticky=W, columnspan=2)
    c8.deselect()

    var_bedrock = tkinter.DoubleVar(root)
    str_bedrock = tkinter.Entry(master, width=5, textvariable=var_bedrock, state = DISABLED)
    str_bedrock.grid(row=12, column=1, sticky=E)
    var_bedrock.set(0.0)

    check_bedrock.trace("w", active_disable_str_bedrock)

    root.mainloop()
except:
    pass
