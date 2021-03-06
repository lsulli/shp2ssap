#!/usr/bin/env pythonw

"""
Shp2SSAP_Ver_118_build211.py file sorgente per Shp2SSAP.exe ver 1.1.8 build 211

Applicazione per creare shapefile di modello pendio da elenco coordinate e convertire in file per SSAP2010 (www.ssap.eu).

AUTORE: Lorenzo Sulli - lorenzo.sulli@gmail.com

INDIRIZZO DOWNLOAD: https://github.com/lsulli/shp2ssap

LICENZA: http://www.gnu.org/licenses/gpl.html

Le procedure fondamentali utilizzano il modulo shapefile.py (credit - https://github.com/GeospatialPython/pyshp)

Per il software SSAP2010 vedi termini di licenza riportati in www.SSAP.eu

Per la guida all'uso dello script vedi readme file su https://github.com/lsulli/shp2ssap

"""

# history
# Build 211 - 2018.04.05: risolto errore di trimming falda
# Build 210 - 2018.04.04
# estrazione etichette in modulo esterno
# sostituito identitation tab con 4 spazi (convenzione PEP8)
# Revisionata la funzione triming - Definizione coordinate y funziona correttamente
# semplificazione polyline nel caso punti > 100
# gestione icona finestra principale

try:
    import sys
    sys.path.insert(0, './moduli_py')
    import shapefile
    import s2s_lbl
    import tkinter.messagebox
    import tkinter.filedialog
    from tkinter import *
    from tkinter import ttk
    import os
    import linecache
    import datetime
    import inspect
    import subprocess
    import shutil
    import math
except:
    tkinter.messagebox.showerror(s2s_lbl.msg_title_error, s2s_lbl.msg_error_import)

mtpl_chk = 0

# default value
xy2shp_forSSAP_str = s2s_lbl.xy2Shp_forSSAP_str

global msg_err_end
msg_err_end = ""

# data non use yet
py_file = os.path.basename(sys.argv[0])
Msg_file_py = "File di riferimento per Shp2SSAP: " + py_file
# end

try:
    # ###### default constant and variable that need try - except ######
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


    # ###### main function to check input shapefile and handle errors #########

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

            # get shapefile and make a copy to by-pass simultaneous access to original one
            global shape_path
            shape_path = str_path_shape.get()
            my_path = os.path.splitext(shape_path)[:1][0]
            global my_shp_tmp_list
            my_shp_tmp_list = []
            my_shp_list = [my_path + ".shp", my_path + ".dbf", my_path + ".shx"]
            for a in my_shp_list:
                b = my_path + "_tmp" + os.path.splitext(a)[1:][0]
                shutil.copyfile(a, b)
                my_shp_tmp_list.append(b)
            global shape_path_tmp
            shape_path_tmp = my_path + "_tmp.shp"

            # set main shape variables
            global sf
            global shapes
            global shapes_geometry
            global num_shape
            # make_error(0) # da attivare solo in caso di test per generare un errore voluto
            # try...except with pass for every function to skip error and go on

            # read and set shapefile
            try:
                sf = shapefile.Reader(shape_path_tmp)
            except:
                # ERRORE 01 - failed to read shapefile
                tkinter.messagebox.showerror(s2s_lbl.msg_title_error, s2s_lbl.msg_error01
                                             + str(sys.exc_info()[0]) + "\n"
                                             + str(sys.exc_info()[1]))
                checkerr_pre = 2
                sys.exit()

            # get shapes and geometry
            shapes = sf.shapeRecords()
            shapes_geometry = sf.shapes()
            num_shape = len(shapes)  # get number of features to manage loop and check order

            # check if shapefile fields match SSAP specification and pass to collect information about errors
            try:
                check_flds_shape_ssap(sf)
            except:
                pass

            # ERRORE 02: check if there are dat polyline
            try:
                if chk_fld_datgeo == 0:
                    msg_err_tot += msg_err_fld_datgeo
                    checkerr_pre = 1
                elif chk_fld_datgeo == 1:
                    check_ok = 1
                    # count layers for .dat,.fld and .svr file
                    global count_feat_dat_fld, count_feat_svr, count_feat_sin
                    count_feat_dat_fld, count_feat_svr, count_feat_sin = count_feat_ssap(sf, num_shape)
            except:
                pass

            # ERRORE 03: check if attribute of SSAP field is correct
            try:
                if check_field_ssap(sf, num_shape):  # test ok ver 116_161
                    msg_err_tot += msg_err_shape_fields_ssap
                    checkerr_pre = 1
            except:
                pass

            # ERRORE 04: check if shape type is polyline and exit if not
            try:
                if check_shape_type(shapes_geometry):  # test ok v.116_161
                    msg_err_tot += msg_err_shape_type
                    checkerr_pre = 1
                    sys.exit()
            except:
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
                pass

            # ERRORE 06: check SSAP limit number of points
            try:
                if check_points_number(sf, num_shape):
                    msg_err_tot += msg_err_points_number
                    checkerr_pre = 1
            except:
                pass

            # ERRORE 07: check id = 0 for no fld field
            try:
                if check_id_zero(sf, num_shape):  # test ok ver 116_161
                    msg_err_tot += msg_err_id_zero
                    checkerr_pre = 1
            except:
                pass

            # ERRORE 08: check that all points have positive coordinate
            try:
                if check_all_negative_val(sf, num_shape):
                    msg_err_tot = msg_err_tot + msg_err_negative_val
                    checkerr_pre = 1
            except:
                pass

            # ERRORE 09: check that topographic hasn't jut
            try:
                if check_jutting_surface(sf, num_shape):
                    msg_err_tot += msg_err_jutting_surface
                    checkerr_pre = 1
            except:
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
                pass

            # ERRORE 11: Check if order from top to bottom is correct
            try:
                if CheckTopBottomOrder.get() == 1:
                    if check_top_bottom_order(sf, count_feat_dat_fld):
                        msg_err_tot += msg_err_topdown_order
                        checkerr_pre = 1
            except:
                pass

            if check_ok == 1 and pass_check == 1:
                tkinter.messagebox.showinfo(s2s_lbl.msg_title_check,
                                            "##### Shapefile: '" + shape_path + "'\n\n" + msg_ok_fld_ssap)
            if checkerr_pre == 1:
                sys.exit()

        except:
            if checkerr_pre == 1:
                if len(msg_err_tot) > int(max_char_msg_err):
                    msg_err_tot = msg_err_tot[:int(max_char_msg_err)] + ".......\n"
                tkinter.messagebox.showerror(s2s_lbl.msg_title_error, "##### Shapefile: '" + str_path_shape.get() + "'\n" +
                                             "##### Sono stati riscontrati errori nella conversione ai file per SSAP: \n"
                                             + msg_err_tot + s2s_lbl.msg_err_end1)
                sf = ""  # azzera chiude il riferimento corrente allo shapefile
                remove_all_file(my_shp_tmp_list)
            # gestisce le condizioni note e genera un messaggio di errore solo per situazioni ignote
            elif check_ok == 1 and pass_check == 1:
                pass
            elif checkerr_pre == 2:
                pass
            else:
                default_msg_unknow_error("check_function")


    # ######## Main Function to create ssap file#########

    def shp_2_ssap_files():
        """
        Funzione principale di creazione dei file .dat, .geo, .fld, sin. e .mod
        Richiama le funzioni di controllo tramite gestione errori unica
        """
        try:
            # cond_write_mod_file flag to handle writing of .mod file
            # 1 = write .dat, .geo in .mod file
            # 2 = check .fld,
            # 3 (2+1) = write .dat, .geo, .fld, in .mod file
            # 4 = check .svr,
            # 5 (1+4) = write .dat, .geo, .mod.,svr, in .mod file
            # 7 (1+2+4) = write .dat, .geo, .mod,.fld, .svr in .mod file
            global sf
            my_ssap_files_list = []
            cond_write_mod_file = 0
            checkerr_run = 0
            mystep = 1

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
                msg_err_end = s2s_lbl.msg_err_end2
                sys.exit()

            # ###### start to process data file
            # get topographic limit coordinate to manage trimming of layers
            global x_min_topo, x_max_topo, xlength_topo, xlenght_tolerance
            x_min_topo, x_max_topo = xtopo(num_shape, sf)  # test ok
            xlength_topo = round(x_max_topo - x_min_topo, 2)
            xlenght_tolerance = round(xlength_topo / trim_tolerance_factor, 2)

            # ####### open dat, geo e mod SSAP file
            f_dat = open(ssap_pathname + ".dat", "w")
            my_ssap_files_list.append(f_dat.name)
            f_geo = open(ssap_pathname + ".geo", "w")
            f_mod = open(ssap_pathname + ".mod", "w")
            cond_write_mod_file = 1
            my_ssap_files_list.append(f_geo.name)
            my_ssap_files_list.append(f_mod.name)

            # ####### start to write header of .dat file
            f_dat.write(chr(124) + t2 + "\n")
            f_dat.write(chr(124) + "File .dat per SSAP2010 generato da Shp2SSAP, versione " + s2s_lbl.versione + "\n")
            f_dat.write(chr(124) + "Shapefile di input: '" + str_path_shape.get() + ". \n")

            # ###### start to set and manage loop trough features and pont
            # counter for while loop and reorder shape drawing not order (id field <> id object)
            main_counter = 0  # main counter
            d_mc = main_counter  # duplicate counter get from main counter to manage loop (with re_loop_counter variable)
            re_loop_counter = 0  # counter to re-loop when if condition is false
            c = 0  # variable to manage ID = 0 for write .fld file

            # Start main loop: read shapefile and get geometry layers and points for .dat and .fld file, get attribute for .geo file
            while main_counter < count_feat_dat_fld:
                # write polyline only when id field = main_counter counter

                # x e y value to create line equation for trimming
                # x of the first point of shape (SSAP criteria editing)
                x_min = sf.shapeRecord(d_mc).shape.points[0][0]

                # x value of the last value of x sorted x value of point
                my_x_max_list = []
                for a in sf.shapeRecord(d_mc).shape.points:
                    my_x_max_list.append(a[0])  # get only x value
                my_x_max_list.sort()  # sort list
                x_max = my_x_max_list[-1]  # get last x value

                x_ref1sx, y_ref1sx, x_ref2sx, y_ref2sx, x_ref1dx, y_ref1dx, x_ref2dx, y_ref2dx = xy_ref(
                    sf.shapeRecord(d_mc))
                # print("id: ", sf.shapeRecord(d_mc).record[id_ssap_id], "ref coord: ", x_ref1sx, y_ref1sx, x_ref2sx,
                #       y_ref2sx, x_ref1dx, y_ref1dx, x_ref2dx, y_ref2dx)

                if ((sf.shapeRecord(d_mc).record[id_ssap].casefold()) == "dat"
                    and (sf.shapeRecord(d_mc).record[id_ssap_id]) == (main_counter + 1)
                    and sf.shapeRecord(d_mc).record[id_exclude] != 1):
                    num_pts = len(sf.shapeRecord(d_mc).shape.points)
                    if check_smp_polyline.get() == 1:
                        mystep = math.ceil(num_pts/99)
                    # write data layer in .geo file by dedicated function
                    if chk_fld_rock == 0 or (chk_fld_rock == 1 and (sf.shapeRecord(d_mc).record[id_sigci]) == 0):
                        if (sf.shapeRecord(d_mc).record[id_dr_undr].casefold()) != "u":
                            # to do: write handle null value
                            f_geo.write("\t" + str(sf.shapeRecord(d_mc).record[id_phi]))
                            f_geo.write("\t" + str(sf.shapeRecord(d_mc).record[id_c]))
                            f_geo.write("\t" + str(0))
                        elif (sf.shapeRecord(d_mc).record[id_dr_undr].casefold()) == "u":
                            if check_cu_value(sf.shapeRecord(d_mc).record[id_cu],
                                              sf.shapeRecord(d_mc).record[id_ssap_id]):
                                msg_err_tot += msg_err_cu_value
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
                                + "-------------------------- Numero punti: ~" + str(int(num_pts/mystep)) + "\n")
                    # loop to write x,y coordinate of layers points in .dat file
                    # print("x_min_topo, xlenght_tolerance,x_min", x_min_topo, xlenght_tolerance, x_min)
                    # print("x_max_topo, xlenght_tolerance,x_max", x_max_topo, xlenght_tolerance, x_max)
                    for k in sf.shapeRecord(d_mc).shape.points[::mystep]:
                        print (type(sf.shapeRecord(d_mc).shape.points))
                        # layer trimming for geo/dat layer
                        if check_trimming.get() == 1:
                            if k[0] < (
                                x_min_topo + xlenght_tolerance):  # x a sinistra del limite topografico + tolleranza
                                if k[0] == x_min:  #
                                    var_x = x_min_topo
                                    if sf.shapeRecord(d_mc).record[id_ssap_id] == 1 or x_min == x_min_topo:
                                        var_y = k[1]
                                    else:
                                        var_y = get_y_trim_bound(x_ref1sx, y_ref1sx, x_ref2sx, y_ref2sx, x_min_topo)
                            elif k[0] > (
                                x_max_topo - xlenght_tolerance):  # x a destra del limte topografico - tolleranza
                                print("sono oltre limite destro")
                                if k[0] == x_max:
                                    var_x = x_max_topo
                                    if sf.shapeRecord(d_mc).record[id_ssap_id] == 1 or x_max == x_max_topo:
                                        var_y = k[1]
                                        print("non calcolo", var_y)
                                    else:
                                        var_y = get_y_trim_bound(x_ref1dx, y_ref1dx, x_ref2dx, y_ref2dx, x_max_topo)
                                        print("calcolo y: ", var_y)
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

                    # manage counter

                    main_counter += 1
                    d_mc = main_counter - re_loop_counter
                    if d_mc < 0:
                        d_mc = 0  # negative id object not exist

                # ###### start write .fld file #######
                elif (sf.shapeRecord(d_mc).record[id_ssap].casefold() == "fld"
                      and sf.shapeRecord(d_mc).record[id_ssap_id] == c
                      and sf.shapeRecord(d_mc).record[id_exclude] != 1):
                    # count point ans simplify
                    if check_smp_polyline.get() == 1:
                        num_pts = len(sf.shapeRecord(d_mc).shape.points)
                        mystep = math.ceil(num_pts/99)
                    # open .fld file
                    f_fld = open(ssap_pathname + ".fld", "w")
                    my_ssap_files_list.append(f_fld.name)

                    for k in sf.shapeRecord(d_mc).shape.points[::mystep]:
                        # layer trimming for fld layer
                        if check_trimming.get() == 1:
                            if k[0] < (x_min_topo + xlenght_tolerance):  # se x cade a sinistra del limite topografico
                                if k[0] == x_min:
                                    var_x = x_min_topo
                                    if x_min == x_min_topo:
                                        var_y = k[1]
                                    else:
                                        var_y = get_y_trim_bound(x_ref1sx, y_ref1sx, x_ref2sx, y_ref2sx, x_min_topo)

                            elif k[0] > (x_max_topo - xlenght_tolerance):  # se x cade a destra del limite topografico
                                if k[0] == x_max:
                                    var_x = x_max_topo
                                    if x_max == x_max_topo:
                                        var_y = k[1]
                                    else:
                                        var_y = get_y_trim_bound(x_ref1dx, y_ref1dx, x_ref2dx, y_ref2dx, x_max_topo)

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
                else:
                    d_mc += 1
                    re_loop_counter += 1
                    continue
                # #######end .fld code#######

            # ###### start .svr code ######

            # ###no trimming because overload are always inside topographic limits#
            # check if svr layer exist and if exist set counter
            if count_feat_svr > 0 and chk_fld_svr == 1:
                f_svr = open(ssap_pathname + ".svr", "w")
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
                        var_y_max_svr = sf.shapeRecord(d_mc_svr).shape.points[-1][1]
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
                f_sin = open(ssap_pathname + ".sin", "w")
                my_ssap_files_list.append(f_sin.name)
                f_sin.write("# Shp2SSAP - versione: " + s2s_lbl.versione + "\n")
                f_sin.write("# file " + ssap_pathname + ".sin creato da Shapefile di input: '"
                            + str_path_shape.get() + "\n")
                sin_counter = 0  # main counter
                d_mc_sin = sin_counter  # duplicate counter get from main counter to manage loop (with re_loop_counter variable)
                re_loop_counter_sin = 0  # counter to re-loop when if condition is false
                # loop: read shapefile and get geometry layers and points for .svr
                while sin_counter < count_feat_sin:
                    # write polyline only when id field = mc counter
                    if sf.shapeRecord(d_mc_sin).record[id_ssap].casefold() == "sin":
                        if check_smp_polyline.get() == 1:
                            num_pts = len(sf.shapeRecord(d_mc_sin).shape.points)
                            mystep = math.ceil(num_pts / 99)
                        # loop to write x,y coordinate of layers points in .dat file
                        for k in sf.shapeRecord(d_mc_sin).shape.points[::mystep]:
                            var_x = k[0]
                            var_y = k[1]
                            f_sin.write("\t" + format_float_str(var_x) + "\t\t")  # write x coordinate
                            f_sin.write(format_float_str(var_y) + "\n")  # write y coordinat

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

            # write .mod file checking cond_write_mod_file variable ######
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

            sf = ""  # set to null reference to shapefile (copy tmp shapefile code)

            if checkerr_run == 1:
                remove_all_file(my_ssap_files_list)  # delete ssap file if error is check
                remove_all_file(my_shp_tmp_list)
                sys.exit()
            elif checkerr_run == 0 and checkerr_pre == 0:
                remove_all_file(my_shp_tmp_list)  # delete tmp shapefile when all is ok
                tkinter.messagebox.showinfo(s2s_lbl.msg_title, "Procedura conclusa. Sono stati creati i file SSAP: \n" + str(
                    my_ssap_files_list) + "\n")

            else:
                remove_all_file(my_ssap_files_list)
                remove_all_file(my_shp_tmp_list)
                sys.exit()

        # just a default except to handle error, there are two main type error:
        # SSAP type (checkerr_pre=1) and system error (checkerr_pre = 0), in system error
        # specific error are handled by type default_msg_unknow_error function that return system error
        # and name of function that catch error

        except:
            if checkerr_run == 0 and checkerr_pre == 0:
                remove_all_file(my_ssap_files_list)  # delete ssap file if error is check
                remove_all_file(my_shp_tmp_list)  # delete temp shapfile if error is check
                tkinter.messagebox.showerror(s2s_lbl.msg_title_error, "Si e' verificato un errore non previsto!\n"
                                             + "La procedura termina \n\n Descrizione dell'errore: \n"
                                             + str(sys.exc_info()[0]) + "\n"
                                             + str(sys.exc_info()[1]) + msg_err_function)
            elif checkerr_run == 1:
                if len(msg_err_tot) > int(max_char_msg_err):
                    msg_err_tot = msg_err_tot[:int(max_char_msg_err)] + ".......\n\n"
                tkinter.messagebox.showerror(s2s_lbl.msg_title_error, "##### Shapefile: '" + str_path_shape.get() + "'\n" +
                                             "##### Sono stati riscontrati errori nella conversione ai file per SSAP: " +
                                             "\n\n" + msg_err_tot + msg_err_end)
                remove_all_file(my_ssap_files_list)
                remove_all_file(my_shp_tmp_list)
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
                            "\nERRORE 09: la superficie topografica presenta una forma aggettante\n"

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

            if len(msg_err_points_number) > 0 and check_smp_polyline.get() == 0:
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
                msg_err_topdown_order = s2s_lbl.msg_error11
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
                            "\n ERRORE 07: lo strato 'fld' ha un SSAP_ID = " + str(
                                my_shape.shapeRecord(f).record[id_ssap_id])
                            + ", per convenzione lo strato .fld deve sempre avere SSAP_ID = 0. \n")
                f += 1
            if len(msg_err_id_zero) > 0:
                return True
            else:
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
                msg_err_shape_type = s2s_lbl.msg_error04
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
                msg_err_fld_datgeo = (s2s_lbl.msg_error02
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
                msg_ok_fld_ssap = (
                    "- Sono presenti i campi per creare i file SSAP .dat, .geo per strati rocciosi e .mod \n" +
                    "- Sono stati assegnati gli indici \n \n" +
                    "- Complessivamente sono presenti i seguenti file SSAP: " + str_lack_builder(
                        ok_ssap_fld_tot) + "\n")
            if fld_ssap_set_other.issubset(fld_set):
                chk_fld_other = 1
            if fld_ssap_set_tot.issubset(fld_set):
                msg_ok_fld_ssap = (
                    "- Sono presenti i campi per creare i file SSAP .dat, .geo per strati rocciosi, .svr  e .mod \n" +
                    "- Sono stati assegnati gli indici \n \n" +
                    "- Complessivamente sono presenti i seguenti file SSAP: " + str_lack_builder(
                        ok_ssap_fld_tot) + "\n")
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
            xset = set(xlist)
            list_msg = list(xset - ssapset)
            # condizione per escludere uno strato dalla conversione

            if len(list_msg) > 0:
                msg_err_shape_fields_ssap += s2s_lbl.msg_error03 + str(list_msg) + "\n"
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
                if (shp.shapeRecord(f).record[id_ssap].casefold()) == "dat" and (
                        shp.shapeRecord(f).record[id_ssap_id]) == (1):
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
        Presupposto alla funzione è il rigido rispetto dei criteri di editing del SSAP:
        da sinistra a destra per gli strati continui e in senso antiorario nel caso di lenti
        """
        try:
            var_y_ref1sx = 0
            var_x_ref1sx = 0
            var_y_ref2sx = 0
            var_x_ref2sx = 0
            var_y_ref1dx = 0
            var_x_ref1dx = 0
            var_y_ref2dx = 0
            var_x_ref2dx = 0
            my_list_xyref = []
            my_refsx_index = 0
            my_refdx_index = 0

            for k in shp_rec.shape.points:
                my_list_xyref.append(k)

            for k in shp_rec.shape.points:
                # se i punti sono a sinistra del limite si completa il ciclo sino a l'ultimo valore
                # inferiore ai limiti sinistro e destro
                if k[0] > (x_min_topo + xlenght_tolerance):
                    my_refsx_index = my_list_xyref.index(k)
                    break

            for k in shp_rec.shape.points:
                if k[0] > (x_max_topo - xlenght_tolerance):
                    my_refdx_index = my_list_xyref.index(k)
                    break

            # coordinata x dell'ultimo punto prima del limite sinistro
            var_x_ref1sx = round(my_list_xyref[my_refsx_index - 1][0], 2)
            # coordinata y dell'ultimo punto prima del limite sinistro
            var_y_ref1sx = round(my_list_xyref[my_refsx_index - 1][1], 2)
            # coordinata x del primo punto dopo il limite sinistro
            var_x_ref2sx = round(my_list_xyref[my_refsx_index][0], 2)
            # cootdinata y del primo punto dopo il limite sinistro
            var_y_ref2sx = round(my_list_xyref[my_refsx_index][1], 2)
            # coordinata x dell'ultimo punto prima del limite destro
            var_x_ref1dx = round(my_list_xyref[my_refdx_index - 1][0], 2)
            # coordinata y dell'ultimo punto prima del limite destro
            var_y_ref1dx = round(my_list_xyref[my_refdx_index - 1][1], 2)
            # coordinata x del primo punto dopo il limite destro
            var_x_ref2dx = round(my_list_xyref[my_refdx_index][0], 2)
            # cootdinata y del primo punto dopo il limite destro
            var_y_ref2dx = round(my_list_xyref[my_refdx_index][1], 2)

            return var_x_ref1sx, var_y_ref1sx, var_x_ref2sx, var_y_ref2sx, var_x_ref1dx, var_y_ref1dx, var_x_ref2dx, var_y_ref2dx
        except:
            default_msg_unknow_error("xy_ref")


    def get_y_trim_bound(x_ref1, y_ref1, x_ref2, y_ref2, var_x_topo):
        """
        Restituisce il valore della y dell'n-esima superficie di strato
        corrispondente al valore x della superficie topografica giacente sulla retta
        congiugente due punti di riferimento.
        """
        try:
            y = 0
            # sviluppo l'equazione delle retta passante tra due punti
            y = (((var_x_topo - x_ref1) / (x_ref2 - x_ref1)) * (y_ref2 - y_ref1)) + y_ref1
            return y
        except:
            default_msg_unknow_error("get_y_trim_bound")

except:
    if checkerr_pre == 2:
        pass
    else:
        tkinter.messagebox.showerror(s2s_lbl.msg_title_error,
                                     return_line_code_number() + s2s_lbl.header_msg_error
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
        defpathshp = os.getcwd() + linecache.getline("default.txt", 2)
        defpathshp = defpathshp[:-1]  # remove /n special character
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
        defpathssap = os.getcwd() + linecache.getline("default.txt", 4)
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


global pid_proc


def open_form():
    try:
        if os.path.exists(xy2shp_forSSAP_str):
            proc = subprocess.Popen(xy2shp_forSSAP_str, creationflags=subprocess.SW_HIDE, shell=True)
        elif os.path.exists('xy2Shp_forSSAP.exe'):
            proc = subprocess.Popen('xy2Shp_forSSAP.exe', creationflags=subprocess.SW_HIDE, shell=True)
        else:
            tkinter.messagebox.showerror(s2s_lbl.msg_title_error, "Controllare se il file 'xy2Shp_forSSAP.exe' esiste")
    except:
        tkinter.messagebox.showerror(s2s_lbl.msg_title_error, str(sys.exc_info()[0]) + "\n" + str(sys.exc_info()[1]))


try:

    # Mmain Frame
    root = tkinter.Tk()
    root.title(s2s_lbl.root_title)
    root.resizable(FALSE, FALSE)
    # looking for icon if not exist use default one
    if os.path.exists('.\Icon\Shp2SSAP.ico'):
        root.iconbitmap('.\Icon\Shp2SSAP.ico')
    elif os.path.exists('Shp2SSAP.ico'):
        root.iconbitmap('Shp2SSAP.ico')
    else:
        pass

    master = ttk.Frame(root, padding="12 12 12 12")
    master.grid(column=0, row=0, sticky=(N, W, E, S))
    master.columnconfigure(0, weight=1)
    master.rowconfigure(0, weight=1)
    master['borderwidth'] = 2
    master['relief'] = 'sunken'

    # Input box
    var1 = tkinter.StringVar(root)
    var2 = tkinter.StringVar(root)
    str_path_shape = tkinter.Entry(master, width=75, textvariable=var1)
    str_path_ssap = tkinter.Entry(master, width=75, textvariable=var2)
    str_path_shape.grid(row=2, column=1, sticky=(E, W))
    str_path_ssap.grid(row=3, column=1, sticky=(E, W))
    var1.trace("w", active_disable_button)
    var2.trace("w", active_disable_button)

    # BUTTONS
    XY_Button = Button(master, text='Crea Shape da XY', command=open_form)
    XY_Button.grid(row=1, column=0, sticky=(W, E), pady=4, padx=8)
    In_Button = Button(master, text='Input Shapefile', command=load_shapefile)
    In_Button.grid(row=2, column=0, sticky=(W, E), pady=4, padx=8)
    Out_Button = Button(master, text='Output SSAP files', command=save_files_ssap)
    Out_Button.grid(row=3, column=0, sticky=(W, E), pady=4, padx=8)
    Exit_Button = Button(master, text='Esci', command=master.quit)
    Exit_Button.grid(row=8, column=1, sticky=E, pady=4)
    Ver_Button = Button(master, text='Verifica preliminare Shape', command=lambda: check_function(1))
    Ver_Button.grid(row=8, column=0, sticky=W, pady=4)
    Conv_Button = Button(master, text='Converti', command=shp_2_ssap_files)
    Conv_Button.grid(row=8, column=0, sticky=E, pady=4)
    Conv_Button.configure(state=DISABLED)
    Ver_Button.configure(state=DISABLED)

    # Separator
    s1 = ttk.Separator(master, orient=HORIZONTAL).grid(column=1, row=1, sticky=(E, W), pady=6)
    s2 = ttk.Separator(master, orient=HORIZONTAL).grid(column=1, row=4, sticky=(E, W), pady=6)
    s3 = ttk.Separator(master, orient=HORIZONTAL).grid(column=0, row=7, sticky=(E, W), pady=10,columnspan=3)

    # label
    l1 = ttk.Label(master, text='  Opzioni controllo e creazioni strati', borderwidth=5, relief=GROOVE,
                   foreground='black')
    l1.grid(column=0, row=4, pady=10, ipadx=10, ipady=3, sticky=(E, W))

    # checkbutton
    check_cu = IntVar()
    CheckTopBottomOrder = IntVar()
    c1 = Checkbutton(master, text="Verifica ordinamento verticale strati", variable=CheckTopBottomOrder,
                     onvalue=1, offvalue=0, height=1, width=35, anchor=W)
    c1.grid(row=5, column=0, sticky=W)
    c1.select()
    check_trimming = IntVar()
    c2 = Checkbutton(master, text="Regola gli strati alla superficie topografica", variable=check_trimming,
                     onvalue=1, offvalue=0, height=1, width=35, anchor=E)
    c2.grid(row=5, column=1, sticky=W)
    c2.select()
    check_smp_polyline = IntVar()
    c3 = Checkbutton(master, text="Semplifica polyline se > 100 punti", variable=check_smp_polyline,
                     onvalue=1, offvalue=0, height=1, width=35, anchor=W)
    c3.grid(row=6, column=0, sticky=W)
    c3.select()

    # mainloop
    root.mainloop()
except:
    tkinter.messagebox.showerror(s2s_lbl.msg_title_error,
                                 return_line_code_number() + " Si e' verificato un errore non previsto!\n"
                                 + "La procedura termina \n\n Descrizione dell'errore: \n"
                                 + str(sys.exc_info()[0]) + "\n" + str(sys.exc_info()[1])
                                 + "\n" + msg_err_function + "\n\n Contattare l'autore: lorenzo.sulli@gmail.com")
