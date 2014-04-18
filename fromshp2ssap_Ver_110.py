#fromshp2ssap.py:  OS indipendent code to write .dat file for SSAP 2000 (www.SSAP.eu) from Shapefile polyline
#Beta Version: 1.1.0 - 2014.04.18 - under test 
#tested with shapefile edit from arcgis 9.2, 3.2 e qgis 1.8.
#Autor: Lorenzo Sulli - Autorità di bacino del fiume Arno (Firenze). lorenzo.sulli@gmail.com
#
#Code re-order shape edit in no order mode
#Added tkinter fram with input box for file path
#
#download shapefile.py from http://code.google.com/p/pyshp/
#copy shapefile.py in \Python3x\Lib
#note: this code run on Phyton 3x, shapefile.py run on 2x and 3x

import os
import sys
import shapefile
import datetime
import tkinter
import tkinter.messagebox
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename

Ver = "1.1.0"
VerMsg = Ver+" : check file .dat, .geo, .fld before use!"
msg_title="Shapefile to SSAP files"

def shp2datgeofld():
	try:
#flag to handle specific SSAP exception
		Cod_Mod_Fld=0
		checkerr1=0
		t=datetime.datetime.now()
		t2=t.strftime("%A, %d. %B %Y %I:%M%p")
		t2="File creato in data: "+str(t2)
#edit string to change shapefile path (dir\basename) 
		shape_path= e1.get()
		sf = shapefile.Reader(shape_path)
		shapes = sf.shapeRecords()# shapes è una list
		num_shape = len(shapes)
#check SSAP limit number of layers
		if num_shape > 20:
			tkinter.messagebox.showinfo(msg_title,"Il numero di polyline nello shapefile " +
										e1.get()+" è pari a " +str(num_shape)+ " superiore a 20, limite ammesso da SSAP." +
										"\n"+"la procedura termina")
			checkerr1 = 1
			exit()
		ssap_pathname = e2.get()
		
#warning: overwrite existing .dat file!!!
		f_dat=open(ssap_pathname+".dat","w+")
		if CheckCu.get()==1: 
			f_geo=open(ssap_pathname+"_c.geo","w+")
		else:
			f_geo=open(ssap_pathname+"_cu.geo","w+")
		
		
#write header of .dat file
		f_dat.write(chr(124)+t2+"\n")
		f_dat.write(chr(124)+"File .dat per SSAP2010 generato da fromshp2ssap.py, versione " + VerMsg+"\n")
		f_dat.write(chr(124)+"\n")

#print function is useful to show running code result in cmd shell or in phyton shell	
		print("fromshp2ssap.py\n"+"Coordinate estratte da Shapefile " + e1.get() + " e convertite in formato .dat:\n")
		
#counter for while loop and reorder shape drawing not order (id field <> id object)
		mc = 0 # main counter 
		a = mc # duplicate counter get from main counter to manage loop (with b variable)
		b = 0 # counter to re-loop when if condition is false
		c = 0 # variable for manage ID = 0 for write .fld file
		cod_mod_fld=0
#main loop: read shapefile and get geometry layers and points for .dat file, get attribute for .geo file
		while mc < num_shape:			
#write polyline only when id field = mc counter
				
			
			if (sf.shapeRecord(a).record[0])==(mc+1):
#write.geo file
				if CheckCu.get()==1:
					f_geo.write("\t"+str(sf.shapeRecord(a).record[1]))
					f_geo.write("\t"+str(sf.shapeRecord(a).record[2]))
					f_geo.write("\t"+str(0))
				else:
					f_geo.write("\t"+str(0))
					f_geo.write("\t"+str(0))
					f_geo.write("\t"+str(sf.shapeRecord(a).record[3]))					
				f_geo.write("\t"+str(sf.shapeRecord(a).record[4]))
				f_geo.write("\t"+str(sf.shapeRecord(a).record[5])+"\n")
#end write .geo file

#write header layer of .dat file
				f_dat.write("##"+str(sf.shapeRecord(a).record[0])+"--------------------------\n")
#print to show on shell
				print("##"+str(sf.shapeRecord(a).record[0])+"--------------------------\n")
#check points number limit of a layer 
				if len(sf.shapeRecord(a).shape.points)> 100:
					tkinter.messagebox.showinfo("Convert shapefile polyline to .dat file",
												"Il numero di punti dello strato ID="+str(sf.shapeRecord(a).record[0])
												+ " è superiore a 100, limite ammesso da SSAP."+"\n"
												+ "La procedura termina""")
					f_dat.close()
					f_geo.close()
					os.remove((os.path.abspath(f_dat.name)))
					os.remove((os.path.abspath(f_geo.name)))
					checkerr1 = 1
					exit()
#loop to write x,y coordinate of layers points in .dat file				
				for k in sf.shapeRecord(a).shape.points:
					f_dat.write("\t"+str(round(k[0],1))+"\t") #write x coordinate
					f_dat.write(str(round(k[1],1))+"\n")#write y coordinate
					print("\t"+str(round(k[0],1))+"\t",str(round(k[1],1))+"\n")
				mc+=1
				a = mc-b
				
				if a < 0:
					a = 0 # negative id object not exist
#write .fld file if ID = 0			
			elif (sf.shapeRecord(a).record[0])==(c):
                                
				f_fld=open(ssap_pathname+".fld","w+")
				for k in sf.shapeRecord(a).shape.points:
					f_fld.write("\t"+str(round(k[0],1))+"\t") #write x coordinate
					f_fld.write(str(round(k[1],1))+"\n")#write y coordinate
				f_fld.close()
# new c value to skip if condition about .fld file (no id value > num shape is admitted)
				c = num_shape+1
#new limit of loop
				num_shape = num_shape-1 
				Cod_Mod_Fld=1
			
			else:
				a = a+1
				b = b+1
				continue
			
		f_dat.close()
		f_geo.close()
#create file .mod
		if CheckCu.get()==1: 
			f_mod=open(ssap_pathname+"_c.mod","w+")
		else:
			f_mod=open(ssap_pathname+"_cu.mod","w+")
		f_mod.write(str(num_shape)+"    "+str(Cod_Mod_Fld)+"    0    0    0    0"+"\n")
		if Cod_Mod_Fld==1:
			f_mod.write(f_dat.name+"\n"+f_fld.name+"\n"+f_geo.name)
			msg_fld_str=os.path.abspath(f_fld.name)+"\n"
		else:
			f_mod.write(f_dat.name+"\n"+f_geo.name)
			msg_fld_str=""
		f_mod.close()
		
		tkinter.messagebox.showinfo("Shapefile to SSAP","Procedura conclusa. Verifica i file SSAP: \n"+
		os.path.abspath(f_dat.name) + "\n"+
		os.path.abspath(f_geo.name) + "\n"+
		msg_fld_str +
		os.path.abspath(f_mod.name) + "\n")
		
		
	except:
# handled exception of system error: show type reference e value of exception instance 
# check if a SSAP exception is occur
		if checkerr1==0:
			tkinter.messagebox.showerror("Convert shapefile to SSAP file", "Si è verificato un errore!\n"+"La procedura termina \n\n Descrizione dell'errore: \n"+str(sys.exc_info()[0])+ "\n" + str(sys.exc_info()[1]))
			f_dat.close()
			f_geo.close()
			os.remove((os.path.abspath(f_dat.name)))
			os.remove((os.path.abspath(f_geo.name)))
		

############## - tkinter/ttk code - ###################

def load_shapefile():
	e1.delete(0,END)
	shp_name = askopenfilename(filetype=(("Shapefile", "*.shp"),("All files", "*.*")))
	e1.insert(10,shp_name)
def save_SSAPfiles():
	e2.delete(0,END)
	SSAP_name = asksaveasfilename(filetypes=(("SSAP FILES", "*.mod*"),("SSAP FILES", "*.dat*"),("SSAP FILES", "*.geo*"),("SSAP FILES", "*.fld*")))
	ssap_text_pathname = os.path.splitext(SSAP_name)[0]
	e2.insert(10,ssap_text_pathname)


root = tkinter.Tk()
root.title("Conversione polyline shapefile in file .dat .geo e .fld per SSAP - Versione: "+Ver)

master = ttk.Frame(root, padding="12 12 12 12")
master.grid(column=0, row=0, sticky=(N, W, E, S))
master.columnconfigure(0, weight=1)
master.rowconfigure(0, weight=1)
master['borderwidth'] = 2

master['relief'] = 'sunken'

e1 = tkinter.Entry(master, width=50)
e2 = tkinter.Entry(master, width=50)

e1.grid(row=0, column=1,sticky= (E, W))
e2.grid(row=1, column=1,sticky= (E, W))

ttk.Button(master, text='Input Shapefile', command=load_shapefile).grid(row=0, column=0, sticky=(W,E), pady=4, padx=8)
ttk.Button(master, text='Output SSAP files name', command=save_SSAPfiles).grid(row=1, column=0, sticky=(W,E), pady=4, padx=8)
ttk.Button(master, text='Esci', command=master.quit).grid(row=5, column=1, sticky=E, pady=4)
ttk.Button(master, text='Converti', command=shp2datgeofld).grid(row=5, column=0, sticky=W, pady=4)

s = ttk.Separator(master, orient=HORIZONTAL).grid(column=0, row=4, sticky= (E, W),pady=10)
s2 = ttk.Separator(master, orient=HORIZONTAL).grid(column=1, row=4, sticky= (E, W),pady=10)

CheckCu = IntVar()
c1 = Checkbutton(master, text = "Verifica in condizioni drenate, Cu=0", variable = CheckCu, onvalue = 1, offvalue = 0, height=1, width = 30)
c1.grid(row=3, column=0, sticky=W)
c1.select()

root.mainloop( )
