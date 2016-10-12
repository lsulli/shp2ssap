#!/usr/bin/env pythonw

# Versione 1.1.6 build 167 - 2016.06.28

# TEST FILE - In sviluppo FUNZIONA da verificare ulteriormente per funzioni di controllo
# Riorganizzazione testi messaggi errore

# Modificato gestione errori coordinate negative: funziona ma DA COMPLETARE
# Modifica gestione dati drained undrained - campo DR_UNDR ed eliminazioen opzione C/Cu per intero modello.
# Modifica con inserimento opzione di esclusione strato  - Campo CONVERT
# creazione file .sin
# separata gestione errori tra check_function() e Shp_2_SSAP_Files() e ottimizzazione avvisi info vs errori
# Controllate dichiarazioni global:devono essere mantenute
# ottimizzata procedura di eliminazione file ssap tramite lista
# ottimizzata procedura di messaggio finale positivo tramite lista
# aggiornata numerazione da build 1.1.6 build 38 a 1.1.6 build 155 per conteggiare i build antecedenti a 1.1.6
# UpperCase per le funzioni e LowerCase per le variabili
# inserita funzioen controllo aggetto nella superfici topografica 

# - sembra risolto ERRORE scrittura valori GEO (tutti zero) in presenza di campi  geo rock (vari test ok)
# - Sembra che in alcuni casi non genera il file .fld (casistica non verificata con test)
# - con assenza del campo VAL2 genera errore di sistema?
# - test con campi assenti datgeo, rock, svr: ok (5-6 ripetizioni)
# - test con punti coordinate negative: ok
# - test con strati ad alta pendenza per verifica controllo sequenza alto-basso:ok.
# - Tende a tagliare lo strato più basso sulla Y invece che sulla X?
# - test controllo sequenza campi: ok
# - test campo SSAP errato: ok

# DA FARE: aggiornare check_points_number() con riferimento al tipo di layer SSAP

"""
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
In particolare e' richiesta una struttura dati del tipo seguente, 
rispettando tipologia dei campi che possono essere in qualsiasi ordine:
Obbligatorio (SSAP id) :['SSAP_ID', 'N', 2, 0]
Obbligatorio (Tipo file SSAP - possibili valori: 'dat', 'fld', 'svr', 'sin'): ['SSAP', 'C', 3]
Obbligatorio (Valore Angolo d'attrito - gradi ): ['PHI', 'N', 2, 0]
Obbligatorio (Coesione efficace - kpa): ['C', 'N', 5, 2]
Obbligatorio (Coesione non drenata - kpa ): ['CU', 'N', 5, 2]
Obbligatorio (Peso di volume insaturo - KN/mc): ['GAMMA', 'N', 5, 2]
Obbligatorio (Campo booleano per escludere strato. 1: escludi - valore predefinito, <> 1: converti, valore predefinito):
																				['EXCLUDE', 'N', 1, 0]
Obbligatorio (Campo scelta verifica condizioni drenate/non drenate. U: non drenato (Undrained), D o <> U drenato, valore predefinito):
																				['DR_UNDR', 'C', 1, 0]
Opzionale (Resistenza Compressione Uniassiale Roccia Intatta): ['SIGCI', 'N', 5, 2]
Opzionale (Geological Strenght Index):['GSI','N', 5, 2]
Opzionale (Indice litologico ammasso):['MI','N', 5, 2]
Opzionale (Fattore di disturbo ammasso):['D','N', 5, 2]
Opzionale (Valore caratteristico file .svr - Kpa):['VAl1','N', 5, 2]

Nel campo SSAP_ID deve essere inserita una sequenza continua ed ordinata numerica intera univoca con base 1
per ogni tipologia SSAP (indicata nel campo SSAP), fa eccezione la falda (SSAP = 'fld')
che deve essere un unico elemento con SSAP_ID = 0

Nel campo SSAP deve essere indicato a quale file ssap e' riferita la polyline.
Valori ammessi: .dat, .fld e .svr. Il file .geo e' generato in base ai valori dei campi PHI, C, CU etc.

Nel campo VAL1 e' indicato il valore in kpa dei carichi

Il campo EXCLUDE serve ad escludere alcuni strati dalla conversione (ad esempio i sovraccarichi o la falda)
Il campo EXCLUDE è impostato di default con 0 o null, valori diversi da 1 indicano che il layer deve essere convertito.
Se si escludono layer 'dat' o alcuni layer 'svr' deve essere ridefinita una seguenza continua dall'alto al basso
dei valori di SSAP_ID.

Sono implementate funzioni di contollo della struttura degli shapefile di input.

A procedura conclusa positivamente saranno creati i file SSAP 
.dat, .geo,  e .mod., i file .fld e .svr saranno presenti se richiesti
Il file .mod potrà essere aperto direttamente da SSAP 
senza ulteriori interventi dell'utente.
La procedura distigue tra condzioni drenate e non drenate,  
creando rispettivamente file .geo e .mod [nome_input]_c [nome_input]_cu.


Autore: Lorenzo Sulli - lorenzo.sulli@gmail.com
L'uso della procedura fromshp2ssap.py e' di esclusiva responsabilità dell'utente, 
In accordo con la licenza l'autore non e' responsabile per eventuali risultati errati o effetti dannosi 
su hardware o software dell'utente
Si ringrazia l'autore del modulo shapefile.py, alla base di tutte le funzionalità del presente script.
Crediti e riferimenti: jlawhead<at>geospatialpython.com. https://github.com/GeospatialPython/pyshp
"""
import tkinter.messagebox
import os
import linecache
import datetime
from tkinter.filedialog import asksaveasfilename
from tkinter import *
from tkinter import ttk
import inspect
import re

msg_title = "Shapefile to SSAP files"
msg_title_error = msg_title + " - Gestione errori"
msg_title_check = msg_title + " - Verifica Tipo e Campi Shapefile"
py_file = os.path.basename(sys.argv[0])
versione = "1.1.6 - build 167 alfa"
ver_msg = versione + " : check file .dat, .geo, .fld e .mod before use!"
msg_err_function = ""
msg_flds_structure = "Controlla il manuale utente e vedi lo shapefile modello " \
					 + "'shape_ssap.shp' nella directory ../Shape_Test/ \n"
msg_err_end = "\n ##### Controllare lo shapefile di input e ripetere la procedura \t"
msg_fld_str = ""

try:
	sys.path.insert(0, './moduli_py')
	import shapefile

	# ###### default constant and variable that need try - except######
	max_char_msg_err = linecache.getline("default.txt", 6)
	max_char_msg_err = max_char_msg_err[:-1]  # remove /n special character

	if max_char_msg_err.isdigit():
		max_char_msg_err = max_char_msg_err
	else:
		max_char_msg_err = "750"

	trim_tolerance_factor = linecache.getline("default.txt", 8)
	trim_tolerance_factor = trim_tolerance_factor[:-1]  # remove /n special character

	if trim_tolerance_factor.isdigit():
		trim_tolerance_factor = int(trim_tolerance_factor)
		if trim_tolerance_factor < 20:
			trim_tolerance_factor = 20
	else:
		trim_tolerance_factor = 20


	def check_function(pass_check):
		"""
		Funzione di controllo preliminare di coerenza dello shapefile con le specifiche SSAP.
		Invocata dal tasto "Verifica Preliminare Shape".
		"""
		try:
			# initialize msg variable
			global checkerr_pre
			checkerr_pre = 0
			global check_ok
			check_ok = 0
			global msg_err_tot
			msg_err_tot = ""
			global shape_path
			shape_path = str_path_shape.get()
			# set main shape variables
			global sf
			global shapes
			global shapes_geometry
			global num_shape
			# make_error(0) # da attivare solo in caso di test per generare un errore voluto
			# try...except with pass for every function to skip error and go on

			try:
				sf = shapefile.Reader(shape_path)
			except:
				# ERRORE 01
				tkinter.messagebox.showerror(msg_title_error, "ERRORE 01 - Si e' verificato un errore "
											"nel caricamento dello shapefile \n La procedura termina "
											"\n\n Descrizione dell'errore: \n "
											 + str(sys.exc_info()[0]) + "\n"
											 + str(sys.exc_info()[1]) + msg_err_function)
				checkerr_pre = 2
				sys.exit()
			shapes = sf.shapeRecords()
			shapes_geometry = sf.shapes()
			num_shape = len(shapes)  # get number of features to manage loop and check order

			# check if shapefile fields match SSAP specification and exit to collect information about errors
			try:
				check_flds_shape_ssap(sf)
			except:
				print(return_line_code_number(), "Errore")  # Per rintracciare la linea di codice con errore tramite IDLE
				pass

			try:
				#ERRORE 02
				if chk_fld_datgeo == 0:  # test ok v.116_161
					msg_err_tot += msg_err_fld_datgeo
					checkerr_pre = 1
				elif chk_fld_datgeo == 1:
					check_ok = 1
					# count layers for .dat,.fld and .svr file
					global count_feat_dat_fld, count_feat_svr, count_feat_sin
					count_feat_dat_fld, count_feat_svr, count_feat_sin = count_feat_ssap(sf, num_shape)  # test ok
			except:
				print(return_line_code_number(), "Errore")  # Per rintracciare la linea di codice con errore tramite IDLE
				pass

			# ERRORE 03: check if attribute of SSAP field is correct
			try:
				if check_field_ssap(sf, num_shape):  # test ok ver 116_161
					msg_err_tot += msg_err_shape_fields_ssap
					checkerr_pre = 1
			except:
				print(return_line_code_number(), "Errore")  # Per rintracciare la linea di codice con errore tramite IDLE
				pass

			# ERRORE 04: check if shape type is polyline and exit if not
			try:
				if check_shape_type(shapes_geometry):  # test ok v.116_161
					msg_err_tot += msg_err_shape_type
					checkerr_pre = 1
					sys.exit()
			except:
				print(return_line_code_number(), "Errore")  # Per rintracciare la linea di codice con errore tramite IDLE
				pass

			# ERRORE 05: check SSAP limit number of layers
			try:
				if check_layers_number(sf, num_shape, "dat", 20):  # test ok ver 113_161
					msg_err_tot += msg_err_layer_num
					checkerr_pre = 1
				if check_layers_number(sf, num_shape, "svr", 10):  # test ok ver 113_161
					msg_err_tot += msg_err_layer_num
					checkerr_pre = 1
				if check_layers_number(sf, num_shape, "fld", 1):  # test ok
					msg_err_tot += msg_err_layer_num
					checkerr_pre = 1
				if check_layers_number(sf, num_shape, "sin", 1):  # test ok
					msg_err_tot += msg_err_layer_num
					checkerr_pre = 1
			except:
				print(return_line_code_number(), "Errore")  # Per rintracciare la linea di codice con errore tramite IDLE
				pass

			# ERRORE 06: check SSAP limit number of points
			try:
				if check_points_number(sf, num_shape):
					msg_err_tot += msg_err_points_number
					checkerr_pre = 1
			except:
				print(return_line_code_number(), "Errore")  # Per rintracciare la linea di codice con errore tramite IDLE
				pass

			# ERRORE 07: check id = 0 for no fld field
			try:
				if check_id_zero(sf, num_shape):  # test ok ver 116_161
					msg_err_tot += msg_err_id_zero
					checkerr_pre = 1
			except:
				print(return_line_code_number(), "Errore")  # Per rintracciare la linea di codice con errore tramite IDLE
				pass

			# ERRORE 08: check that all points have positive coordinate
			try:
				if check_all_negative_val(sf, num_shape):
					msg_err_tot = msg_err_tot + msg_err_negative_val
					checkerr_pre = 1
			except:
				print(return_line_code_number(), "Errore")  # Per rintracciare la linea di codice con errore tramite IDLE
				pass

			# ERRORE 09: check that topographic hasn't jut
			try:
				if check_jutting_surface(sf, num_shape):
					msg_err_tot += msg_err_jutting_surface
					checkerr_pre = 1
			except:
				print(return_line_code_number(), "Errore")  # Per rintracciare la linea di codice con errore tramite IDLE
				pass

			# ERRORE 10: check if ID is continuous for "dat" record
			try:
				if count_feat_dat_fld > 0:
					if check_continuous_order(sf, num_shape, "dat"):  # test ok
						msg_err_tot += msg_err_continuous_order
						checkerr_pre = 1

				# check if ID is continuous for "svr"" record
				if count_feat_svr > 0:
					if check_continuous_order(sf, num_shape, "svr"):
						msg_err_tot = msg_err_tot + msg_err_continuous_order
						checkerr_pre = 1
			except:
				print(return_line_code_number(), "Errore")  # Per rintracciare la linea di codice con errore tramite IDLE
				pass

			# ERRORE 11: Check if order from top to bottom is correct
			try:
				if CheckTopBottomOrder.get() == 1:
					if check_top_bottom_order(sf, count_feat_dat_fld):
						msg_err_tot += msg_err_topdown_order
						checkerr_pre = 1
			except:
				print(return_line_code_number(), "Errore")  # Per rintracciare la linea di codice con errore tramite IDLE
				pass

			if check_ok == 1 and pass_check == 1:
				tkinter.messagebox.showinfo(msg_title_check, "##### Shapefile: '" + shape_path + "'\n\n" + msg_ok_fld_ssap)
			if checkerr_pre == 1:
				sys.exit()
		except:
			if checkerr_pre == 1:
				if len(msg_err_tot) > int(max_char_msg_err):
					msg_err_tot = msg_err_tot[:int(max_char_msg_err)] + ".......\n"
				tkinter.messagebox.showerror(msg_title_error, "##### Shapefile: '" + str_path_shape.get() + "'\n" +
											 "##### Sono stati riscontrati errori nella conversione ai file per SSAP: \n"
											 + msg_err_tot + msg_err_end)
			# gestisce le condzioni note e genera un messaggio di errore solo per situazioni ignote
			elif check_ok == 1 and pass_check == 1:
				pass
			elif checkerr_pre == 2:
				print(return_line_code_number())
				pass
			else:
				default_msg_unknow_error("check_function")

			# ######## Main Function #########


	def shp_2_ssap_files():
		"""
		Funzione principale di creazione dei file .dat, .geo, .fld, sin. e .mod
		Richiama le funzioni di controllo tramite gestione errori unica
		"""
		try:
			# cond_write_mod_file flag to handle writing of .mod file
			# 1 = delete .dat, .geo e mod,
			# 2 = delete .fld,
			# 3 (2+1) = delete .dat, .geo, .mod e .fld,
			# 4 = delete .svr,
			# 5 (1+4) = delete .dat, .geo, .mod.,svr,
			# 7 (1+2+4) = delete .dat, .geo, .mod,.fld, .svr
			global my_ssap_files_list
			my_ssap_files_list = []
			global cond_write_mod_file
			cond_write_mod_file = 0
			global checkerr_run
			checkerr_run = 0
			t = datetime.datetime.now()
			t2 = t.strftime("%A, %d. %B %Y %I:%M%p")
			t2 = "File creato in data: " + str(t2)
			# invoca la funzione di controllo check_function con parametro 0 in modo da non mostrare i messaggi di informazione
			# verifica se sono stati intercettati errori e nel caso esce dalla procedura evitando l'eccezione della funzione corrente
			check_function(0)
			if checkerr_pre == 1:
				sys.exit()
			# richiama la variabile per la creazione dei messaggi di errore e la azzera
			# DOPO l'esecuzione della funzione check_function
			global msg_err_end
			msg_err_end = ""
			global msg_err_tot
			msg_err_tot = ""
			if not os.path.exists(shape_path):
				checkerr_run = 1
				msg_err_tot = "Non e' stato selezionato lo shapefile di Input o lo shapefile indicato non esiste \t \n"
				sys.exit()
			count_feat_dat_fld, count_feat_svr, count_feat_sin = count_feat_ssap(sf, num_shape)
			# SSAP file pathname
			ssap_pathname = str_path_ssap.get()
			# last exit for error input, ordinary way use active_disable_button()
			if not os.path.isdir(os.path.dirname(ssap_pathname)):
				checkerr_run = 1
				msg_err_tot = "- Non e' stato indicato il nome dei file SSAP di output \t \n"
				msg_err_end = "\n ##### Indicare il nome dei file SSAP di output e ripetere la procedura \t"
				sys.exit()
			# ###start to process data file
			# get topographic limit coordinate to manage trimming of layers
			global x_min_topo, x_max_topo, xlength_topo, xlenght_tolerance
			x_min_topo, x_max_topo = xtopo(num_shape, sf)  # test ok
			xlength_topo = round(x_max_topo - x_min_topo, 2)
			xlenght_tolerance = round(xlength_topo / trim_tolerance_factor, 2)
			# create all SSAP file - someone will be empty
			f_dat = open(ssap_pathname + ".dat", "w+")
			my_ssap_files_list.append(f_dat.name)
			f_geo = open(ssap_pathname + ".geo", "w+")
			f_mod = open(ssap_pathname + ".mod", "w+")
			cond_write_mod_file = 1
			my_ssap_files_list.append(f_geo.name)
			my_ssap_files_list.append(f_mod.name)
			# write header of .dat file
			f_dat.write(chr(124) + t2 + "\n")
			f_dat.write(chr(124) + "File .dat per SSAP2010 generato da fromshp2ssap.py, versione " + ver_msg + "\n")
			f_dat.write(chr(124) + "Shapefile di input: '" + str_path_shape.get() + "'. Numero di strati: " + str(
				num_shape) + ". \n")
			# print function is useful to show running code result in cmd shell or in phyton shell
			print("fromshp2ssap.py\n" + "Coordinate estratte da Shapefile " + str_path_shape.get() + " e convertite in formato .dat:\n")
			# counter for while loop and reorder shape drawing not order (id field <> id object)
			main_counter = 0  # main counter
			d_mc = main_counter  # duplicate counter get from main counter to manage loop (with re_loop_counter variable)
			re_loop_counter = 0  # counter to re-loop when if condition is false
			c = 0  # variable to manage ID = 0 for write .fld file

			# main loop: read shapefile and get geometry layers and points for .dat and .fld file, get attribute for .geo file
			while main_counter < count_feat_dat_fld:
				# write polyline only when id field = main_counter counter
				# x value of first point of the shape
				x_min = sf.shapeRecord(d_mc).shape.points[0][0]
				# y value of first point of the shape
				y_min = round(sf.shapeRecord(d_mc).shape.points[0][1], 2)
				# x value of the last point of shape
				x_max = sf.shapeRecord(d_mc).shape.points[-1][0]
				# y value of last point of the shape
				y_max = round(sf.shapeRecord(d_mc).shape.points[-1][1], 2)
				# x e y value to create line equation for trimming
				x_ref1, x_ref2, y_ref1, y_ref2 = xy_ref(sf.shapeRecord(d_mc))
				print(return_line_code_number(), x_min, x_max)
				if ((sf.shapeRecord(d_mc).record[id_ssap].casefold()) == "dat"
					and (sf.shapeRecord(d_mc).record[id_ssap_id]) == (main_counter + 1)
					and sf.shapeRecord(d_mc).record[id_exclude] != 1):
					num_pts = len(sf.shapeRecord(d_mc).shape.points)
					# write data layer in .geo file
					if chk_fld_rock == 0 or (chk_fld_rock == 1 and (sf.shapeRecord(d_mc).record[id_sigci]) == 0):
						if (sf.shapeRecord(d_mc).record[id_dr_undr].casefold()) != "u":
							f_geo.write("\t" + str(sf.shapeRecord(d_mc).record[id_phi]))
							f_geo.write("\t" + str(sf.shapeRecord(d_mc).record[id_c]))
							f_geo.write("\t" + str(0))
						elif (sf.shapeRecord(d_mc).record[id_dr_undr].casefold()) == "u":
							if check_cu_value(sf.shapeRecord(d_mc).record[id_cu], sf.shapeRecord(d_mc).record[id_ssap_id]):
								msg_err_tot +=  msg_err_cu_value
								checkerr_run = 1
							else:
								f_geo.write("\t" + str(0))
								f_geo.write("\t" + str(0))
								f_geo.write("\t" + str(sf.shapeRecord(d_mc).record[id_cu]))
						f_geo.write("\t" + str(sf.shapeRecord(d_mc).record[id_gamma]))
						f_geo.write("\t" + str(sf.shapeRecord(d_mc).record[id_gammasat]) + "\n")
					elif chk_fld_rock == 1 and (sf.shapeRecord(d_mc).record[id_sigci]) > 0:
						f_geo.write("\t" + str(0))
						f_geo.write("\t" + str(0))
						f_geo.write("\t" + str(0))
						f_geo.write("\t" + str(sf.shapeRecord(d_mc).record[id_gamma]))
						f_geo.write("\t" + str(sf.shapeRecord(d_mc).record[id_gammasat]))
						f_geo.write("\t" + str(sf.shapeRecord(d_mc).record[id_sigci]))
						f_geo.write("\t" + str(sf.shapeRecord(d_mc).record[id_gsi]))
						f_geo.write("\t" + str(sf.shapeRecord(d_mc).record[id_mi]))
						f_geo.write("\t" + str(sf.shapeRecord(d_mc).record[id_d]) + "\n")
					# end write data layer in .geo file

					# write header layer of .dat file
					f_dat.write("##" + str(sf.shapeRecord(d_mc).record[id_ssap_id])
								+ "-------------------------- Numero punti: " + str(num_pts) + "\n")
					# print to show on shell
					print("##" + str(sf.shapeRecord(d_mc).record[id_ssap_id]) + "--------------------------\n")
					# loop to write x,y coordinate of layers points in .dat file
					for k in sf.shapeRecord(d_mc).shape.points:
						# layer trimming for geo/dat layer
						if check_trimming.get() == 1:
							if k[0] < (x_min_topo + xlenght_tolerance):  # x a sinistra del limte topografico + tolleranza
								if k[0] == x_min:  #
									var_x = x_min_topo
									if x_min == x_min_topo:
										var_y = k[1]
									else:
										if global_points_counter > 0:
											var_y = get_y_trim_bound(x_ref1, x_min, y_ref1, y_min, x_min_topo)
										else:
											var_y = get_y_trim_bound(x_ref2, x_min, y_ref2, y_min, x_min_topo)
								else:
									continue
							elif k[0] > (x_max_topo - xlenght_tolerance):
								if k[0] == x_max:
									var_x = x_max_topo
									if x_max == x_max_topo:
										var_y = k[1]
									else:
										if global_points_counter > 0:
											var_y = get_y_trim_bound(x_ref2, x_max, y_ref2, y_max, x_max_topo)
										else:
											var_y = get_y_trim_bound(x_ref1, x_max, y_ref1, y_max, x_max_topo)
								else:
									continue
							else:
								var_x = k[0]
								var_y = k[1]
						else:
							var_x = k[0]
							var_y = k[1]
						# end trimming for geo/dat layer
						# write x, y coordinate rounded to first decimal
						f_dat.write("\t" + format_float_str(var_x) + "\t\t")  # write x coordinate
						f_dat.write(format_float_str(var_y) + "\n")  # write y coordinate
						# print to show shell
						print(return_line_code_number(), "\t" + format_float_str(var_x) + "\t",
							  format_float_str(var_y) + "\n")
					# manage counter
					main_counter += 1
					d_mc = main_counter - re_loop_counter
					if d_mc < 0:
						d_mc = 0  # negative id object not exist

				# ###### start write .fld file #######
				elif (sf.shapeRecord(d_mc).record[id_ssap].casefold() == "fld"
					and sf.shapeRecord(d_mc).record[id_ssap_id] == c
					and sf.shapeRecord(d_mc).record[id_exclude] != 1):
					f_fld = open(ssap_pathname + ".fld", "w+")
					my_ssap_files_list.append(f_fld.name)
					for k in sf.shapeRecord(d_mc).shape.points:
						# layer trimming for fld layer
						if check_trimming.get() == 1:
							if k[0] < (x_min_topo + xlenght_tolerance):  # se x cade a sinistra del limite topografico
								if k[0] == x_min:
									var_x = x_min_topo
									if x_min == x_min_topo:
										var_y = k[1]
									else:
										if global_points_counter > 0:
											var_y = get_y_trim_bound(x_ref1, x_min, y_ref1, y_min, x_min_topo)
										else:
											var_y = get_y_trim_bound(x_ref2, x_min, y_ref2, y_min, x_min_topo)
								else:
									continue
							elif k[0] > (x_max_topo - xlenght_tolerance):  # se x cade a destra del limite topografico
								if k[0] == x_max:
									var_x = x_max_topo
									if x_max == x_max_topo:
										var_y = k[1]
									else:
										if global_points_counter > 0:
											var_y = get_y_trim_bound(x_ref2, x_max, y_ref2, y_max, x_max_topo)
										else:
											var_y = get_y_trim_bound(x_ref1, x_max, y_ref1, y_max, x_max_topo)
								else:
									continue
							else:
								var_x = k[0]
								var_y = k[1]
						else:
							var_x = k[0]
							var_y = k[1]
						# end trimming for fld layer
						f_fld.write("\t" + format_float_str(var_x) + "\t\t")  # write x coordinate
						f_fld.write(format_float_str(var_y) + "\n")  # write y coordinate
					f_fld.close()
					# new c value to skip if condition about .fld file (no id value > num shape is admitted)
					c = count_feat_dat_fld + 1
					# new limit of loop - no need to manage counter
					count_feat_dat_fld -= 1
					cond_write_mod_file += 2
				# #######end .fld code#######
				else:
					d_mc += 1
					re_loop_counter += 1
					continue

			# ###### start .svr code ######
			# ###no trimming because overload are always inside topographic limits#
			# check if svr layer exist and if exist set counter
			if count_feat_svr > 0 and chk_fld_svr == 1:
				f_svr = open(ssap_pathname + ".svr", "w+")
				my_ssap_files_list.append(f_svr.name)
				svr_counter = 0  # main counter
				d_mc_svr = svr_counter  # duplicate counter get from main counter to manage loop (with re_loop_counter variable)
				re_loop_counter_svr = 0  # counter to re-loop when if condition is false
				# loop: read shapefile and get geometry layers and points for .svr
				while svr_counter < count_feat_svr:

					# write polyline only when id field = mc counter
					if ((sf.shapeRecord(d_mc_svr).record[id_ssap].casefold()) == "svr"
						and (sf.shapeRecord(d_mc_svr).record[id_ssap_id]) == (svr_counter + 1)
						and sf.shapeRecord(d_mc_svr).record[id_exclude] != 1):
						# write x min e x max coordinate in .svr file
						var_x_min = sf.shapeRecord(d_mc_svr).shape.points[0][0]
						var_x_max = sf.shapeRecord(d_mc_svr).shape.points[-1][0]
						f_svr.write(format_float_str(var_x_min) + "\t")  # write x coordinate
						f_svr.write(format_float_str(var_x_max) + "\t")  # write x coordinate
						f_svr.write(format_float_str(sf.shapeRecord(d_mc_svr).record[id_val1]) + "\n")
						svr_counter += 1
						d_mc_svr = svr_counter - re_loop_counter_svr
						if d_mc_svr < 0:
							d_mc_svr = 0  # negative id object not exist
					else:
						d_mc_svr += 1
						re_loop_counter_svr += 1
						continue
				f_svr.close()
				cond_write_mod_file += 4
			# ###### end .svr code ######

			# ###### start .sin code ######
			# ###no trimming because landslide surface have to be  always inside topographic limits#
			# check if sin layer exist and if exist set counter
			if count_feat_sin > 0:
				print("creo file .sin")
				f_sin = open(ssap_pathname + ".sin", "w+")
				my_ssap_files_list.append(f_sin.name)
				f_sin.write("# " + py_file + "- versione: " + versione + "\n")
				f_sin.write("# file " + ssap_pathname + ".sin creato da Shapefile di input: '"
							+ str_path_shape.get() + "\n")
				sin_counter = 0  # main counter
				d_mc_sin = sin_counter  # duplicate counter get from main counter to manage loop (with re_loop_counter variable)
				re_loop_counter_sin = 0  # counter to re-loop when if condition is false
				# loop: read shapefile and get geometry layers and points for .svr
				while sin_counter < count_feat_sin:
					# write polyline only when id field = mc counter
					if sf.shapeRecord(d_mc_sin).record[id_ssap].casefold() == "sin":
						# loop to write x,y coordinate of layers points in .dat file
						for k in sf.shapeRecord(d_mc_sin).shape.points:
							var_x = k[0]
							var_y = k[1]
							f_sin.write("\t" + format_float_str(var_x) + "\t\t")  # write x coordinate
							f_sin.write(format_float_str(var_y) + "\n")  # write y coordinate
						sin_counter += 1
						d_mc_sin = sin_counter - re_loop_counter_sin
						if d_mc_sin < 0:
							d_mc_sin = 0  # negative id object not exist
					else:
						d_mc_sin += 1
						re_loop_counter_sin += 1
						continue
				f_sin.close()
			# ###### end .sin code ######

			f_dat.close()
			f_geo.close()
			# ##### end .dat e .geo code ######

			# write .mod file checking cond_write_mod_file variable
			if cond_write_mod_file == 7:
				f_mod.write(str(count_feat_dat_fld) + "    1    1    0    0    0" + "\n")
				f_mod.write(
					(os.path.basename(f_dat.name)) + "\n" + os.path.basename(f_fld.name) + "\n"
					+ os.path.basename(f_geo.name) + "\n" +
					os.path.basename(f_svr.name))
			elif cond_write_mod_file == 5:
				f_mod.write(str(count_feat_dat_fld) + "    0    1    0    0    0" + "\n")
				f_mod.write((os.path.basename(f_dat.name)) + "\n"
							+ os.path.basename(f_geo.name) + "\n" + os.path.basename(f_svr.name))
			elif cond_write_mod_file == 3:
				f_mod.write(str(count_feat_dat_fld) + "    1    0    0    0    0" + "\n")
				f_mod.write((os.path.basename(f_dat.name)) + "\n" + os.path.basename(f_fld.name)
							+ "\n" + os.path.basename(f_geo.name))
			elif cond_write_mod_file == 1:
				f_mod.write(str(count_feat_dat_fld) + "    0    0    0    0    0" + "\n")
				f_mod.write(os.path.basename(f_dat.name) + "\n" + os.path.basename(f_geo.name))

			f_mod.close()
			# ##### end .mod code #####

			if checkerr_run == 1:
				remove_all_file(my_ssap_files_list)
				sys.exit()
			elif checkerr_run == 0 and checkerr_pre == 0:
				tkinter.messagebox.showinfo(msg_title, "Procedura conclusa. Sono stati creati i file SSAP: \n" + str(
					my_ssap_files_list) + "\n")
			else:
				sys.exit()

		# just a default except to handle error, there are two main type error:
		# SSAP type (checkerr_pre=1) and system error (checkerr_pre = 0), in system error
		# specific error are handled by type default_msg_unknow_error function that return system error
		# and name of function that catch error

		except:
			if checkerr_run == 0 and checkerr_pre == 0:
				tkinter.messagebox.showerror(msg_title_error, "Si e' verificato un errore!\n"
											 + "La procedura termina \n\n Descrizione dell'errore: \n"
											 + str(sys.exc_info()[0]) + "\n"
											 + str(	sys.exc_info()[1]) + msg_err_function)
			elif checkerr_run == 1:
				if len(msg_err_tot) > int(max_char_msg_err):
					msg_err_tot = msg_err_tot[:int(max_char_msg_err)] + ".......\n\n"
				tkinter.messagebox.showerror(msg_title_error, "##### Shapefile: '" + str_path_shape.get() + "'\n" +
											 "##### Sono stati riscontrati errori nella conversione ai file per SSAP: " +
											 "\n\n" + msg_err_tot + msg_err_end)
			elif checkerr_pre == 1:
				pass


	############## - Utility Function  for SSAP code - ##############


	def make_error(flag):
		"""
		Genero un errore di divisione per zero
		serve a verificare le istruzioni in except
		"""
		a = 0
		if flag == 1:
			a = 1 / 0
		else:
			pass
		return a


	def return_line_code_number():
		"""
		Returns the current line number in this code
		"""
		return "Code line number: " + str(inspect.currentframe().f_back.f_lineno) + "\t"


	def remove_all_file(xfileslist):
		try:
			# result = tkinter.messagebox.askyesno(msg_title_error,"eliminare tutti i file \n"
			# 									+ "presenti nella directory  ?")

			for f in xfileslist:
				if os.path.exists(f):
					os.remove(f)
		except:
			default_msg_unknow_error("remove_all_file")


	def format_float_str(float_coord):
		try:
			coord_format = "{0:.2f}".format(round(float_coord, 2))
			return coord_format
		except:
			default_msg_unknow_error("format_float_string")


	############## - check file for SSAP code - ##############
	def default_msg_unknow_error(function_name):
		"""
		Creazione messaggio di errore personalizzato per singola funzione (arg function_name)
		Rimanda all'except della funzione principale Shp_2_SSAP_Files()
		"""
		global msg_err_function
		msg_err_function = ""
		msg_err_function = ("\n Errore generato dalla funzione:  '" + function_name + "'\n")


	def check_all_negative_val(my_shape, layer_num):
		global msg_err_negative_val
		msg_err_negative_val = ""
		try:
			f = 0
			while f < layer_num:
				for k in my_shape.shapeRecord(f).shape.points:
					if (k[0] < 0) or (k[1] < 0):
						msg_err_negative_val += ("- Nello  strato '"
												 + str(sf.shapeRecord(f).record[id_ssap]) + "' con ID = "
												 + str(sf.shapeRecord(f).record[id_ssap_id])
												 + ". x=" + format_float_str(k[0])
												 + ", y=" + format_float_str(k[1]) + "\t\n")

				f += 1
			if len(msg_err_negative_val) > 0:
				msg_err_negative_val = "\n ERRORE 08: Presenti coordinate con valori negativi:\n" + msg_err_negative_val
				return True
			else:
				return False
		except:
			default_msg_unknow_error("check_all_negative_val")


	def check_jutting_surface(my_shape, layer_num):
		global msg_err_jutting_surface
		msg_err_jutting_surface = ""
		try:
			f = 0
			mylist = []
			while f < layer_num:
				for k in my_shape.shapeRecord(f).shape.points:
					if sf.shapeRecord(f).record[id_ssap].casefold() == "dat" \
							and sf.shapeRecord(f).record[id_ssap_id] == 1:
						mylist.append(k[0])
				f += 1

			for a in mylist:
				# verifica che l'indice non superi il limite superiore della lista
				if mylist.index(a) + 1 < len(mylist):
					# confronta il valore x n-esimo con il successivo della lista
					if mylist[mylist.index(a)] > mylist[mylist.index(a) + 1]:
						msg_err_jutting_surface = \
							("\nERRORE 09: la superficie topografica presenta una forma aggettante\n")

			if len(msg_err_jutting_surface) > 0:
				return True
			else:
				return False

		except:
			default_msg_unknow_error("check_jutting_surface")


	def check_points_number(my_shape, layer_num):
		"""
		Verifica il numero totale di punti di ogni strato in riferimento allo standard SSAP
		Funzione richiamata dalla funzione check_function()
		"""
		global msg_err_points_number
		msg_err_points_number = ""
		try:
			f = 0
			while f < layer_num:
				if (len(my_shape.shapeRecord(f).shape.points)) > 100:
					msg_err_points_number += ("- Strato '" + str(sf.shapeRecord(f).record[id_ssap])
											  + "' con ID = " + str(sf.shapeRecord(f).record[id_ssap_id])
											  + " conta " + str((len(my_shape.shapeRecord(f).shape.points)))
											  + " punti.\n")
				f += 1

			if len(msg_err_points_number) > 0:
				msg_err_points_number = "\nERRORE 06: Presenti strati con numero di punti > 100 limite massimo per SSAP:\n" \
										+ msg_err_points_number
				return True
			else:
				return False
		except:
			default_msg_unknow_error("check_points_number")


	def check_layers_number(my_shape, layer_num, type_ssap, max_num):
		"""
		Verifica il numero totale di strati in riferimento allo standard SSAP
		Funzione richiamata dalla funzione principale Shp_2_SSAP_Files()
		"""
		try:
			f = 0
			type_ssap_num = 0
			while f < layer_num:
				if my_shape.shapeRecord(f).record[id_ssap].casefold() == type_ssap:
					type_ssap_num += 1
				f += 1
			if type_ssap_num > max_num:
				global msg_err_layer_num
				msg_err_layer_num = ""
				msg_err_layer_num = ("\n ERRORE 05: Il numero di strati '" + type_ssap + "' nello shapefile "
									 + " e' pari a " + str(type_ssap_num) + ", superiore a " + str(max_num)
									 + ", limite ammesso da SSAP.\n")
				return True
			else:
				return False

		except:
			default_msg_unknow_error("check_layers_number")


	def check_top_bottom_order(xsf, xcount_feat):
		"""
		Verifica che gli strati di input abbiano indici ordinati dall'alto verso il basso
		Si tratta di una verifica di tipo geometrico (basata sui valori delle coordinate di y) diversa dalla
		verifica della funzione check_continuous_order che si basa sui valori degli indici e non e' in grado
		di discriminare eventuali incongruenze geometriche.
		Funzione richiamata dalla funzione principale shp_2_ssap_files()
		"""
		try:
			# counter for while loop and reorder shape drawing not order (id field <> id object)
			main_counter = 0  # main counter
			d_mc = main_counter  # duplicate counter get from main counter to manage loop (with re_loop_counter variable)
			re_loop_counter = 0  # counter to re-loop when if condition is false

			# list to manage layer error
			list_check_topdown = []
			my_topdown_list_min = []
			my_topdown_list_max = []
			my_topdown_list_centroid = []

			while main_counter < xcount_feat - 1:
				if xsf.shapeRecord(d_mc).record[id_ssap].casefold() == "dat" \
						and xsf.shapeRecord(d_mc).record[id_ssap_id] == main_counter + 1 \
						and xsf.shapeRecord(d_mc).record[id_exclude] != 1:
					# loop to write x,y coordinate of layers points in .dat file
					for k in xsf.shapeRecord(d_mc).shape.points:
						# append all y value in list to check correct id order topdown
						list_check_topdown.append(round(k[1], 2))
					# get min, max and geometric centroid value of y value from points of any layer
					my_ysum = 0
					for my_yval in list_check_topdown:
						my_ysum += my_yval
					my_ycentroid = round(my_ysum / len(list_check_topdown), 2)
					list_check_topdown.sort()
					my_ymin = list_check_topdown[0]
					my_ymax = list_check_topdown[-1]
					my_topdown_list_min.append(my_ymin)
					my_topdown_list_max.append(my_ymax)
					my_topdown_list_centroid.append(my_ycentroid)
					list_check_topdown = []
					# manage counter
					main_counter += 1
					d_mc = main_counter - re_loop_counter
					if d_mc < 0:
						d_mc = 0  # negative id object not exist
				else:
					d_mc += 1
					re_loop_counter += 1
					continue
			myorderlist_min = my_topdown_list_min[:]
			myorderlist_min.sort()
			myorderlist_min.reverse()
			myorderlist_max = my_topdown_list_max[:]
			myorderlist_max.sort()
			myorderlist_max.reverse()
			myorderlist_centroid = my_topdown_list_centroid[:]
			myorderlist_centroid.sort()
			myorderlist_centroid.reverse()

			if (my_topdown_list_min != myorderlist_min) \
					and (my_topdown_list_max != myorderlist_max) \
					and (my_topdown_list_centroid != myorderlist_centroid):
				global msg_err_topdown_order
				msg_err_topdown_order = ""
				msg_err_topdown_order = (
				"\n ERRORE 11: Possibili problemi con l'ordinamento verticale dei valori ssap_id per i layer 'dat'.\n "
				+ "Attenzione: per modelli complessi sono possibili false segnalazioni di errore. "
				+ "In tal caso riprovare escludendo la 'verifica ordinamento verticale strati'\n")
				return True
			else:
				return False
		except:
			default_msg_unknow_error("check_top_bottom_order")


	def check_continuous_order(my_shape, layer_num, type_ssap):
		"""
		Verifica che gli strati di input abbiano indici continui.
		Si tratta di una verifica di tipo formale sui valori degli indici
		non e' possibile discriminare eventuali incongruenze geometriche.
		Funzione richiamata dalla funzione principale Shp_2_SSAP_Files()
		"""
		try:
			global msg_err_continuous_order
			msg_err_continuous_order = ""
			f = 0
			tot_shape = layer_num  # copy num_shape
			# create list for id value
			id_list = []
			# create list for x value
			x_value_topo = []
			while f < layer_num:
				# get id value
				if (my_shape.shapeRecord(f).record[id_ssap].casefold() == type_ssap) and (
					my_shape.shapeRecord(f).record[id_exclude] != 1):
					id_list.append(my_shape.shapeRecord(f).record[id_ssap_id])
				f += 1
			# manage list of id value
			id_list_ordered = id_list[:]
			id_list_ordered.sort()
			perfectorder = []
			if id_list_ordered[0] == 0:
				perfectorder = list(range(0, len(id_list)))
			elif id_list_ordered[0] == 1:
				perfectorder = list(range(1, len(id_list) + 1))
			if (id_list_ordered != perfectorder):
				msg_err_continuous_order = (
				"\n ERRORE 10: Problemi con la seguenza del campo indice delle polyline nello shapefile. "
				+ "Per i layer '" + type_ssap + "' la seguenza degli indici ordinata e' errata: " + str(
					id_list_ordered) + "\n")
				return True
			else:
				return False
		except:
			default_msg_unknow_error("check_continuous_order")


	def check_id_zero(my_shape, layer_num):
		"""
		Verifica che gli strati di input non abbiano indice = 0, indice ammesso solo per lo strato falda
		Funzione richiamata dalla funzione principale Shp_2_SSAP_Files()
		"""
		try:
			global msg_err_id_zero
			msg_err_id_zero = ""
			f = 0
			while f < layer_num:
				if my_shape.shapeRecord(f).record[id_ssap].casefold() != "fld":
					if my_shape.shapeRecord(f).record[id_ssap_id] == 0:
						msg_err_id_zero += (
						"\n ERRORE 07: presente uno strato SSAP = " + str(my_shape.shapeRecord(f).record[id_ssap])
						+ ", con ID = 0, diverso dallo strato .fld unico ammesso con indice 0. \n")
				else:
					if my_shape.shapeRecord(f).record[id_ssap_id] != 0:
						msg_err_id_zero += (
						"\n ERRORE 07: lo strato 'fld' ha un SSAP_ID = " + str(my_shape.shapeRecord(f).record[id_ssap_id])
						+ ", per convenzione lo strato .fld deve sempre avere SSAP_ID = 0. \n")
				f += 1
			if len(msg_err_id_zero) > 0:
				return True
			else:
				print(return_line_code_number(), "check_id_zero")
				return False
		except:
			default_msg_unknow_error("check_id_zero")


	def check_shape_type(my_shapes):
		"""
		Verifica tipologia dello shapefile di input.
		Funzione richiamata dalla funzione principale Shp_2_SSAP_Files()
		"""
		try:
			global msg_err_shape_type
			msg_err_shape_type = ""
			if my_shapes[0].shapeType != 3:  # 3 = polyline type in ESRI specification
				msg_err_shape_type = "\n ERRORE 04: Lo shapefile non e' del tipo 'polyline'\n"
				return True
			else:
				return False
		except:
			default_msg_unknow_error("check_shape_type")


	def check_flds_shape_ssap(my_sf):
		"""
		Verifica dei campi necessari per creare i file ssap e assegnazione indice ai campi
		"""

		try:
			my_flds = my_sf.fields
			fld_set = set()

			fld_ssap_set_datgeo = {'SSAP_ID_N', 'SSAP_C', 'PHI_N', 'CU_N', 'C_N', 'GAMMA_N', 'GAMMASAT_N', 'EXCLUDE_N',
								   'DR_UNDR_C'}
			fld_ssap_set_svr = fld_ssap_set_datgeo.union({'VAL1_N'})
			fld_ssap_set_rock = fld_ssap_set_datgeo.union({'SIGCI_N', 'GSI_N', 'MI_N', 'D_N'})
			fld_ssap_set_other = fld_ssap_set_datgeo.union({'VAL2_N', 'VAL3_N', 'VAL4_N'})
			fld_ssap_set_tot = fld_ssap_set_datgeo.union({'SIGCI_N', 'GSI_N', 'MI_N', 'D_N', 'VAL1_N',
														  'VAL2_N', 'VAL3_N', 'VAL4_N'})

			global id_ssap_id
			global id_ssap
			global id_c
			global id_cu
			global id_phi
			global id_gamma
			global id_gammasat
			global id_sigci
			global id_gsi
			global id_mi
			global id_d
			global id_val1
			global id_val2
			global id_val3
			global id_val4
			global id_exclude
			global id_dr_undr
			id_ssap_id = 999
			id_ssap = 999
			id_c = 999
			id_cu = 999
			id_phi = 999
			id_gamma = 999
			id_gammasat = 999
			id_sigci = 999
			id_gsi = 999
			id_mi = 999
			id_d = 999
			id_val1 = 999
			id_val2 = 999
			id_val3 = 999
			id_val4 = 999
			id_exclude = 999
			id_dr_undr = 999

			global chk_fld_datgeo
			global chk_fld_rock
			global chk_fld_svr
			global chk_fld_other
			global chk_fld_tot
			chk_fld_rock = 0
			chk_fld_svr = 0
			chk_fld_datgeo = 0
			chk_fld_other = 0
			chk_fld_tot = 0

			global msg_err_fld_datgeo
			global msg_ok_fld_ssap
			msg_err_fld_datgeo = ""
			msg_ok_fld_ssap = ""

			for a in my_flds:
				b = str(a[0]) + "_" + str(a[1])
				fld_set.add(b)
				if a[0].upper() == "SSAP_ID":
					id_ssap_id = my_flds.index(a) - 1  # remove DeletionFlag Field
				elif a[0].upper() == "SSAP":
					id_ssap = my_flds.index(a) - 1
				elif a[0].upper() == "PHI":
					id_phi = my_flds.index(a) - 1
				elif a[0].upper() == "GAMMA":
					id_gamma = my_flds.index(a) - 1
				elif a[0].upper() == "GAMMASAT":
					id_gammasat = my_flds.index(a) - 1
				elif a[0].upper() == "C":
					id_c = my_flds.index(a) - 1
				elif a[0].upper() == "CU":
					id_cu = my_flds.index(a) - 1
				elif a[0].upper() == "VAL1":
					id_val1 = my_flds.index(a) - 1
				elif a[0].upper() == "SIGCI":
					id_sigci = my_flds.index(a) - 1
				elif a[0].upper() == "GSI":
					id_gsi = my_flds.index(a) - 1
				elif a[0].upper() == "MI":
					id_mi = my_flds.index(a) - 1
				elif a[0].upper() == "D":
					id_d = my_flds.index(a) - 1
				elif a[0].upper() == "VAL2":
					id_val2 = my_flds.index(a) - 1
				elif a[0].upper() == "VAL3":
					id_val3 = my_flds.index(a) - 1
				elif a[0].upper() == "VAL4":
					id_val4 = my_flds.index(a) - 1
				elif a[0].upper() == "EXCLUDE":
					id_exclude = my_flds.index(a) - 1
				elif a[0].upper() == "DR_UNDR":
					id_dr_undr = my_flds.index(a) - 1

				# function to build a string for fields error

			def str_lack_builder(lack_list):
				str_lack = ""
				list_str_lack_tot = []
				for a in lack_list:
					b = a[-1:]
					c = a[0:(len(a) - 2)]
					if b.casefold() == "c":
						str_lack = " (str)"
					else:
						str_lack = " (num)"
					str_lack = str(c) + str_lack
					list_str_lack_tot.append(str_lack)
				return str(list_str_lack_tot)

			lack_ssap_fld_tot = list(fld_ssap_set_tot - fld_set)
			lack_ssap_fld_tot.sort()

			ok_ssap_fld_tot = list(fld_ssap_set_tot & fld_set)
			ok_ssap_fld_tot.sort()

			lack_ssap_fld_datgeo = list(fld_ssap_set_datgeo - fld_set)
			lack_ssap_fld_datgeo.sort()

			lack_ssap_fld_rock = list(fld_ssap_set_rock - fld_set)
			lack_ssap_fld_rock.sort()

			lack_ssap_fld_svr = list(fld_ssap_set_svr - fld_set)
			lack_ssap_fld_svr.sort()

			lack_ssap_fld_other = list(fld_ssap_set_other - fld_set)
			lack_ssap_fld_other.sort()

			if fld_ssap_set_datgeo.issubset(fld_set) == FALSE:
				msg_err_fld_datgeo = ("\nERRORE 02: mancano i seguenti campi per i file per SSAP (configurazione base file .dat, .geo e .mod):"
				+ str_lack_builder(lack_ssap_fld_datgeo) + "\n")
				if len(ok_ssap_fld_tot) > 0:
					msg_ok_fld_ssap = ("\n- Sono presenti i seguenti campi per SSAP: "
									   + str_lack_builder(ok_ssap_fld_tot) + "\n")
					msg_err_fld_datgeo += msg_ok_fld_ssap
			else:
				chk_fld_datgeo = 1
				msg_ok_fld_ssap = ("- Sono presenti i campi per creare i file SSAP .dat, .geo e .mod \n"
								   + "- Sono stati assegnati gli indici \n \n"
								   + "- Complessivamente sono presenti i seguenti file SSAP: "
								   + str_lack_builder(ok_ssap_fld_tot) + "\n")
			if fld_ssap_set_svr.issubset(fld_set):
				chk_fld_svr = 1
				msg_ok_fld_ssap = ("- Sono presenti i campi per creare i file SSAP .dat, .geo, .svr e .mod \n" +
								   "- Sono stati assegnati gli indici \n \n" +
								   "- Complessivamente sono presenti i seguenti file SSAP: "
								   + str_lack_builder(ok_ssap_fld_tot) + "\n")
			if fld_ssap_set_rock.issubset(fld_set):
				chk_fld_rock = 1
				msg_ok_fld_ssap = ("- Sono presenti i campi per creare i file SSAP .dat, .geo per strati rocciosi e .mod \n" +
				"- Sono stati assegnati gli indici \n \n" +
				"- Complessivamente sono presenti i seguenti file SSAP: " + str_lack_builder(ok_ssap_fld_tot) + "\n")
			if fld_ssap_set_other.issubset(fld_set):
				chk_fld_other = 1
			if fld_ssap_set_tot.issubset(fld_set):
				msg_ok_fld_ssap = ("- Sono presenti i campi per creare i file SSAP .dat, .geo per strati rocciosi, .svr  e .mod \n" +
				"- Sono stati assegnati gli indici \n \n" +
				"- Complessivamente sono presenti i seguenti file SSAP: " + str_lack_builder(ok_ssap_fld_tot) + "\n")
		except:
			default_msg_unknow_error("check_flds_shape_ssap")


	def check_field_ssap(xsf, xshape_num):
		"""
		Verifica che gli attributi del campo SSAP siano corretti.
		Funzione richiamata dalla funzione principale Shp_2_SSAP_Files()
		"""
		try:
			global msg_err_shape_fields_ssap
			msg_err_shape_fields_ssap = ""
			a = 0
			xlist = []
			ssapset = {"dat", "fld", "svr", "sin"}
			while a < xshape_num:
				xlist.append(xsf.shapeRecord(a).record[id_ssap].casefold())
				a += 1
			print(return_line_code_number(), "test check_field_ssap " + str(xlist))
			xset = set(xlist)
			list_msg = list(xset - ssapset)
			# condizione per escludere uno strato dalla conversione

			if len(list_msg) > 0:
				msg_err_shape_fields_ssap += ("\nERRORE 03: Nel campo SSAP risultano presenti i seguenti valori errati o "
												 "incoerenti rispetto alle specifiche SSAP: " + str(list_msg) + "\n")
				return True
			else:
				return False
		except:
			default_msg_unknow_error("check_field_ssap")


	def count_feat_ssap(xsf, xshape_num):
		"""
		Conteggia il numero di feature per ogni tipo di file SSAP indicati nel campo relativo.
		Funzione richiamata dalla funzione principale Shp_2_SSAP_Files()
		"""
		try:
			xcount_dat_fld = 0
			xcount_svr = 0
			xcount_sin = 0
			a = 0
			while a < xshape_num:
				print(xsf.shapeRecord(a).record[id_exclude])
				if xsf.shapeRecord(a).record[id_exclude] != 1:
					if xsf.shapeRecord(a).record[id_ssap].casefold() == "dat" \
							or xsf.shapeRecord(a).record[id_ssap].casefold() == "fld":
						xcount_dat_fld += 1
					elif xsf.shapeRecord(a).record[id_ssap].casefold() == "svr":
						xcount_svr += 1
					elif xsf.shapeRecord(a).record[id_ssap].casefold() == "sin":
						xcount_sin += 1
				a += 1
			return xcount_dat_fld, xcount_svr, xcount_sin
		except:
			default_msg_unknow_error("count_feat_ssap")


	def check_cu_value(cu_value, layer_id):
		try:
			global msg_err_cu_value
			msg_err_cu_value = ""
			if cu_value == 0:
				msg_err_cu_value = ("- Il valore di CU dello strato " + str(layer_id)
									+ " e' zero, la verifica in condizioni non drenate non e' applicabile.\t\n")
				return True
			else:
				return False
		except:
			default_msg_unknow_error("check_cu_value")


	############## - function to manage layer trimming - ##############
	def xtopo(n_shp, shp):
		"""
		Restituisce i valori x massimi e minimi della
		superficie topografica
		"""
		try:
			var_x_min = 0
			var_x_max = 0
			f = 0
			while f < n_shp:
				if (shp.shapeRecord(f).record[id_ssap].casefold()) == "dat" and (shp.shapeRecord(f).record[id_ssap_id]) == (1):
					var_x_min = round(shp.shapeRecord(f).shape.points[0][0], 2)
					var_x_max = round(shp.shapeRecord(f).shape.points[-1][0], 2)
				f += 1
			return var_x_min, var_x_max
		except:
			default_msg_unknow_error("xtopo")


	def xy_ref(shp_rec):
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
				if k[0] > (x_min_topo + xlenght_tolerance) and k[0] < (x_max_topo - xlenght_tolerance):
					global_points_counter += 1
			for k in shp_rec.shape.points:
				if global_points_counter > 0:
					if k[0] > (x_min_topo + xlenght_tolerance) and k[0] < (x_max_topo - xlenght_tolerance):
						c += 1
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


	def get_y_trim_bound(x1, x2, y1, y2, var_x_topo):
		"""
		Restituisce il valore della y dell'n-esima superficie di strato
		corrispondente al valore x della superficie topografica giacente sulla retta
		congiugente due punti di riferimento.
		"""
		try:
			c = 0
			m = 0
			y = 0
			m = (y1 - y2) / (x1 - x2)  # coefficiente angolare y1-y2/x1-x2
			c = (x1 * y2 - x2 * y1) / (x1 - x2)  # intercetta ordinate x1*y1-x2*y1/x1-x2
			y = c + m * var_x_topo  # valore y da equazione retta conoscendo x superfcie topografica
			return y
		except:
			default_msg_unknow_error("get_y_trim_bound")

except:
	if checkerr_pre == 2:
		pass
	else:
		tkinter.messagebox.showerror(msg_title_error,
									 return_line_code_number() + "Si e' verificato un errore non previsto!\n"
									 + "La procedura termina \n\n Descrizione dell'errore: \n"
									 + str(sys.exc_info()[0]) + "\n" + str(sys.exc_info()[1])
									 + "\n" + msg_err_function + "\n\n Contattare l'autore: lorenzo.sulli@gmail.com")


# ############# - tkinter/ttk code - ###################


def load_shapefile():
	"""
	Funzione di caricamento degli sahpefile di input.
	Funzione richiamata dall'interfaccia tkinter
	"""
	try:
		# load default path value from default.txt file
		defpathshp = os.getcwd()+linecache.getline("default.txt", 2)
		print (defpathshp)
		defpathshp = defpathshp[:-1]  # remove /n special character
		print(defpathshp)
		str_path_shape.delete(0, END)
		if os.path.exists(defpathshp) == False:
			defpathshp = ""
		shp_name = tkinter.filedialog.askopenfilename(filetypes=(("Shapefile", "*.shp"), ("All files", "*.*")),
													  initialdir=defpathshp)
		str_path_shape.insert(10, shp_name)
		linecache.clearcache()
	except:
		default_msg_unknow_error("load_shapefile")


def save_files_ssap():
	"""
	Funzione di definzione dei file SSAP di output.
	Funzione richiamata dall'interfaccia tkinter
	"""
	try:
		defpathssap = os.getcwd()+linecache.getline("default.txt", 4)
		defpathssap = defpathssap[:-1]  # remove /n special character
		str_path_ssap.delete(0, END)
		if not os.path.exists(defpathssap):
			defpathssap = ""
		SSAP_name = tkinter.filedialog.asksaveasfilename(filetypes=(("SSAP FILES", "*.mod*"), ("All files", "*.*")),
														 initialdir=defpathssap)
		ssap_text_pathname = os.path.splitext(SSAP_name)[0]
		str_path_ssap.insert(10, ssap_text_pathname)
		linecache.clearcache()
	except:
		default_msg_unknow_error("save_files_ssap")


def active_disable_button(*args):
	"""
	active or disable button 'Converti' and 'Verifica' by input and output entry
	"""
	x = var1.get()
	y = var2.get()
	if os.path.exists(x):
		Ver_Button.configure(state='normal')
		if os.path.isdir(os.path.dirname(y)) and os.path.basename(y):
			Conv_Button.configure(state='normal')
	else:
		Conv_Button.configure(state='disabled')
		Ver_Button.configure(state='disabled')

try:
		root = tkinter.Tk()
		root.title("Conversione da polyline shapefile a file per SSAP - Versione: " + versione)
		master = ttk.Frame(root, padding="12 12 12 12")
		master.grid(column=0, row=0, sticky=(N, W, E, S))
		master.columnconfigure(0, weight=1)
		master.rowconfigure(0, weight=1)
		master['borderwidth'] = 2
		master['relief'] = 'sunken'
		# variable for trace method
		var1 = tkinter.StringVar(root)
		var2 = tkinter.StringVar(root)
		str_path_shape = tkinter.Entry(master, width=75, textvariable=var1)
		str_path_ssap = tkinter.Entry(master, width=75, textvariable=var2)
		str_path_shape.grid(row=0, column=1, sticky=(E, W))
		str_path_ssap.grid(row=1, column=1, sticky=(E, W))
		Button(master, text='Input Shapefile', command=load_shapefile).grid(row=0, column=0, sticky=(W, E), pady=4, padx=8)
		Button(master, text='Output SSAP files name', command=save_files_ssap).grid(row=1, column=0, sticky=(W, E), pady=4,
																																								padx=8)
		Button(master, text='Esci', command=master.quit).grid(row=9, column=1, sticky=E, pady=4)
		Ver_Button = Button(master, text='Verifica preliminare Shape', command=lambda: check_function(1))
		Ver_Button.grid(row=9, column=0, sticky=W, pady=4)
		Conv_Button = Button(master, text='Converti', command=shp_2_ssap_files)
		Conv_Button.grid(row=9, column=0, sticky=E, pady=4)
		Conv_Button.configure(state=DISABLED)
		Ver_Button.configure(state=DISABLED)
		var1.trace("w", active_disable_button)
		var2.trace("w", active_disable_button)
		s2 = ttk.Separator(master, orient=HORIZONTAL).grid(column=1, row=5, sticky=(E, W), pady=10)
		s3 = ttk.Separator(master, orient=HORIZONTAL).grid(column=0, row=8, sticky=(E, W), pady=10)
		s4 = ttk.Separator(master, orient=HORIZONTAL).grid(column=1, row=8, sticky=(E, W), pady=10)
		l1 = ttk.Label(master, text='  Opzioni controllo e creazioni strati', borderwidth=5, relief=GROOVE, foreground='black')
		l1.grid(column=0, row=5, pady=10, ipadx=10, ipady=5, sticky=(N + S))
		check_cu = IntVar()
		# c1 = Checkbutton(master, text = "Verifica in condizioni drenate, Cu=0", variable = check_cu, onvalue = 1,
		# 					offvalue = 0, height=1, width = 30)
		# c1.grid(row=3, column=0, sticky=(W))
		# c1.select()
		CheckTopBottomOrder = IntVar()
		c2 = Checkbutton(master, text="Verifica ordinamento verticale strati", variable=CheckTopBottomOrder,
										 onvalue=1, offvalue=0, height=1, width=30)
		c2.grid(row=6, column=0, sticky=W)
		c2.select()
		check_trimming = IntVar()
		c3 = Checkbutton(master, text="Regola gli strati alla superficie topografica", variable=check_trimming,
										 onvalue=1, offvalue=0, height=1, width=35)
		c3.grid(row=6, column=1, sticky=E)
		c3.select()
		root.mainloop()
except:
		tkinter.messagebox.showerror(msg_title_error,
									 return_line_code_number() + " Si e' verificato un errore non previsto!\n"
									 + "La procedura termina \n\n Descrizione dell'errore: \n"
									 + str(sys.exc_info()[0]) + "\n" + str(sys.exc_info()[1])
									 + "\n" + msg_err_function + "\n\n Contattare l'autore: lorenzo.sulli@gmail.com")