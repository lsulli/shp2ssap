#!/usr/bin/env pythonw

"""
fromshp2ssap.py
https://code.google.com/p/fromshp2ssap/
Licenza: http://www.gnu.org/licenses/gpl.html
o \fromshp2ssap\licenza\gpl.txt 

Procedura per la creazione di file .dat, .geo, .fld e .mod
per SSAP 2010 (www.SSAP.eu) partendo da shapefile polyline.

Richiede Python 3x, incompatibile con Python 2x.
Richiede il modulo shapefile.py (già presente di default nella distribuzione di fromshp2ssap.py)

Necessita di shapefile in input con struttura geometrica 
e attributi compatibili con le specifiche SSAP.

In particolare è richiesta una struttura dati del tipo seguente, 
rispettando rigidamente ordine e tipologia dei campi:

1° campo utente (User id) :['USER_ID', 'N', 2, 0]
2° campo utente (Tipo file SSAP): ['SSAP', 'C', 3]
3° campo utente (Valore Angolo d'attrito): ['PHI', 'N', 2, 0]
4° campo utente (Coesione efficace): ['C', 'N', 5, 2]
5° campo utente (Coesione non drenata): ['CU', 'N', 5, 2]
6° campo utente (Peso di volume insaturo): ['GAMMA', 'N', 5, 2]
7° campo utente (Peso di volume saturo): ['GAMMASAT', 'N', 5, 2]
8° campo utente (Resistenza Compressione Uniassiale Roccia Intatta): ['SIGCI', 'N', 5, 2]
9° campo utente (Geological Strenght Index):['GSI','N', 5, 2]
10° campo utente (Indice litologico ammasso):['MI','N', 5, 2]
11° campo utente (Fattore di disturbo ammasso):['D','N', 5, 2]
12° campo utente (Valore caratteristico file .svr):['VAl1','N', 5, 2]

Sono implementate funzioni di contollo della struttura degli shapefile di input.

A procedura conclusa positivamente saranno creati i file SSAP 
.dat, .geo, .fld (se richiesto) e .mod.
Quest'ultimo potrà essere aperto direttamente da SSAP 
senza ulteriori interventi dell'utente.

La procedura distigue tra condzioni drenate e non drenate,  
creando rispettivamente file .geo e .mod [nome_input]_c [nome_input]_cu.

Versione 1.1.5 built 17
Autore: Lorenzo Sulli - lorenzo.sulli@gmail.com
L'uso della procedura fromshp2ssap.py è di esclusiva responsabilità dell'utente, 
In accordo con la licenza l'autore non è responsabile per eventuali risultati errati o effetti dannosi 
su hardware o software dell'utente

Si ringrazia l'autore del modulo shapefile.py, alla base di tutte le funzionalità del presente script.
Crediti e riferimenti: jlawhead<at>geospatialpython.com. http://code.google.com/p/pyshp/
"""
import sys
sys.path.insert(0, '.\\moduli_py')
import shapefile
import os
import linecache
import datetime
import tkinter.messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import Tk, N, S, E, W, HORIZONTAL, IntVar, Checkbutton, Button
from tkinter import *
from tkinter import ttk
from tkinter import font
#from math import tan, atan

####### default constant and variable ######
Ver = "1.1.5 - built 20"
VerMsg = Ver+" : check file .dat, .geo, .fld e .mod before use!"
msg_title="Shapefile to SSAP files"
msg_title_error=msg_title+" - Gestione errori"
global msg_err_function
global msg_flds_structure
msg_flds_structure = ("1° campo utente (User id) :['USER_ID', 'N', 2, 0] \n"
					"2° campo utente (Tipo file SSAP): ['SSAP', 'C', 3]\n"
					"3° campo utente (Valore Angolo d'attrito): ['PHI', 'N', 2, 2]\n"
					"4° campo utente (Coesione efficace): ['C', 'N', 5, 2]\n"
					"5° campo utente (Coesione non drenata): ['CU', 'N', 5, 2]\n"
					"6° campo utente (Peso di volume insaturo): ['GAMMA', 'N', 5, 2]\n"
					"7° campo utente (Peso di volume saturo): ['GAMMASAT', 'N', 5, 2]\n"
					"8° campo utente (Resistenza Compressione Uniassiale Roccia Intatta): ['SIGCI', 'N', 5, 2]\n"
					"9° campo utente (Geological Strenght Index):['GSI','N', 5, 2]\n"
					"10° campo utente (Indice litologico ammasso):['MI','N', 5, 2]\n"
					"11° campo utente (Fattore di disturbo ammasso):['D','N', 5, 2]\n"
					"12° campo utente (Valore caratteristico file .svr):['VAl1','N', 5, 2]\n\n"
					"Vedi lo shapefile modello 'shape_ssap.shp' nella dictory ..\\Shape_Test\\ \n")

max_char_msg_err=linecache.getline("default.txt", 6)
max_char_msg_err=max_char_msg_err[:-1]#remove /n special character

if max_char_msg_err.isdigit():
	max_char_msg_err=max_char_msg_err
else:
	max_char_msg_err="750"

trim_tolerance_factor=linecache.getline("default.txt", 8)
trim_tolerance_factor=trim_tolerance_factor[:-1]#remove /n special character

if trim_tolerance_factor.isdigit():
	trim_tolerance_factor=int(trim_tolerance_factor)
	if trim_tolerance_factor < 20:
		trim_tolerance_factor=20
else:
	trim_tolerance_factor=20
	

######## Main Function #########

def shp2ssapfile():
	"""
	Funzione principale di creazione dei file .dat, .geo, .fld e .mod
	Richiama le funzioni di controllo tramite gestione errori unica
	"""
	try:
#flag to handle specific SSAP exception
		#condition to manage deletion of SSAP File. 
		#1 = delete .dat, .geo e mod, 
		#2 = delete .fld, 
		#3 (2+1) = delete .dat, .geo, .mod e .fld,
		#4 = delete .svr, 
		#5 (1+4) = delete .dat, .geo, .mod.,svr, 
		#7 (1+2+4) = delete .dat, .geo, .mod,.fld, .svr 
		Cond_del_file_SSAP=0
		global checkerr1
		checkerr1=0
#initialize msg variable
		msg_err_tot = ""
		msg_err_end = "\n ##### Controllate lo shapefile id input e ripetere la procedura \t"
#set time variable
		t=datetime.datetime.now()
		t2=t.strftime("%A, %d. %B %Y %I:%M%p")
		t2="File creato in data: "+str(t2)
#get shapes feature and attribute from shapefile
		shape_path= e1.get()
#last exit for error input, ordinary way use active_disable_button()
		if os.path.exists(shape_path)==False:
			checkerr1=1
			msg_err_tot = "Non è stato selezionato lo shapefile di Input o lo shapefile indicato non esiste \t \n"
			sys.exit()
#set main shape variables
		sf = shapefile.Reader(shape_path)
		shapes = sf.shapeRecords()
		shapes_geometry = sf.shapes()
		num_shape = len(shapes) #get number of features to manage loop and check order
#check if shape type is polyline and exit if not
		if check_shape_type (shapes_geometry) == True:
			msg_err_tot = msg_err_tot + msg_err_shape_type
			checkerr1 = 1
			sys.exit()
#get fields list from shapefile
		flds = sf.fields 
#check if shapefile fields match SSAP specification but not exit to collect information about errors
		if check_shape_fields_number (flds) == True:
			msg_err_tot = msg_err_tot + msg_err_shape_fields_number
			checkerr1 = 1
		if check_shape_fields_type (flds) == True:
			msg_err_tot = msg_err_tot + msg_err_shape_fields_type
			checkerr1 = 1
		if check_shape_fields_ssap (sf,num_shape) == True:
			msg_err_tot = msg_err_tot + msg_err_shape_fields_ssap
			checkerr1 = 1
#check SSAP limit number of layers
		if check_layers_number(num_shape)== True:
			msg_err_tot = msg_err_tot + msg_err_layer_num
			checkerr1 = 1
#check if ID is continuous
		if check_continuous_order(sf,num_shape,"dat")==True:
			msg_err_tot = msg_err_tot + msg_err_continuous_order
			checkerr1 = 1 
#SSAP file pathname
		ssap_pathname = e2.get()
#last exit for error input, ordinary way use active_disable_button()
		if os.path.isdir(os.path.dirname(ssap_pathname)) == False:
			checkerr1=1
			msg_err_tot = "Non è stato indicato il nome dei file SSAP di output \t \n"
			msg_err_end = "\n ##### Indicare il nome dei file SSAP di output e ripetere la procedura \t"
			sys.exit()
#get topographic limit coordinate to manage trimming of layers
		global x_min_topo, x_max_topo, xlength_topo, xlenght_tolerance
		x_min_topo, x_max_topo = x_topo (num_shape, sf)
		xlength_topo = round(x_max_topo-x_min_topo,2)
		xlenght_tolerance= round(xlength_topo/trim_tolerance_factor,2)
#create all SSAP file - someone will be empty 
		f_dat=open(ssap_pathname+".dat","w+")
		if CheckCu.get()==1:
			f_geo=open(ssap_pathname+"_c.geo","w+")
			f_mod=open(ssap_pathname+"_c.mod","w+")
		else:
			f_geo=open(ssap_pathname+"_cu.geo","w+")
			f_mod=open(ssap_pathname+"_cu.mod","w+")
		Cond_del_file_SSAP = 1
#write header of .dat file
		f_dat.write(chr(124)+t2+"\n")
		f_dat.write(chr(124)+"File .dat per SSAP2010 generato da fromshp2ssap.py, versione " + VerMsg+"\n")
		f_dat.write(chr(124)+"Shapefile di input: '"+e1.get()+"'. Numero di strati: "+ str( num_shape)+". \n")
#print function is useful to show running code result in cmd shell or in phyton shell
		print("fromshp2ssap.py\n"+"Coordinate estratte da Shapefile " + e1.get() + " e convertite in formato .dat:\n")
#counter for while loop and reorder shape drawing not order (id field <> id object)
		mc = 0 # main counter
		a = mc # duplicate counter get from main counter to manage loop (with b variable)
		b = 0 # counter to re-loop when if condition is false
		c = 0 # variable for manage ID = 0 for write .fld file
		cod_mod_fld=0
# list to manage layer error
		list_check_topdown=[]
		my_topdown_list_min=[]
		my_topdown_list_max=[]
#count layers for .dat,.fld and .svr file
		count_fields_dat_fld, count_fields_svr = count_fields_ssap (sf, num_shape)
#main loop: read shapefile and get geometry layers and points for .dat and .fld file, get attribute for .geo file
		while mc < count_fields_dat_fld:
			print ("num_shape del ciclo è = ", count_fields_dat_fld, " - mc del ciclo è = ", mc)
#write polyline only when id field = mc counter
#x value of first point of the shape
			x_min = sf.shapeRecord(a).shape.points[0][0]
#y value of first point of the shape
			y_min = round(sf.shapeRecord(a).shape.points[0][1],2)
# x value of the last point of shape
			x_max = sf.shapeRecord(a).shape.points[-1][0]
#y value of last point of the shape
			y_max = round(sf.shapeRecord(a).shape.points[-1][1],2)
#x e y value to create line equation for trimming
			x_ref1, x_ref2, y_ref1, y_ref2 = xy_ref(sf.shapeRecord(a))
			if (sf.shapeRecord(a).record[1])=="dat" and (sf.shapeRecord(a).record[0])==(mc+1):
				num_pts = len(sf.shapeRecord(a).shape.points)
#write data layer in .geo file
				if (sf.shapeRecord(a).record[7])==0:
					if CheckCu.get()==1:
						f_geo.write("\t"+str(sf.shapeRecord(a).record[2]))
						f_geo.write("\t"+str(sf.shapeRecord(a).record[3]))
						f_geo.write("\t"+str(0))
					else:
						if check_cu_value(sf.shapeRecord(a).record[4],sf.shapeRecord(a).record[0])==True:
							msg_err_tot = msg_err_tot + msg_err_cu_value
							checkerr1 = 1
						else:
							f_geo.write("\t"+str(0))
							f_geo.write("\t"+str(0))
							f_geo.write("\t"+str(sf.shapeRecord(a).record[4]))
					f_geo.write("\t"+str(sf.shapeRecord(a).record[5]))
					f_geo.write("\t"+str(sf.shapeRecord(a).record[6])+"\n")
				else:
					f_geo.write("\t"+str(0))
					f_geo.write("\t"+str(0))
					f_geo.write("\t"+str(0))
					f_geo.write("\t"+str(sf.shapeRecord(a).record[5]))
					f_geo.write("\t"+str(sf.shapeRecord(a).record[6]))
					f_geo.write("\t"+str(sf.shapeRecord(a).record[7]))
					f_geo.write("\t"+str(sf.shapeRecord(a).record[8]))
					f_geo.write("\t"+str(sf.shapeRecord(a).record[9]))
					f_geo.write("\t"+str(sf.shapeRecord(a).record[10])+"\n")
#end write data layer in .geo file
#write header layer of .dat file
				f_dat.write("##"+str(sf.shapeRecord(a).record[0])+"-------------------------- Numero punti: " + str(num_pts)+"\n")
#print to show on shell
				print("##"+str(sf.shapeRecord(a).record[0])+"--------------------------\n")
#check points number limit of a layer
				if check_points_number(len(sf.shapeRecord(a).shape.points),sf.shapeRecord(a).record[0])==True:
					msg_err_tot = msg_err_tot + msg_err_points_number
					checkerr1 = 1
#loop to write x,y coordinate of layers points in .dat file
				for k in sf.shapeRecord(a).shape.points:
#verify negative coordinate
					if check_negative_val(k,sf.shapeRecord(a).record[0]) == True:
						msg_err_tot = msg_err_tot + msg_err_negative_val
						checkerr1 = 1
#layer trimming for geo/dat layer
					if CheckTrimming.get() == 1:
						if k[0]<(x_min_topo+xlenght_tolerance):
							if k[0]==x_min:
								var_x = x_min_topo
								if x_min == x_min_topo:
									var_y = k [1]
								else:
									if global_points_counter>0:
										var_y=get_y_trim_bound(x_ref1, x_min, y_ref1, y_min, x_min_topo)
									else:
										var_y=get_y_trim_bound(x_ref2, x_min, y_ref2, y_min, x_min_topo)
							else:
								continue
						elif k[0]>(x_max_topo-xlenght_tolerance):
							if k[0]==x_max:
								var_x = x_max_topo
								if x_max == x_max_topo:
									var_y = k[1]
								else:
									if global_points_counter>0:
										var_y=get_y_trim_bound (x_ref2, x_max, y_ref2, y_max, x_max_topo)
									else:
										var_y=get_y_trim_bound (x_ref1, x_max, y_ref1, y_max, x_max_topo)
							else:
								continue
						else:
							var_x = k[0]
							var_y = k[1]
					else:
						var_x = k[0]
						var_y = k[1]

#end trimming for geo/dat layer
#write x, y coordinate rounded to first decimal
					f_dat.write("\t"+format_f_str(var_x)+"\t\t") #write x coordinate
					f_dat.write(format_f_str(var_y)+"\n")#write y coordinate
#append all y value in list to check correct id order topdown
					list_check_topdown.append (round(k[1],2))
#print to show shell
					print("\t"+format_f_str(var_x)+"\t",format_f_str(var_y)+"\n")
#get min value of y value from any layer
				list_check_topdown.sort()
				my_ymin=list_check_topdown[0]
				my_ymax=list_check_topdown[-1]
				my_topdown_list_min.append(my_ymin)
				my_topdown_list_max.append(my_ymax)
				list_check_topdown=[]
				mc+=1
				a = mc-b
				if a < 0:
					a = 0 # negative id object not exist
#write .fld file if ID = 0
			elif (sf.shapeRecord(a).record[1])=="fld" and (sf.shapeRecord(a).record[0])==(c):
				if check_points_number(len(sf.shapeRecord(a).shape.points),sf.shapeRecord(a).record[0])==True:
					msg_err_tot = msg_err_tot + msg_err_points_number
					checkerr1 = 1
				f_fld=open(ssap_pathname+".fld","w+")
				for k in sf.shapeRecord(a).shape.points:
					if check_negative_val(k,sf.shapeRecord(a).record[0]) == True:
						msg_err_tot = msg_err_tot + msg_err_negative_val
						f_fld.close
						checkerr1 = 1
#layer trimming for fld layer
					if CheckTrimming.get() == 1:
						if k[0]<(x_min_topo+xlenght_tolerance):
							if k[0]==x_min:
								var_x = x_min_topo
								if x_min == x_min_topo:
									var_y = k [1]
								else:
									if global_points_counter>0:
										var_y=get_y_trim_bound(x_ref1, x_min, y_ref1, y_min, x_min_topo)
									else:
										var_y=get_y_trim_bound(x_ref2, x_min, y_ref2, y_min, x_min_topo)
							else:
								continue
						elif k[0]>(x_max_topo-xlenght_tolerance):
							if k[0]==x_max:
								var_x = x_max_topo
								if x_max == x_max_topo:
									var_y = k[1]
								else:
									if global_points_counter>0:
										var_y=get_y_trim_bound (x_ref2, x_max, y_ref2, y_max, x_max_topo)
									else:
										var_y=get_y_trim_bound (x_ref1, x_max, y_ref1, y_max, x_max_topo)
							else:
								continue
						else:
							var_x = k[0]
							var_y = k[1]
					else:
						var_x = k[0]
						var_y = k[1]
#end trimming for fld layer

					f_fld.write("\t"+format_f_str(var_x)+"\t\t") #write x coordinate
					f_fld.write(format_f_str(var_y)+"\n")#write y coordinate
				f_fld.close()
# new c value to skip if condition about .fld file (no id value > num shape is admitted)
				c = count_fields_dat_fld+1
#new limit of loop
				count_fields_dat_fld = count_fields_dat_fld-1
				print ("num_shape f(fld) = ", count_fields_dat_fld)
				Cond_del_file_SSAP=Cond_del_file_SSAP+2
			else:
				a = a+1
				b = b+1
				continue
###### .svr code ######

#check if svr layer exist and if exist set counter
		if count_fields_svr >0:
			f_svr=open(ssap_pathname+".svr","w+")
			svr_counter = 0 # main counter
			a_svr = mc # duplicate counter get from main counter to manage loop (with b variable)
			b_svr = 0 # counter to re-loop when if condition is false
#loop: read shapefile and get geometry layers and points for .svr
			while svr_counter < count_fields_svr:
				print ("num_shape del ciclo per svr è = ", count_fields_svr, " - svr_counter del ciclo è = ", svr_counter)
	#write polyline only when id field = mc counter
				if (sf.shapeRecord(a_svr).record[1])=="svr" and (sf.shapeRecord(a_svr).record[0])==(svr_counter+1):
					num_pts = len(sf.shapeRecord(a_svr).shape.points)
	#check points number limit of a layer
					if check_points_number(len(sf.shapeRecord(a_svr).shape.points),sf.shapeRecord(a_svr).record[0])==True:
						msg_err_tot = msg_err_tot + msg_err_points_number
						checkerr1 = 1
	#loop to write x,y coordinate of layers points in .dat file
					for k in sf.shapeRecord(a_svr).shape.points:
	#verify negative coordinate
						if check_negative_val(k,sf.shapeRecord(a_svr).record[0]) == True:
							msg_err_tot = msg_err_tot + msg_err_negative_val
							checkerr1 = 1
						var_x = k[0]
						f_svr.write(format_f_str(var_x)+"\t") #write x coordinate
	#print to show shell
						print("svr:" + format_f_str(var_x)+"\t")
	#write pressure value
					f_svr.write(format_f_str(sf.shapeRecord(a_svr).record[11])+"\n")
	#print to show shell
					print("\n"+"svr pressure value:" + format_f_str(sf.shapeRecord(a_svr).record[11])+"\t")

					svr_counter+=1
					a_svr = svr_counter-b_svr
					if a_svr < 0:
						a_svr = 0 # negative id object not exist
				else:
					a_svr = a_svr+1
					b_svr = b_svr+1
					continue
			f_svr.close()
			Cond_del_file_SSAP=Cond_del_file_SSAP+4
		
			
		f_dat.close()
		f_geo.close()

		if Cond_del_file_SSAP==7:
			f_mod.write(str(count_fields_dat_fld)+"    1    1    0    0    0"+"\n")
			f_mod.write((os.path.basename(f_dat.name))+"\n"+os.path.basename(f_fld.name)+"\n"+os.path.basename(f_geo.name)+ "\n"+
						os.path.basename(f_svr.name))
			msg_fld_str=os.path.abspath(f_fld.name)+"\n"+os.path.abspath(f_svr.name)+"\n"
		elif Cond_del_file_SSAP==5:
			f_mod.write(str(count_fields_dat_fld)+"    0    1    0    0    0"+"\n")
			f_mod.write((os.path.basename(f_dat.name))+"\n"+"\n"+os.path.basename(f_geo.name)+ "\n"+os.path.basename(f_svr.name))
			msg_fld_str=os.path.abspath(f_svr.name)+"\n"
		elif Cond_del_file_SSAP==3:
			f_mod.write(str(count_fields_dat_fld)+"    1    0    0    0    0"+"\n")
			f_mod.write((os.path.basename(f_dat.name))+"\n"+os.path.basename(f_fld.name)+"\n"+os.path.basename(f_geo.name))
			msg_fld_str=os.path.abspath(f_fld.name)+"\n"
		elif Cond_del_file_SSAP==1:
			f_mod.write(str(count_fields_dat_fld)+"    0    0    0    0    0"+"\n")
			f_mod.write(os.path.basename(f_dat.name)+"\n"+os.path.basename(f_geo.name))
			msg_fld_str=""

		f_mod.close()

		if CheckTopoDownOrder.get() == 1:
			if check_topdown_order(my_topdown_list_min,my_topdown_list_max) == True:
				msg_err_tot = msg_err_tot + msg_err_topdown_order
				checkerr1 = 1

		if checkerr1 == 1:
			sys.exit()

		tkinter.messagebox.showinfo(msg_title,"Procedura conclusa. Verifica i file SSAP: \n"+
									os.path.abspath(f_dat.name) + "\t\n"+ os.path.abspath(f_geo.name) + "\t\n"+
									msg_fld_str +os.path.abspath(f_mod.name) + "\t\n")
#just a default except to handle error, there are two main type error: SSAP type (checkerr1=1) and system error (checkerr1 = 0), in system error 
#specific error are handled by type default_msg_unknow_error function that return system error and name of function that catch error
	except:
		if checkerr1==0:
			tkinter.messagebox.showerror(msg_title_error, "Si è verificato un errore!\n"+"La procedura termina \n\n Descrizione dell'errore: \n"
			+str(sys.exc_info()[0])+ "\n" + str(sys.exc_info()[1])+msg_err_function)
		elif checkerr1==1:
			if len(msg_err_tot) > int(max_char_msg_err):
				msg_err_tot = msg_err_tot[:int(max_char_msg_err)]+".......\n\n"
			tkinter.messagebox.showinfo(msg_title_error,"##### Shapefile: '"+e1.get()+"'\n"+
			"##### Sono stati riscontrati errori nella conversione ai file per SSAP: \t" +
			"\n\n"+msg_err_tot+msg_err_end)
#remove ssap file
		if Cond_del_file_SSAP == 7:
			 remove_file(f_dat, f_geo, f_mod, f_fld, f_svr)
		elif Cond_del_file_SSAP == 5:
			 remove_file(f_dat, f_geo, f_mod, f_svr)
		elif Cond_del_file_SSAP == 3:
			 remove_file(f_dat, f_geo, f_fld, f_mod)
		elif Cond_del_file_SSAP == 1:
			 remove_file(f_dat, f_geo, f_mod)



############## - Utility Function  for SSAP code - ##############

def remove_file (*remove_file):
	"""
	Elimina i file di output se richiesto dalla funzione principale shp2ssapfile()
	"""

	try:
		for x in remove_file:
			if os.path.exists(os.path.abspath(x.name)):
				x.close()
				os.remove((os.path.abspath(x.name)))
	except:
		default_msg_unknow_error("remove_file")

def format_f_str (float_coord):
	try:
		coord_format = "{0:.2f}".format(round(float_coord,2))
		return coord_format
	except:
		default_msg_unknow_error("format_float_string")

############## - check file for SSAP code - ##############

def default_msg_unknow_error(function_name):
	"""
	Creazione messaggio di errore personalizzato per singola funzione (arg function_name)
	Rimanda all'except della funzione principale shp2ssapfile()
	"""
	msg_err_function = ""
	msg_err_function = ("\n Errore spefico nella funzione '" + function_name + "': \n"
	+ str(sys.exc_info()[0])+ "\n"+ str(sys.exc_info()[1])+"\n \n Verificare il codice o contattare l'autore. \n Mail: lorenzo.sulli@gmail.com")
	sys.exit()
def check_negative_val (point_coord, layer_id):
	"""
	Verifica la presenza di valori negativi delle coordinate
	Funzione richiamata dalla funzione principale shp2ssapfile()
	"""
	try:
		if (point_coord[0] < 0) or (point_coord[1] < 0):
			global msg_err_negative_val
			msg_err_negative_val= ""
			msg_err_negative_val = ("nello  strato ID = " + str(layer_id)
								+ " sono presenti coordinate negative (x=" + format_f_str(point_coord[0])
								+ ", y=" + format_f_str(point_coord[1])+")\t\n")
			return True
		else:
			return False
	except:
			default_msg_unknow_error("check_negative_val")
def check_layers_number (layer_num):
	"""
	Verifica il numero totale di strati in riferimento allo standard SSAP
	Funzione richiamata dalla funzione principale shp2ssapfile()
	"""

	try:
		if layer_num > 20:
			global msg_err_layer_num
			msg_err_layer_num = ""
			msg_err_layer_num = ("Il numero di polyline nello shapefile "
			+" è pari a " +str(layer_num)+ " superiore a 20, limite ammesso da SSAP.\t\n\n")
			return True
		
	except:
			default_msg_unknow_error("check_layers_number")
def check_points_number (points_num, layer_id):
	"""
	Verifica il numero totale di punti di ogni strato in riferimento allo standard SSAP
	Funzione richiamata dalla funzione principale shp2ssapfile()
	"""

	try:
		if (points_num)> 100:
			global msg_err_points_number
			msg_err_points_number = ""
			msg_err_points_number = ("Il numero di punti dello strato ID=" + str(layer_id)
			+ " è superiore a 100, limite ammesso da SSAP.\t\n")
			return True
		else:
			return False
	except:
		default_msg_unknow_error("check_points_number")
def check_topdown_order (mylist_min,mylist_max):
	"""
	Verifica che gli strati di input abbiano indici ordinati dall'alto verso il basso
	Si tratta di una verifica di tipo geometrico (basata sui valori delle coordinate di y) diversa dalla
	verifica della funzione check_continuous_order che si basa sui valori degli indici e non è in grado 
	di discriminare eventuali incongruenze geometriche.
	Funzione richiamata dalla funzione principale shp2ssapfile()
	"""

	try:
		myorderlist_min = mylist_min [:]
		myorderlist_min.sort()
		myorderlist_min.reverse()
		myorderlist_max = mylist_max[:]
		myorderlist_max.sort()
		myorderlist_max.reverse()

		if (mylist_min != myorderlist_min) and (mylist_max != myorderlist_max):
			global msg_err_topdown_order
			msg_err_topdown_order = ""
			msg_err_topdown_order = ("Possibili problemi con la seguenza del campo indice delle polyline nello shapefile, "
			+ "probabili cause:\n"+"- la seguenza verticale è continua ma non è ordinata\t\n"
			+"- è presente una lente o un muro che non rispetta la numerazione sencondo gli standard SSAP\n\n"
			+"Attenzione: per modelli complessi sono possibili false segnalazioni di errore.\n"
			+"In tal caso riprovare escludendo la 'verifica ordinamento verticale strati'\n\n")
			return True
		else:
			return False
	except:
		default_msg_unknow_error("check_topdown_order")
def check_continuous_order (my_shape,layer_num, type_ssap):
	"""
	Verifica che gli strati di input abbiano indici continui.
	Si tratta di una verifica di tipo formale sui valori degli indici 
	non è possibile discriminare eventuali incongruenze geometriche.
	Funzione richiamata dalla funzione principale shp2ssapfile()
	"""

	try:
		global msg_err_continuous_order
		msg_err_continuous_order = ""
		msg_err_continuous_order_n1 = ""
		f=0
		tot_shape = layer_num #copy num_shape
#create list for id value
		id_list=[]
#create list for x value
		x_value_topo = []
		while f < layer_num:
#get id value
			if my_shape.shapeRecord(f).record[1] == type_ssap:
				id_list.append(my_shape.shapeRecord(f).record[0])
			f+=1
#manage list of id value
		id_list_ordered=id_list[:]
		id_list_ordered.sort()
		perfectorder = []

		if id_list_ordered[0] == 0:
			perfectorder = list (range(0, len(id_list)))
		elif id_list_ordered[0] == 1:
			perfectorder = list (range(1, len(id_list)+1))
		else:
			msg_err_continuous_order_n1 = ("- la seguenza degli indici dello strato inizia con ID = " + str(id_list_ordered[0])
			+", deve iniziare con 0 (in presenza di falda) o 1 (in assenza di falda) \n")
			
		if (id_list_ordered != perfectorder):
			msg_err_continuous_order = ("Problemi con la seguenza del campo indice delle polyline nello shapefile"
			+"\n\n" + "Per i layer '" + type_ssap + "' La seguenza degli indici ordinata è: " + str(id_list_ordered) 
			+ "\n\n possibili cause:\n"+"- la seguenza dell'indice è continua ma più strati hanno lo stesso ID \t\n"
			+"- la seguenza dell'indice non è continua\n" + msg_err_continuous_order_n1+"\n")
			return True
		else:
			return False

	except:
		default_msg_unknow_error("check_continuous_order")
def check_shape_type (my_shapes):
	"""
	Verifica tipologia dello shapefile di input.
	Funzione richiamata dalla funzione principale shp2ssapfile()
	"""

	try:
		global msg_err_shape_type
		msg_err_shape_type = ""
		if my_shapes[0].shapeType != 3: # 3 = polyline type in ESRI specification
			msg_err_shape_type = ("Lo shapefile non è del tipo 'polyline' \n\n")
			return True
		else:
			return False
	except:
		default_msg_unknow_error("check_shape_type")
def check_shape_fields_number (my_flds):
	"""
	Verifica del numero di campi di input.
	Funzione richiamata dalla funzione principale shp2ssapfile()
	"""

	try:
		global num_flds
		num_flds = len(my_flds)
		global msg_err_shape_fields_number
		msg_err_shape_fields_number = ""
		if num_flds < 12:
			msg_err_shape_fields_number = ("Lo shapefile ha n." + str(len(my_flds)-1) + " campi definiti dall'utente. \n"
											+ "I campi devono essere almeno 12, del tipo:\n"
											+msg_flds_structure+"\n\n")
			return True
		else:
			return False
	except:
		default_msg_unknow_error("check_shape_fields_number")

def check_shape_fields_type (my_flds):
	"""
	Verifica tipologia dati dei primi 12 campi utente di input.
	Funzione richiamata dalla funzione principale shp2ssapfile()
	"""

	try:
		global msg_err_shape_fields_type
		msg_err_shape_fields_type = ""
		msg_err_tmp = ""
		#salta il primo campo di sistema ('DeletionFlag', 'C', 1, 0)
		xcount = 0
		for a in my_flds[1:2]:
			xcount +=1
			if a[1]!='N':
				msg_err_tmp = ("Il 1° campo utente '" + str(a[0]) + "' dello shapefile non è numerico. \n")
				msg_err_shape_fields_type = msg_err_shape_fields_type + msg_err_tmp
		for b in my_flds[2:3]:
			xcount +=1
			if b[1]!='C':
				msg_err_tmp = ("Il 2° campo utente '" + str(b[0]) + "' dello shapefile non è stringa. \n")
				msg_err_shape_fields_type = msg_err_shape_fields_type + msg_err_tmp
		for c in my_flds[3:13]:
			xcount +=1
			if c[1]!='N':
				msg_err_tmp = ("Il " +str(xcount)+ "° campo utente '" + str(c[0]) + "' dello shapefile non è numerico. \n")
				msg_err_shape_fields_type = msg_err_shape_fields_type + msg_err_tmp
		if len (msg_err_shape_fields_type) > 0:
			msg_err_shape_fields_type = (msg_err_shape_fields_type
			+ "\n I campi devono avere una struttura del tipo: \n"
			+ msg_flds_structure+ "\n\n")
			return True
		else:
			return False
	except:
		default_msg_unknow_error("check_shape_fields_type")
def check_shape_fields_ssap (xsf, xshape_num):
	"""
	Verifica tipologia dati dei primi 6 campi utente di input.
	Funzione richiamata dalla funzione principale shp2ssapfile()
	"""

	try:
		global msg_err_shape_fields_ssap
		msg_err_shape_fields_ssap = ""
		a = 0
		xlist = []
		xset = {}
		ssapset = {"dat", "fld", "svr"}
		while a < xshape_num:
			xlist.append(xsf.shapeRecord(a).record[1])
			a+=1
		xset = set(xlist)
		list_msg=list(xset-ssapset)
		for a in xlist:
			if a not in ssapset:
				msg_err_shape_fields_ssap = ("Il 2° campo utente deve indicare il tipo di file SSAP da creare. \n"
										+"Risultano presenti i seguenti valori errati o incoerenti rispetto alle specifiche SSAP: \n"
										+str(list_msg)+ "\n\n")
				return True
				break
		else:
			return False
	except:
		default_msg_unknow_error("check_shape_fields_ssap")

def count_fields_ssap (xsf, xshape_num):
	"""
	Conteggia il numero di feature per ogni tipo di file SSAp indicati nel campo relativo.
	Funzione richiamata dalla funzione principale shp2ssapfile()
	"""
	try:
		xcount_dat_fld = 0
		xcount_svr = 0
		a = 0
		while a < xshape_num:
			if xsf.shapeRecord(a).record[1] == "dat" or xsf.shapeRecord(a).record[1] == "fld":
				xcount_dat_fld +=1
			elif xsf.shapeRecord(a).record[1] == "svr":
				xcount_svr +=1
			a+=1
		return xcount_dat_fld, xcount_svr
	except:
		default_msg_unknow_error("count_fields_ssap")
def check_cu_value (cu_value, layer_id):
	try:
		global msg_err_cu_value
		msg_err_cu_value = ""
		if cu_value == 0:
			msg_err_cu_value = ("Il valore di CU dello strato " + str(layer_id)
			+ " è zero, la verifica in condizioni non drenate non è applicabile.\t\n")
			return True
		else: 
			return False
	except:
		default_msg_unknow_error("check_cu_value")


############## - function to manage layer trimming - ##############
def x_topo(n_shp,shp):
	"""
	Restituisce i valori x massimi e minimi della
	superficie topografica
	"""
	try:
		var_x_min = 0
		var_x_max = 0
		f = 0
		while f < n_shp:
			if (shp.shapeRecord(f).record[1])=="dat" and (shp.shapeRecord(f).record[0])==(1):
				var_x_min=round(shp.shapeRecord(f).shape.points[0][0],2)
				var_x_max=round(shp.shapeRecord(f).shape.points[-1][0],2)
			f+=1
		return var_x_min, var_x_max
	except:
		default_msg_unknow_error("x_topo")

def xy_ref (shp_rec):
	"""
	Restituisce i valori di riferimento x e y utili alla definizione 
	della funzione della retta che unisce i due punti estremi della superfici di strato
	che rientra nei limiti di tolleranza definiti dalla superficie topografica
	"""
	try:
		var_y_ref1 = 0
		var_y_ref2 = 0
		var_x_ref1 = 0
		var_x_ref2 = 0
		global global_points_counter
		global_points_counter = 0
		c = 0
		for k in shp_rec.shape.points:
			if k[0]> (x_min_topo+xlenght_tolerance) and k [0] < (x_max_topo-xlenght_tolerance):
				global_points_counter +=1 
		for k in shp_rec.shape.points:
			if global_points_counter>0:
				if k[0]> (x_min_topo+xlenght_tolerance) and k [0] < (x_max_topo-xlenght_tolerance):
					c+=1
					if c == 1:
						var_y_ref1 = k[1]
						var_x_ref1 = k[0]
					elif c == global_points_counter:
						var_y_ref2 = k[1]
						var_x_ref2 = k[0]
			else:
				var_x_ref1 = shp_rec.shape.points[0][0]
				var_y_ref1 = shp_rec.shape.points[0][1]
				var_x_ref2 = shp_rec.shape.points[-1][0]
				var_y_ref2 = shp_rec.shape.points[-1][1]
		return var_x_ref1, var_x_ref2, var_y_ref1, var_y_ref2
	except:
		default_msg_unknow_error("xy_ref")

def get_y_trim_bound (x1, x2, y1, y2, var_x_topo):
	"""
	Restituisce il valore della y dell'n-esima superficie di strato 
	corrispondente al valore x della superficie topografica giacente sulla retta
	congiugente due punti di riferimento.
	"""
	try:
		c=0
		m=0
		y=0
		m=(y1-y2)/(x1-x2) #coefficiente angolare y1-y2/x1-x2
		c=(x1*y2-x2*y1)/(x1-x2)#intercetta ordinate x1*y1-x2*y1/x1-x2
		y=c+m*var_x_topo# valore y da equazione retta conoscendo x superfcie topografica
		return y
	except:
		default_msg_unknow_error("get_y_trim_bound")

############## - tkinter/ttk code - ###################

def load_shapefile():
	"""
	Funzione di caricamento degli sahpefile di input.
	Funzione richiamata dall'interfaccia tkinter 
	"""

	try:
#load default path value from default.txt file
		defpathshp=linecache.getline("default.txt", 2)
		defpathshp=defpathshp[:-1]#remove /n special character
		e1.delete(0,END)
		if os.path.exists(defpathshp)==False:
			defpathshp= ""
		shp_name = tkinter.filedialog.askopenfilename(filetype=(("Shapefile", "*.shp"),("All files", "*.*")), initialdir=defpathshp)
		e1.insert(10,shp_name)
		linecache.clearcache()
	except:
		default_msg_unknow_error("load_shapefile")

def save_SSAPfiles():
	"""
	Funzione di definzione dei file SSAP di output.
	Funzione richiamata dall'interfaccia tkinter 
	"""

	try:
		defpathssap=linecache.getline("default.txt", 4)
		defpathssap=defpathssap[:-1]#remove /n special character
		e2.delete(0,END)
		if os.path.exists(defpathssap)==False:
			defpathssap= ""
		SSAP_name = tkinter.filedialog.asksaveasfilename(filetypes=(("SSAP FILES", "*.mod*"),("All files", "*.*")),initialdir=defpathssap)
		ssap_text_pathname = os.path.splitext(SSAP_name)[0]
		e2.insert(10,ssap_text_pathname)
		linecache.clearcache()
	except:
		default_msg_unknow_error("save_SSAPfiles")
def active_disable_button (*args):
	"""
	active or disable button 'Converti' by input and output entry
	"""
	x=var1.get()
	y=var2.get()
	if os.path.exists(x) and os.path.isdir(os.path.dirname(y)) and os.path.basename(y):
		xbutton.configure(state='normal')
	else:
		xbutton.configure(state='disabled')


root = tkinter.Tk()
root.title("Conversione da polyline shapefile a file per SSAP - Versione: "+Ver)

master = ttk.Frame(root, padding="12 12 12 12")
master.grid(column=0, row=0, sticky=(N, W, E, S))
master.columnconfigure(0, weight=1)
master.rowconfigure(0, weight=1)
master['borderwidth'] = 2

master['relief'] = 'sunken'
#variable for trace method
var1 = tkinter.StringVar(root)
var2 = tkinter.StringVar(root)
e1 = tkinter.Entry(master, width=60, textvariable= var1)
e2 = tkinter.Entry(master, width=60, textvariable= var2)

e1.grid(row=0, column=1,sticky= (E, W))
e2.grid(row=1, column=1,sticky= (E, W))

Button(master, text='Input Shapefile', command=load_shapefile).grid(row=0, column=0, sticky=(W,E), pady=4, padx=8)
Button(master, text='Output SSAP files name', command=save_SSAPfiles).grid(row=1, column=0, sticky=(W,E), pady=4, padx=8)
Button(master, text='Esci', command=master.quit).grid(row=9, column=1, sticky=E, pady=4)
xbutton=Button(master, text='Converti', command=shp2ssapfile)
xbutton.grid(row=9, column=0, sticky=W, pady=4)
xbutton.configure(state = DISABLED)

var1.trace("w", active_disable_button)
var2.trace("w", active_disable_button)

#s = ttk.Separator(master, orient=HORIZONTAL).grid(column=0, row=5, sticky= (E, W),pady=10)
s2 = ttk.Separator(master, orient=HORIZONTAL).grid(column=1, row=5, sticky= (E, W),pady=10)
s3 = ttk.Separator(master, orient=HORIZONTAL).grid(column=0, row=8, sticky= (E, W),pady=10)
s4 = ttk.Separator(master, orient=HORIZONTAL).grid(column=1, row=8, sticky= (E, W),pady=10)


l1 = ttk.Label(master, text = '  Opzioni controllo e creazioni strati', borderwidth = 5,  relief = GROOVE,  foreground = 'black' )
l1.grid (column=0, row=5, pady=10, ipadx=10, ipady=5, sticky= (N+S))

CheckCu = IntVar()
c1 = Checkbutton(master, text = "Verifica in condizioni drenate, Cu=0", variable = CheckCu, onvalue = 1, offvalue = 0, height=1, width = 30)
c1.grid(row=3, column=0, sticky=(W))
c1.select()

CheckTopoDownOrder = IntVar()
c2 = Checkbutton(master, text = "Verifica ordinamento verticale strati", variable = CheckTopoDownOrder, onvalue = 1, offvalue = 0,
                 height=1, width = 30)
c2.grid(row=6, column=0, sticky=(W))
c2.select()

CheckTrimming = IntVar()
c3 = Checkbutton(master, text = "Regola gli strati alla superficie topografica", variable = CheckTrimming, onvalue = 1, offvalue = 0,
                 height=1, width = 35)
c3.grid(row=6, column=1, sticky=(E))
c3.select()

root.mainloop( )


