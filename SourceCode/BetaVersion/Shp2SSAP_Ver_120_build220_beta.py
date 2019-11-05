import sys
#sys.path.insert(0, '../moduli_py')
import os
import linecache
import Shp2SSAP_Ver_120_build220_beta_MainFun as FuncMain
import tkinter.filedialog
from tkinter import *
from tkinter import ttk
import s2s_lbl_ver120_build220 as s2s_lbl
########################################################################
class Shp2SSAP_GUI(object):
    """"""
 
    #----------------------------------------------------------------------
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

        # BUTTONS
        self.XY_Button = Button(self.frame, text='Crea Shape da XY', command=FuncMain.open_form)
        self.XY_Button.grid(row=1, column=0, sticky=(W, E), pady=4, padx=8)
        self.In_Button = Button(self.frame, text='Input Shapefile', command= self.load_shapefile)
        self.In_Button.grid(row=2, column=0, sticky=(W, E), pady=4, padx=8)
        self.Out_Button = Button(self.frame, text='Output SSAP files', command= self.save_files_ssap)
        self.Out_Button.grid(row=3, column=0, sticky=(W, E), pady=4, padx=8)
        self.Exit_Button = Button(self.frame, text='Esci', command=self.frame.quit)
        self.Exit_Button.grid(row=8, column=1, sticky=E, pady=4)
        self.Ver_Button = Button(self.frame, text='Verifica preliminare Shape', command=lambda: FuncMain.check_function(1, self.str_path_shape))
        self.Ver_Button.grid(row=8, column=0, sticky=W, pady=4)
        self.Conv_Button = Button(self.frame, text='Converti', command=lambda: FuncMain.shp_2_ssap_files(self.str_path_shape, self.str_path_ssap))
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

        # checkbutton
        check_cu = IntVar()
        CheckTopBottomOrder = IntVar()
        c1 = Checkbutton(self.frame, text="Verifica ordinamento verticale strati", variable=CheckTopBottomOrder,
                         onvalue=1, offvalue=0, height=1, width=35, anchor=W)
        c1.grid(row=5, column=0, sticky=W)
        c1.select()
        check_trimming = IntVar()
        c2 = Checkbutton(self.frame, text="Regola gli strati alla superficie topografica", variable=check_trimming,
                         onvalue=1, offvalue=0, height=1, width=35, anchor=E)
        c2.grid(row=5, column=1, sticky=W)
        c2.select()
        check_smp_polyline = IntVar()
        c3 = Checkbutton(self.frame, text="Semplifica polyline se > 100 punti", variable=check_smp_polyline,
                         onvalue=1, offvalue=0, height=1, width=35, anchor=W)
        c3.grid(row=6, column=0, sticky=W)
        c3.select()

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
        self.SSAP_name = tkinter.filedialog.asksaveasfilename(filetypes=(("SSAP FILES", "*.mod*"), ("All files", "*.*")),
                                                         initialdir=self.defpathssap)
        self.ssap_text_pathname = os.path.splitext(self.SSAP_name)[0]
        self.str_path_ssap.insert(10, self.ssap_text_pathname)
        linecache.clearcache()


    def active_disable_button(self,*args):
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

    #----------------------------------------------------------------------
    def openFrame(self):
        """"""
        otherFrame = Toplevel()
        otherFrame.geometry("400x300")
        otherFrame.title("otherFrame")
        handler = lambda: self.onCloseOtherFrame(otherFrame)
        btn = Button(otherFrame, text="Close", command=handler)
        btn.pack()
 
    #----------------------------------------------------------------------
    def onCloseOtherFrame(self, otherFrame):
        """"""
        otherFrame.destroy()
        #self.show()
 
    #----------------------------------------------------------------------
    def show(self):
        """"""
        self.root.update()
        self.root.deiconify()
 
 
#----------------------------------------------------------------------
if __name__ == "__main__":
    root = Tk()
    app = Shp2SSAP_GUI(root)
    root.mainloop()
