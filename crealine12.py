
import shapefile
import csv
import os
import tkinter.messagebox
import linecache
from tkinter.filedialog import asksaveasfilename
from tkinter import *
from tkinter import ttk
import inspect
from math import atan, degrees, radians
versione = "0.8.12"
msg_title_error = "Gestione Errori"
msg_title = "Crea shapefile per SSAP da elenco xy"

def convert_txt2shp():

	try:

		infile = str_path_txt.get()
		work_tmp_file = 'out_tmp.txt'
		shapeout = str_path_shape.get()
		checkerr = 0

		f = open(infile,'r')
		filedata = f.read()
		f.close()

		newdata = filedata.replace(",", ".")# converte separatore decimale per tutto il file
		# A causa di possibili casi non risolvibili in presenza di decimali con la virgola
		# non è ammessa la virgola come separatore di colonna
		newdata2 = newdata.replace(";", "\t")# converte separatore di colonne per tutto il file - punto e virgola
		newdata3 = newdata2.replace ("|", "\t")#converte separatore di colonna per tutto il file - barra verticale
		f = open(work_tmp_file,'w')
		f.write(newdata3)
		f.close()

		polylinelist = []
		coordlist = []
		clonepolylinelist = []
		c = []

		with open(work_tmp_file, newline='') as inputfile:
			#opera riga per riga e nel caso di stringhe non convertibili in decimali passa a quella successiva
			#la sostituzione degli spazi per separatori di colonna si esegue riga per riga invece che per tutto il file

			for row in csv.reader(inputfile):
				try:
					s = (row[0])
					a = s.strip()# elimina spazi all'inzio e alla fine della riga
					# converte separatore di colonna - spazio
					if a.count(" ") == 1:
						b = a.replace(" ", "\t")
					else:
						b = a
					c = (b.find("\t"))
					d = (b.rfind("\t"))
					x = float(b[:c])
					y = float(b[d:])
					coordlist = [x,y]
					polylinelist.append(coordlist)
				except:
					pass
		if polylinelist == [] or len(polylinelist) == 1:
			tkinter.messagebox.showerror(msg_title_error, "Si è verificato un errore, non ci sono dati utili "
														  "per creare uno shapefile lineare. \n"
														+ "Probabilmente il file non riporta elenchi di coordinate")
			checkerr = 1
			sys.exit()
# copia profonda di polylinelist
		for n in polylinelist:
			c = n[:]
			clonepolylinelist.append(c)
		# calcola la pendenza media del versante per una stima dell'angolo di riposo del materiale
		# ovvero dell'angolo di attrito interno in condizioni residue


		cateto_opposto=abs((clonepolylinelist[-1][-1])-(clonepolylinelist[0][-1]))
		cateto_addiacente=abs((clonepolylinelist[-1][0]-clonepolylinelist[0][0]))
		tangente = cateto_opposto/cateto_addiacente
		print (tangente)
		if check_pendenza_media.get() == 1:
			pendenza_media = round(degrees(atan(tangente)), 2)
		else:
			pendenza_media = 0

		if check_gamma.get() == 1:
			gamma_default = round(var4.get(),1)
		else:
			gamma_default = 0.0

	#create polyline shapefile
		w = shapefile.Writer(shapefile.POLYLINE)
		print (86, clonepolylinelist)
		w.line(parts=[polylinelist])
		w.field('SSAP_ID', 'N', '2', 0)
		w.field('SSAP', 'C', '3')
		w.field('DR_UNDR', 'C', '1')
		w.field('PHI', 'N', '5', 2)
		w.field('C', 'N', '5', 2)
		w.field('CU', 'N', '5', 2)
		w.field('GAMMA', 'N', '5', 2)
		w.field('GAMMASAT', 'N', 5, 2)
		w.field('SIGCI', 'N', '5', 2)
		w.field('GSI','N', '5', 2)
		w.field('MI','N', '5', 2)
		w.field('D','N', '5', 2)
		w.field('VAL1','N', '5', 2)
		w.field('EXCLUDE', 'N', '1')
		w.record(SSAP_ID=1, SSAP='dat', DR_UNDR='D', PHI=pendenza_media, C=0, CU=0, GAMMA=gamma_default, GAMMASAT=gamma_default, SIGCI = 0,GSI=0,MI=0,
				 D=0, VAL1= 0,EXCLUDE=0)
		print (104, clonepolylinelist)
		if check_falda.get() == 1:
			blist = []
			xsogg = float(var3.get())

			for n in clonepolylinelist:

				a = n[-1] - xsogg
				n[-1] = a
				blist.append(n)

			print (116, blist)
			w.line(parts=[blist])
			w.record(SSAP_ID=0, SSAP='fld', DR_UNDR='0', PHI=0, C=0, CU=0, GAMMA=0, GAMMASAT=0, SIGCI = 0,GSI=0,MI=0,
				 D=0, VAL1= 0,EXCLUDE=0)
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
			tkinter.messagebox.showinfo(msg_title, "Procedura conclusa senza errori è stato creato il file: \n" + shapeout + "\n")
		else:
			tkinter.messagebox.showerror(msg_title_error, "Si è verificato un errore, lo shapefile creato è corrotto. \n"
														+ "Lo shapefile non è lineare o è privo di features. \n"
														+  "Controllare i dati di imput \n"
										 				+ + return_line_code_number()+ "\n"
									 					+ "\n\n Contattare l'autore: lorenzo.sulli@gmail.com")
			checkerr = 1
			sys.exit()

		#os.remove (work_tmp_file)#elimina il file temporaneo
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
	Funzione di caricamento degli sahpefile di input.
	Funzione richiamata dall'interfaccia tkinter
	"""
	try:
		# load default path value from default.txt file
		defpathtxt = os.getcwd()+linecache.getline("default.txt", 2)
		print (defpathtxt)
		defpathtxt = defpathtxt[:-1]  # remove /n special character
		print(defpathtxt)
		str_path_txt.delete(0, END)# pulisco il campo di input
		if os.path.exists(defpathtxt) == False:
			defpathshp = ""
		txt_filename = tkinter.filedialog.askopenfilename(filetypes=(("txt file", "*.txt"), ("All files", "*.*")),
													  initialdir=defpathshp)
		str_path_txt.insert(10, txt_filename)
		linecache.clearcache()
	except:
		pass


def save_shapefile():
	"""
	Funzione di definzione dei file SSAP di output.
	Funzione richiamata dall'interfaccia tkinter
	"""
	try:
		defpathshape = os.getcwd()+linecache.getline("default.txt", 4)
		defpathshape = defpathshape[:-1]  # remove /n special character
		str_path_shape.delete(0, END)
		if not os.path.exists(defpathshape):
			defpathshape = ""
		SHP_name = tkinter.filedialog.asksaveasfilename(filetypes=(("Shapefile", "*.shp"), ("All files", "*.*")),
														 initialdir=defpathshape)
		shape_text_pathname = os.path.splitext(SHP_name)[0]
		str_path_shape.insert(10, SHP_name)
		linecache.clearcache()
	except:
		pass


def active_disable_button(*args):
	"""
	active or disable button 'Converti' and 'Verifica' by input and output entry
	"""
	x = var1.get()
	y = var2.get()
	if os.path.exists(x):
		if os.path.isdir(os.path.dirname(y)) and os.path.basename(y):
			Conv_Button.configure(state='normal')
	else:
		Conv_Button.configure(state='disabled')


try:
	root = tkinter.Tk()
	root.title("Crea shapefile base per SSAP da elenco coordinate - Versione: " + versione)
	master = ttk.Frame(root, padding="12 12 12 12")
	master.grid(column=0, row=0, sticky=(N, W, E, S))
	master.columnconfigure(0, weight=1)
	master.rowconfigure(0, weight=1)
	master['borderwidth'] = 2
	master['relief'] = 'sunken'
	# variable for trace method
	var1 = tkinter.StringVar(root)
	var2 = tkinter.StringVar(root)
	str_path_txt = tkinter.Entry(master, width=75, textvariable=var1)
	str_path_shape = tkinter.Entry(master, width=75, textvariable=var2)
	str_path_txt.grid(row=0, column=1, sticky=(E, W))
	str_path_shape.grid(row=1, column=1, sticky=(E, W))
	Button(master, text='Input text file', command=load_textfile).grid(row=0, column=0, sticky=(W, E), pady=4, padx=8)
	Button(master, text='Output Shapefile per SSAP', command=save_shapefile).grid(row=1, column=0, sticky=(W, E), pady=4, padx=8)
	Button(master, text='Esci', command=master.quit).grid(row=10, column=1, sticky=E, pady=4)
	Conv_Button = Button(master, text='Converti', command=convert_txt2shp)
	Conv_Button.grid(row=10, column=0, sticky=W, pady=4)
	Conv_Button.configure(state=DISABLED)
	var1.trace("w", active_disable_button)
	var2.trace("w", active_disable_button)
	s2 = ttk.Separator(master, orient=HORIZONTAL).grid(column=1, row=5, sticky=(E, W), pady=10)
	s5 = ttk.Separator(master, orient=HORIZONTAL).grid(column=0, row=5, sticky=(E, W), pady=10)
	s3 = ttk.Separator(master, orient=HORIZONTAL).grid(column=0, row=9, sticky=(E, W), pady=10)
	s4 = ttk.Separator(master, orient=HORIZONTAL).grid(column=1, row=9, sticky=(E, W), pady=10)
	check_pendenza_media = IntVar()
	c1 = Checkbutton(master, text = "Back Analysis. Per pendii uniformi: calcola pendenza media e associa a phi", variable = check_pendenza_media, onvalue = 1,
		 					offvalue = 0, height=1, width = 70)
	c1.grid(row=6, column=1, sticky=(E))
	c1.select()

	check_gamma = IntVar()
	c3 = Checkbutton(master, text = "Back Analysis. Valore di prima approssimazione per gamma e gamma saturo:", variable = check_gamma, onvalue = 1,
		 					offvalue = 0, height=1, width = 70)
	c3.grid(row=7, column=1, sticky=(E))
	c3.select()

	check_falda = IntVar()
	c2 = Checkbutton(master, text = "Crea superficie falda parallela alla topografia con soggiacenza di metri:", variable = check_falda, onvalue = 1,
		 					offvalue = 0, height=1, width = 70)
	c2.grid(row=8, column=1, sticky=E)
	c2.select()

	var3 = tkinter.DoubleVar(root)
	str_falda = tkinter.Entry(master, width=5, textvariable=var3)
	str_falda.grid(row=8, column=1, sticky= (E))
	var3.set(0.0)

	var4 = tkinter.DoubleVar(root)
	str_gamma = tkinter.Entry(master, width=5, textvariable=var4)
	str_gamma.grid(row=7, column=1, sticky= (E))
	var4.set(0.0)

	root.mainloop()
except:
	pass
