## **Qgis Plugin Shp2SSAP ver 2.0.7 (build 274)** ##

QGIS plugin for managing the SSAP2010 slope model (www.ssap.eu) in a GIS environment.

It allows converting polyline shapefiles and geopackages of a slope model into files for SSAP2010 (tested with SSAP versions 4x and above). A single-layer slope layer ready for conversion can be created starting from a list of topographic surface coordinates; it accepts text files with pairs of metric numeric coordinates, 2D DXF format or .csv files extracted from the QGIS **elevation** tool or the **Profile Plugin** for QGIS.

**----- TABLE OF CONTENTS -----**
1. [Author/Home Page/License](#author)
2. [System Requirements](#sys_req)
3. [Main Features](#main_feat)
4. [Installation](#installation)
5. [User Guide](#guide)
6. [Vector Layer Attributes for SSAP](#shp_attr)
7. [Upgrade](#upgrade)
8. [Bug Fix](#bug_fix)

**----- AUTHOR -----** <a name="author"></a>

Lorenzo Sulli - Autorità di bacino distrettuale Appennino settentrionale

l.sulli@appenninosettentrionale.it - lorenzo.sulli@gmail.com

Code optimization and plugin code generation via ChatGPT 5.2 up to 27/02/2026 and subsequently via Claude Sonnet 4.6, starting from the author's original Python sources Shp2SSAP_Ver_118_build212.py and xy2shp_forSSAP_095_028.py.

**HOME PAGE - CODE REPOSITORY**

https://github.com/lsulli/shp2ssap

Guide: https://github.com/lsulli/shp2ssap/blob/master/README.md

Latest plugin file: https://github.com/lsulli/shp2ssap/blob/master/Shp2SSAP_QGIS_v207_build274.zip

**LICENSE**

http://www.gnu.org/licenses/gpl.html

The core procedures use the shapefile.py module (credit: https://github.com/GeospatialPython/pyshp) and the QGIS libraries.
For the SSAP2010 software, see the license terms at www.ssap.eu (Author: Lorenzo Borselli).

**----- SYSTEM REQUIREMENTS -----** <a name="sys_req"></a>

QGIS version 3.x or higher installed, tested with 3.24, 3.34, 3.40.

No external Python modules or libraries beyond QGIS are required.

**----- MAIN FEATURES -----** <a name="main_feat"></a>

QGIS plugin for creating .dat, .geo, .fld, .svr, .sin and .mod files for SSAP2010 (www.SSAP.eu) starting from a single polyline shapefile. By leveraging GIS functionality, it is possible to manage geometry editing in an integrated way for the .dat, .fld, .svr and .sin files, as well as attribute data for the .geo and .svr files.

It is possible to create a single-layer vector layer (already structured for generating SSAP files) starting from a list of Cartesian XY coordinates describing the morphological profile of the terrain. The shapefile describes the geometric model (i.e., data for the .dat file), with the optional presence of a water table (data for the .fld file) and bedrock (layer **SSAP_ID** = 2 in the .dat file). The polylines describing the geometric model have associated attributes for creating the .geo file. By editing the vector layer in the GIS environment, attributes for the .geo file can be modified, additional polylines describing other layers can be added, loads can be inserted (data for .svr file), and a single verification surface can be defined (for the .sin file).

**Typical Workflow**

```
                    ┌──────────────────────────────────────┐
                    │         TOPOGRAPHIC PROFILE          │
                    │  (XY file, DXF, CSV, or clipboard)   │
                    └──────────────┬───────────────────────┘
                                   │
                          TAB: XY → Vector
                                   │
                    ┌──────────────▼───────────────────────┐
                    │     SHAPEFILE / GEOPACKAGE SSAP      │
                    │  single layer or with bedrock/water  │
                    │        (data for dat, fld, geo)      │
                    └──────────────┬───────────────────────┘
                                   │
                    ┌──────────────▼───────────────────────┐
                    │   Editing in QGIS (add layers,       │
                    │   fill in geotechnical parameters)   │
                    └──────────────┬───────────────────────
                                   │
                         TAB: Vector → SSAP Files
                                   │
                              Trim/simplify
                              (if needed)
                                   │
                    ┌──────────────▼───────────────────────┐
                    │      Preliminary check               │
                    └──────────────┬───────────────────────┘
                                   │
                    ┌──────────────▼───────────────────────┐
                    │    .dat  .geo  .fld  .svr  .mod      │
                    └──────────────┬───────────────────────┘
                                   │
                             Launch SSAP2010
```

**----- INSTALLATION -----** <a name="installation"></a>

Installation can be done directly in QGIS from the zip file [https://github.com/lsulli/shp2ssap/releases/download/Ver_2_0_7_Build274/Shp2SSAP_QGIS_v207_build274.zip] via the menu [*Plugins/Manage and Install Plugins/Install from zip*], or by installing the plugin from [*Plugins/Manage and Install Plugins/All*] searching with the keyword *"Shp2SSAP"*.

**----- USER GUIDE -----** <a name="guide"></a>

**STARTUP**

Once the **Shp2SSAP** plugin is installed and activated, clicking the icon ![Optional Text](../master/Image_readme/fig_shp2SSAP_icon.png) in the *plugins toolbar* or selecting the corresponding entry in the *plugins* menu opens a multi-tab dialog with three tabs: *TAB XY → Vector*, *Vector → SSAP Files*, and *Options*.

**TAB XY → Vector**

![Optional Text](../master/Image_readme/Screenshot_Shp2SSAP_Tab1.png)

From the *XY → Vector* tab, it is possible to create a polyline vector layer of the topographic surface from a list of XY coordinates (in the .dat file, a single layer with **SSAP_ID** = 1). Input data can come from a file or directly from the clipboard (retrieves the last copied content). Tested for .csv and 2D DXF formats exported from the QGIS *elevation* tool and for data copied to the clipboard, and 2D DXF format for *Profile Plugin*.
Input coordinates must have values and ordering consistent with the .dat file standard for SSAP. The vector layer will have all the attributes needed to be converted into SSAP files for a single-layer slope model.

<details>
<summary> XY pair values. Tested cases. </summary>

  The typical structure of an accepted XY file is that commonly generated by GIS tools
  for creating profiles from DTMs. The file must be an ASCII file (.txt, .csv or .dxf by default)
  with pairs of numeric values listed row by row. Various cases are accepted, including cases with interleaved strings.
  Comma is not accepted as a column separator.
  Tested cases are as follows (test script: [test_parse_xy_points.py](https://github.com/lsulli/shp2ssap/blob/master/test_parse_xy_points.py)).

    #1. Normal row with values separated by any whitespace (space, tab, newline, etc.)
        input ("1.5 3.2")
        output [1.5, 3.2]
    #2. Row with comma as decimal separator
        input ("1,5 3,2")
        output [1.5, 3.2]
    #3. Row with a text label at the beginning and commas as separators
        input ("id_string, label:, 1.5, 3.2")
        output [1.5, 3.2]

</details>

**TAB Vector → SSAP Files**

![Optional Text](../master/Image_readme/Screenshot_Shp2SSAP_Tab2.png)

From the *Vector → SSAP Files* tab, the vector layer structured for SSAP is converted into the SSAP2010 input files. The input vector layer must be selected from those loaded in the QGIS project.

The **Convert** button starts the conversion process. In the event of errors, these are reported in the QGIS log messages and in a dedicated message window.

The **Launch SSAP** button starts the SSAP2010 executable, if the path has been set in the *Options* tab.

**Preliminary check**

Before conversion, a preliminary check on the vector layer is performed to verify compliance with the layer structure required for SSAP. Errors found are reported in the QGIS log and in a dedicated message window.

The **Check vector layer** button launches the preliminary check of the vector layer without performing the conversion.

The **vertical layer ordering check** option verifies that the layers are ordered from top to bottom by SSAP_ID. In some cases of complex geometry, the **vertical layer ordering check** option may generate false errors; in that case, it should be disabled.

**Adjust vector layers to the limits of the topographic surface** function

By acting on the vector file, a trimming procedure can be applied to layers that exceed the minimum and/or maximum abscissa values of the topographic surface. This is useful for editing layers without worrying about the precision of the start and end points relative to the topographic surface. By default, a temporary vector named *miolayer_trim* is created; an option is available to edit the layer directly as indicated in the *input vector* field.

    NOTE: This procedure only works by setting the layer limits with x values
    lower than the left boundary and higher than the right boundary.

**Reduce the number of nodes per layer** function

An essential function for creating shapefiles with a number of nodes consistent with SSAP specifications, i.e., fewer than 100 nodes — a common condition when the topographic profile is derived directly from a DTM. By default, a temporary vector named *miolayer_simplified* is created; an option is available to edit the layer directly in the *input vector* field. The *Node count limit* control can be set to a value from 2 to 99.

    TIP: This option is also useful when you want to facilitate snapping of new polylines
    to the topographic surface by reducing the number of snap nodes (particularly when
    lenses have one side coinciding with the surface).

**TAB Options**

Sets default values for the **XY → Vector** tab, and reference directories for input/output and for the SSAP.exe executable.

The **Save** button updates the data in the tabs by saving the values to the *default.txt* file in the "Shp2SSAP" directory created within the currently active default directory, typically "C:\Users\<user>\AppData\Roaming\QGIS\QGIS3\profiles\default\".

The **Reload** button retrieves the default data saved via the **Save** button.

The **Reset** button restores the original values and updates the default.txt file.

![Optional Text](../master/Image_readme/Screenshot_Shp2SSAP_Tab3.png)

**----- VECTOR LAYER ATTRIBUTES FOR SSAP SLOPE MODEL CONVERSION -----** <a name="shp_attr"></a>

    REMINDER: The *XY → Vector* TAB generates directly a vector that meets the criteria described in this section;
    it is not necessary to create it from scratch.

Only "single part" polyline vectors are accepted. If a vector with a different geometry type is loaded, an error will be generated.

    WARNING: The geometry must strictly comply with the SSAP specifications for .dat files
    as specified in the SSAP 4.9.8 manual, chapter 3.3.

<details>
<summary> Structure and meaning of vector layer attributes for SSAP </summary>

No predefined field order is required; however, the use of the field names and the minimum type and length indicated is mandatory.

    WARNING: Null values are not accepted; errors may be generated during conversion.
    In some cases these are unhandled errors that are therefore 'asymptomatic' but prevent
    the process from completing.

['SSAP_ID', 'N', 2, 0] Layer index (required field)

['SSAP', 'C', 3] SSAP file type. Accepted values: dat, geo, fld, svr, sin (required field)

['PHI', 'N', 4, 2] Friction angle value – degrees (required field)

['C', 'N', 5, 2] Effective cohesion – kPa (required field)

['CU', 'N', 5, 2] Undrained cohesion – kPa (required field)

['GAMMA', 'N', 5, 2] Natural unit weight – kN/m³ (required field)

['GAMMASAT', 'N', 5, 2] Saturated unit weight – kN/m³ (required field)

['EXCLUDE', 'N', 1, 0] Boolean field to exclude layer, surcharge, water table or verification surface. Accepted values: 1 = exclude, <> 1 = convert (required field)

['DR_UNDR', 'C', 1, 0] Field for drained/undrained condition selection. Accepted values: D or <> U = drained (default), U = undrained (required field)

['SIGCI', 'N', 5, 2] Uniaxial Compressive Strength of intact rock – MPa (optional field)

['GSI','N', 5, 2] Geological Strength Index – dimensionless (optional field)

['MI','N', 5, 2] Rock mass lithological index – dimensionless (optional field)

['D','N', 5, 2] Rock mass disturbance factor – dimensionless (optional field)

['VAl1','N', 10, 2] Characteristic value for .svr file – in kPa (optional field)

In detail:

- The **SSAP_ID** field must contain the layer index (stored in the .dat file) or the surcharge index (stored in the .svr file), following the numeric sequence according to the specifications in the SSAP manual.

- The **SSAP** field must indicate which SSAP file the polyline refers to.

- For layers with **SSAP** = "dat" and **SSAP** = "svr", a set of increasing **SSAP_ID** values from top to bottom, continuous from 1 to n, is required (n = 20 for **SSAP** = "dat" and n = 10 for **SSAP** = "svr"). For these polylines, **SSAP_ID** = 0 is **not** allowed; this value is reserved for polylines with **SSAP** = "fld".

- Polylines with **SSAP** = "dat" and **SSAP** = "svr" can also be added interleaved with existing polylines of the same type (add layers freely), but the geometrically increasing and continuous top-to-bottom sequence of the **SSAP_ID** field must still be respected. Therefore, when inserting a new layer between two existing ones, the **SSAP_ID** field must be edited and updated.

- For **SSAP** = "fld" (water table), only one layer with **SSAP_ID** = 0 is allowed: this value uniquely identifies the water table.

- For **SSAP** = "sin" (single verification surface), only one layer with **SSAP_ID** > 0 is allowed.

- For **SSAP** = "svr" (surcharges), only one layer with **SSAP_ID** > 0 is allowed.
A .svr file with uniform non-inclined loads is always created.

- The **.geo** file is generated based on the values of the dedicated fields (PHI, C, CU, etc.). Both C and Cu values > 0 can be present simultaneously; the user can choose whether to impose drained or undrained conditions for the individual layer by setting D (drained) or U (undrained) in the **DR_UNDR** field. The .geo files for SSAP2010 will be created accordingly, writing the values according to SSAP specifications.

The **EXCLUDE** field allows individual layers (**SSAP** = "dat", "svr", "fld" or "sin") to be excluded from conversion to SSAP2010 files.

    WARNING: if individual polylines with SSAP = "dat" or SSAP = "svr" are excluded,
    the USER_ID field values must be checked to ensure a continuous and increasing
    sequence 1 – n from top to bottom. If needed, the sequence must be restored by
    editing the SSAP_ID field values; if the sequence is incorrect, an error will be generated.

If a **SIGCI** value > 0 is present, a .geo file for rock layers is generated, and the field values for soils are ignored and set to zero in the output .geo file.

</details>

**----- UPGRADE -----** <a name="upgrade"></a>

See change_log.txt – https://github.com/lsulli/shp2ssap/blob/master/change_log.txt

**----- BUG FIX -----** <a name="bug_fix"></a>

The application has been tested with very complex slope models and simulating various error combinations. These are intercepted by the control system, which typically reports them in the log file and displays them via dedicated message windows or QGIS messaging.

The ease with which layers of complex geometry can be created through editing in QGIS is a potential source of unhandled errors, which are mainly caused by failure to comply with the SSAP editing criteria.

If unexpected errors occur, you can report them by email (l.sulli@appenninosettentrionale.it), attaching the shapefile that generated the error.
If errors are generated by **SSAP2010**, particularly during model reading, after verifying that no editing errors occurred, you can report them by email, attaching both the shapefile and the SSAP model that generated the error.

Thank you for your collaboration and good work.

Last modified: **2026.03.22**
