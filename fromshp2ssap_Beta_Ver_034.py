#fromshp2ssap.py:  OS indipendent code to write .dat file for SSAP 2000 (www.SSAP.eu) from Shapefile polyline
#Beta Version: 0.3.4 - 2014.03.13 - under test 
#tested with shapefile edit from arcgis 9.2, 3.2 e qgis 1.8.
#Autor: Lorenzo Sulli - Autorità di bacino del fiume Arno (Firenze). lorenzo.sulli@gmail.com
#
#Code re-order shape edit in no order mode
#Added tkinter fram with input box for file path
#
#dowload shapefile.py from http://code.google.com/p/pyshp/
#copy shapefile.py in \Python3x\Lib
#note: this code run on Phyton 3x, shapefile.py run on 2x and 3x

import os
import sys
import shapefile
import datetime

import tkinter
import tkinter.messagebox 

#flag to handle specific SSAP exception


def shp2dat():
	try:
		checkerr1=0
		ver = "0.3.4 - beta - under test: check file .dat before use!"
		t=datetime.datetime.now()
		t2=t.strftime("%A, %d. %B %Y %I:%M%p")
		t2="File creato in data: "+str(t2)
		#edit string to change shapefile path (dir\basename) 
		pathstr= e1.get()
		# if os.path.exists(pathstr)==False:
		sf = shapefile.Reader(pathstr)
		shapes = sf.shapeRecords()# shapes è una list
		num_shape = len(shapes)
		if num_shape > 25:
			tkinter.messagebox.showinfo("Convert shapefile polyline to .dat file","Il numero di polyline nello shapefile "+e1.get()+" è superiore a 25, limite ammesso da SSAP")
			checkerr1 = 1
			exit()
		datpath=e2.get()
		#warning: overwrite existing .dat file!!!
		f_dat=open(datpath,"w+")
		f_dat.write(chr(124)+t2+"\n")
		f_dat.write(chr(124)+"File .dat per SSAP2010 generato da FromShp2dat.py, versione " + ver+"\n")
		f_dat.write(chr(124)+"Numero polyline: "+str(num_shape)+"\n")
		#print function is useful to show running code result in cmd shell or in phyton shell	
		print("FromShp2Dat.py\n"+"Coordinate estratte da Shapefile " + e1.get() + " e convertite in formato .dat:\n")
		#counter for while loop and reorder shape drawing not order (id field <> id object)
		x = 0 # main counter 
		a = x # duplicate counter get from main counter to manage loop (with b variable)
		b = 0 # counter to re-loop when if condition is false

		while x < num_shape:
		#write polyline only when id field = x counter
			if (sf.shapeRecord(a).record[0])==(x+1):
				f_dat.write("##"+str(sf.shapeRecord(a).record[0])+"--------------------------\n")
				print("##"+str(sf.shapeRecord(a).record[0])+"--------------------------\n")
				for y in sf.shapeRecord(a).shape.points:
					f_dat.write("\t"+str(round(y[0],1))+"\t")
					f_dat.write(str(round(y[1],1))+"\n")
					print("\t"+str(round(y[0],1))+"\t",str(round(y[1],1))+"\n")
				x+=1
				a = x-b
				
				if a < 0:
					a = 0 # negative id object not exist
			else:
				a = a+1
				b = b+1
				continue
			
		f_dat.close
		tkinter.messagebox.showinfo("Convert shapefile polyline to .dat file","Procedura conclusa. Verifica il file:"+e2.get())
	except:
		# handled exception of system error: show type reference e value of exception instance 
		# check if a SSAP exception is occur
		if checkerr1==0:
			tkinter.messagebox.showerror("Convert shapefile polyline to .dat file", "Si è verificato un errore! \n" + str(sys.exc_info()[0])+ "; \n" + str(sys.exc_info()[1]))


master = tkinter.Tk()
master.title("Convert shapefile polyline to .dat file")
master.geometry("650x70+250+250") 

tkinter.Label(master, text="Path of input shapefile (accept relative path)", font = ("Courier", 10)).grid(row=0)
tkinter.Label(master, text="Path of output .dat file (accept relative path)",font = ("Courier", 10)).grid(row=1)

e1 = tkinter.Entry(master, width=65,font = ("Courier", 10))
e2 = tkinter.Entry(master, width=65,font = ("Courier", 10))

e1.insert(10,"Shape_Test\polyline_ssap_test")
e2.insert(10,"SSAPPY.dat")

e1.grid(row=0, column=1)
e2.grid(row=1, column=1)

tkinter.Button(master, text='Quit', command=master.quit).grid(row=3, column=1, sticky=tkinter.W, pady=4)
tkinter.Button(master, text='Convert', command=shp2dat).grid(row=3, column=0, sticky=tkinter.W, pady=4)

tkinter.mainloop( )
