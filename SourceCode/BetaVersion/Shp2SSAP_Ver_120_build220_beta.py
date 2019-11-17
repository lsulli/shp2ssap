# Prima versione con Classe dedicata all'interfaccia e richiamo delle funzioni da modulo esterno

import sys

sys.path.insert(0, '../moduli_py')
import os
import linecache
import Shp2SSAP_Ver_120_build220_beta_MainFun as FuncMain
import xy2shp_forSSAP_Ver_120_build220_beta_XYFun as FuncXY
import tkinter.filedialog
from tkinter import *
from tkinter import ttk
import s2s_lbl_ver120_build220 as s2s_lbl


########################################################################
class Shp2SSAP_GUI(object):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        self.root = parent
        self.root.title(s2s_lbl.root_title)
        self.root.resizable(False, False)
        self.frame = ttk.Frame(parent, padding="12 12 12 12")
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame['borderwidth'] = 2
        self.frame['relief'] = 'sunken'

        # Input box
        self.var1 = StringVar(self.root)
        self.var2 = StringVar(self.root)
        self.str_path_shape = Entry(self.frame, width=75, textvariable=self.var1)
        self.str_path_ssap = Entry(self.frame, width=75, textvariable=self.var2)
        self.str_path_shape.grid(row=2, column=1, sticky=(E, W))
        self.str_path_ssap.grid(row=3, column=1, sticky=(E, W))
        self.var1.trace("w", self.active_disable_button)
        self.var2.trace("w", self.active_disable_button)

        # checkbutton
        self.check_cu = IntVar()
        self.check_top_bottom_order = IntVar()
        self.c1 = Checkbutton(self.frame, text="Verifica ordinamento verticale strati",
                              variable=self.check_top_bottom_order,
                              onvalue=1, offvalue=0, height=1, width=35, anchor=W)
        self.c1.grid(row=5, column=0, sticky=W)
        self.c1.select()
        self.check_trimming = IntVar()
        self.c2 = Checkbutton(self.frame, text="Regola gli strati alla superficie topografica",
                              variable=self.check_trimming,
                              onvalue=1, offvalue=0, height=1, width=35, anchor=E)
        self.c2.grid(row=5, column=1, sticky=W)
        self.c2.select()
        self.check_smp_polyline = IntVar()
        self.c3 = Checkbutton(self.frame, text="Semplifica polyline se > 100 punti", variable=self.check_smp_polyline,
                              onvalue=1, offvalue=0, height=1, width=35, anchor=W)
        self.c3.grid(row=6, column=0, sticky=W)
        self.c3.select()

        # BUTTONS
        self.XY_Button = Button(self.frame, text='Crea Shape da XY', command=self.openSubForm)
        self.XY_Button.grid(row=1, column=0, sticky=(W, E), pady=4, padx=8)
        self.In_Button = Button(self.frame, text='Input Shapefile', command=self.load_shapefile)
        self.In_Button.grid(row=2, column=0, sticky=(W, E), pady=4, padx=8)
        self.Out_Button = Button(self.frame, text='Output SSAP files', command=self.save_files_ssap)
        self.Out_Button.grid(row=3, column=0, sticky=(W, E), pady=4, padx=8)
        self.Exit_Button = Button(self.frame, text='Esci', command=self.frame.quit)
        self.Exit_Button.grid(row=8, column=1, sticky=E, pady=4)
        self.Ver_Button = Button(self.frame, text='Verifica preliminare Shape', command=lambda:
        FuncMain.check_function(1, self.str_path_shape, self.check_top_bottom_order.get(),
                                self.check_smp_polyline.get()))
        self.Ver_Button.grid(row=8, column=0, sticky=W, pady=4)
        self.Conv_Button = Button(self.frame, text='Converti', command=lambda:
        FuncMain.shp_2_ssap_files(self.str_path_shape, self.str_path_ssap, self.check_top_bottom_order.get(),
                                  self.check_trimming.get(), self.check_smp_polyline.get()))
        self.Conv_Button.grid(row=8, column=0, sticky=E, pady=4)
        self.Conv_Button.configure(state=DISABLED)
        self.Ver_Button.configure(state=DISABLED)

        # Separator
        s1 = ttk.Separator(self.frame, orient=HORIZONTAL).grid(column=1, row=1, sticky=(E, W), pady=6)
        s2 = ttk.Separator(self.frame, orient=HORIZONTAL).grid(column=1, row=4, sticky=(E, W), pady=6)
        s3 = ttk.Separator(self.frame, orient=HORIZONTAL).grid(column=0, row=7, sticky=(E, W), pady=10, columnspan=3)

        # label
        l1 = ttk.Label(self.frame, text='  Opzioni controllo e creazioni strati', borderwidth=5, relief=GROOVE,
                       foreground='black')
        l1.grid(column=0, row=4, pady=10, ipadx=10, ipady=3, sticky=(E, W))

    def load_shapefile(self):
        """
        Funzione di caricamento degli sahpefile di input.
        Funzione richiamata dall'interfaccia tkinter
        """
        # load default path value from default.txt file
        self.defpathshp = os.getcwd() + linecache.getline("default.txt", 2)
        self.defpathshp = self.defpathshp[:-1]  # remove /n special character
        self.str_path_shape.delete(0, END)
        if os.path.exists(self.defpathshp) == False:
            self.defpathshp = ""
        self.shp_name = tkinter.filedialog.askopenfilename(filetypes=(("Shapefile", "*.shp"), ("All files", "*.*")),
                                                           initialdir=self.defpathshp)
        self.str_path_shape.insert(10, self.shp_name)
        linecache.clearcache()

    def save_files_ssap(self):
        """
        Funzione di definzione dei file SSAP di output.
        Funzione richiamata dall'interfaccia tkinter
        """
        self.defpathssap = os.getcwd() + linecache.getline("default.txt", 4)
        self.defpathssap = self.defpathssap[:-1]  # remove /n special character
        self.str_path_ssap.delete(0, END)
        if not os.path.exists(self.defpathssap):
            self.defpathssap = ""
        self.SSAP_name = tkinter.filedialog.asksaveasfilename(
            filetypes=(("SSAP FILES", "*.mod*"), ("All files", "*.*")),
            initialdir=self.defpathssap)
        self.ssap_text_pathname = os.path.splitext(self.SSAP_name)[0]
        self.str_path_ssap.insert(10, self.ssap_text_pathname)
        linecache.clearcache()

    def active_disable_button(self, *args):
        """
        active or disable button 'Converti' and 'Verifica' by input and output entry
        """
        x = self.var1.get()
        y = self.var2.get()
        if os.path.exists(x):
            self.Ver_Button.configure(state='normal')
        else:
            self.Conv_Button.configure(state='disabled')
            self.Ver_Button.configure(state='disabled')
        if os.path.isdir(os.path.dirname(y)) and os.path.basename(y) and os.path.exists(x):
            self.Conv_Button.configure(state='normal')
        else:
            self.Conv_Button.configure(state='disabled')

    # ----------------------------------------------------------------------
    def openSubForm(self):
        """"""
        SubForm = Toplevel()
        SubForm.resizable(FALSE,FALSE)
        SubForm.title(s2s_lbl.subform_title + s2s_lbl.subform_ver)

        if os.path.exists('.\\Icon\\xy2Shp_forSSAP.ico'):
            root.iconbitmap('.\\Icon\\xy2Shp_forSSAP.ico')
        elif os.path.exists('xy2Shp_forSSAP.ico'):
            root.iconbitmap('xy2Shp_forSSAP.ico')
        else:
            pass
        self.frame = ttk.Frame(SubForm, padding="12 12 12 12")
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame['borderwidth'] = 2
        self.frame['relief'] = 'sunken'
        Button(self.frame, text='Input file di testo', command=FuncXY.load_textfile).grid(row=0, column=0, sticky=(W), pady=4,
                                                                               padx=8)
        Button(self.frame, text='Input appunti', command=FuncXY.load_clipboard).grid(row=0, column=0, sticky=(E), pady=4, padx=8)
        var_str_input = tkinter.StringVar(SubForm)
        str_path_txt = tkinter.Entry(self.frame, width=70, textvariable=var_str_input)
        Button(self.frame, text='Output Shapefile per SSAP', command=FuncXY.save_shapefile).grid(row=1, column=0, sticky=(W, E),
                                                                                      pady=4, padx=8)
        var_str_output = tkinter.StringVar(SubForm)
        str_path_shape = tkinter.Entry(self.frame, width=70, textvariable=var_str_output)
        str_path_txt.grid(row=0, column=1, sticky=(E, W), columnspan=1)
        str_path_shape.grid(row=1, column=1, sticky=(E, W), columnspan=1)
        Conv_Button = Button(self.frame, text='Converti', command=FuncXY.convert_txt2shp)
        Conv_Button.grid(row=14, column=0, sticky=W, pady=4)
        Conv_Button.configure(state=DISABLED)
        Button(self.frame, text='Esci', command=self.frame.quit).grid(row=14, column=1, sticky=E, pady=4)
        #var_str_input.trace("w", active_disable_button)
        #var_str_output.trace("w", active_disable_button)

        # separator
        s1_0 = ttk.Separator(self.frame, orient=HORIZONTAL).grid(column=1, row=3, sticky=(E, W), pady=10, columnspan=2)
        s2_0 = ttk.Separator(self.frame, orient=HORIZONTAL).grid(column=0, row=9, sticky=(E, W), pady=10, columnspan=3)
        s3_0 = ttk.Separator(self.frame, orient=HORIZONTAL).grid(column=0, row=13, sticky=(E, W), pady=10, columnspan=3)

        # label
        l1 = ttk.Label(self.frame, text='                  Assegna valori a strato', borderwidth=5, relief=GROOVE,
                       foreground='black')
        l1.grid(column=0, row=3, pady=10, ipadx=5, ipady=3, sticky=(W, E))

        # checkbutton
        width_cb = 30
        check_phi = IntVar()
        c1 = Checkbutton(self.frame, text="Angolo d'attrito", variable=check_phi, onvalue=1,
                         offvalue=0, height=1, width=width_cb, anchor=W)
        c1.grid(row=4, column=0, sticky=W)
        c1.deselect()

        var_phi = tkinter.DoubleVar(SubForm)
        str_phi = tkinter.Entry(self.frame, width=5, textvariable=var_phi, state=DISABLED)
        str_phi.grid(row=4, column=0, sticky=E)
        #var_phi.set(default_phi)

        #check_phi.trace("w", active_disable_str_phi)

        check_c = IntVar()
        c2 = Checkbutton(self.frame, text="Coesione drenata (Kpa)", variable=check_c, onvalue=1,
                         offvalue=0, height=1, width=width_cb, anchor=W)
        c2.grid(row=5, column=0, sticky=W)
        c2.deselect()

        var_c = tkinter.DoubleVar(SubForm)
        str_c = tkinter.Entry(self.frame, width=5, textvariable=var_c, state=DISABLED)
        str_c.grid(row=5, column=0, sticky=E)
        #var_c.set(default_c)

        #check_c.trace("w", active_disable_str_c)

        check_cu = IntVar()
        c3 = Checkbutton(self.frame, text="Coesione non drenata (Kpa)", variable=check_cu, onvalue=1,
                         offvalue=0, height=1, width=width_cb, anchor=W)
        c3.grid(row=6, column=0, sticky=W)
        c3.deselect()

        var_cu = tkinter.DoubleVar(SubForm)
        str_cu = tkinter.Entry(self.frame, width=5, textvariable=var_cu, state=DISABLED)
        str_cu.grid(row=6, column=0, sticky=E)
        #var_cu.set(default_cu)

        #check_cu.trace("w", active_disable_str_cu)

        check_gamma = IntVar()
        c4 = Checkbutton(self.frame, text="Peso di volume naturale (KN/mc):", variable=check_gamma, onvalue=1,
                         offvalue=0, height=1, width=width_cb, anchor=W)
        c4.grid(row=4, column=1, sticky=W, padx=50)
        c4.deselect()

        var_gamma = tkinter.DoubleVar(SubForm)
        str_gamma = tkinter.Entry(self.frame, width=5, textvariable=var_gamma, state=DISABLED)
        str_gamma.grid(row=4, column=1, sticky=E)
        #var_gamma.set(default_gamma)

        #check_gamma.trace("w", active_disable_str_gamma)

        check_gammasat = IntVar()
        c5 = Checkbutton(self.frame, text="Peso di volume saturo (KN/mc):", variable=check_gammasat, onvalue=1,
                         offvalue=0, height=1, width=width_cb, anchor=W)
        c5.grid(row=5, column=1, sticky=(W, E), padx=50)
        c5.deselect()

        var_gammasat = tkinter.DoubleVar(SubForm)
        str_gammasat = tkinter.Entry(self.frame, width=5, textvariable=var_gammasat, state=DISABLED)
        str_gammasat.grid(row=5, column=1, sticky=E)
        #var_gammasat.set(default_gammasat)

        #check_gammasat.trace("w", active_disable_str_gammasat)

        check_falda = IntVar()
        c6 = Checkbutton(self.frame, text="Superficie di saturazione parallela alla topografia a profondità di metri:",
                         variable=check_falda, onvalue=1,
                         offvalue=0, height=1, width=60, anchor=W)
        c6.grid(row=10, column=0, sticky=W, columnspan=2)
        c6.deselect()

        var_falda = tkinter.DoubleVar(SubForm)
        str_falda = tkinter.Entry(self.frame, width=5, textvariable=var_falda, state=DISABLED)
        str_falda.grid(row=10, column=1, sticky=E)
        #var_falda.set(default_falda_deep)

        #check_falda.trace("w", active_disable_str_falda)

        check_pendenza_media = IntVar()
        c7 = Checkbutton(self.frame,
                         text="Angolo d'attrito = pendenza media pendio e coesione = 0 kpa (back analysis condizioni residue)",
                         variable=check_pendenza_media, onvalue=1,
                         offvalue=0, height=1, width=80, anchor=W)
        c7.grid(row=11, column=0, sticky=W, columnspan=2)
        c7.deselect()

        #check_pendenza_media.trace("w", active_disable_chkb_backanalysis)
        #check_phi.trace("w", active_disable_chkb_backanalysis)
        #check_c.trace("w", active_disable_chkb_backanalysis)

        check_bedrock = IntVar()
        c8 = Checkbutton(self.frame,
                         text="Substrato con resistenza infinita parallelo alla topografia  a profondità di metri:",
                         variable=check_bedrock, onvalue=1,
                         offvalue=0, height=1, width=60, anchor=W)
        c8.grid(row=12, column=0, sticky=W, columnspan=2)
        c8.deselect()

        var_bedrock = tkinter.DoubleVar(SubForm)
        str_bedrock = tkinter.Entry(self.frame, width=5, textvariable=var_bedrock, state=DISABLED)
        str_bedrock.grid(row=12, column=1, sticky=E)
        #var_bedrock.set(default_deep_bedrock)

        #check_bedrock.trace("w", active_disable_str_bedrock)

    # ----------------------------------------------------------------------
    def onCloseOtherFrame(self, otherFrame):
        """"""
        otherFrame.destroy()
        # self.show()

    # ----------------------------------------------------------------------
    def show(self):
        """"""
        self.root.update()
        self.root.deiconify()


# ----------------------------------------------------------------------
if __name__ == "__main__":
    root = Tk()
    app = Shp2SSAP_GUI(root)

    root.mainloop()
