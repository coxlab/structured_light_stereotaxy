structured_light_stereotaxy
===========================

Structured light imaging of rat skulls


Flexscan scan structure
==========================

A Flexscan project (one per surgery) will contain several scans (in numbered subfolders) each 
with the following files:

* Scan<index>.3d3 (one version of the 3D mesh)
* View1/ (images & data for camera 1)
* View2/ (images & data for camera 2)
* skull.mtl
* skull.jpg (this is actually a png, so you will need to rename it to skull.png)
* skull.obj
* ref.mtl
* ref.jpg (also actually a png, so rename this)
* ref.obj
* ...various other files


Pre-Cleaning Scans
===========================

This should be done prior to analyzing. Dowload meshlab to clean scans. For each scan:

* rename .jpg files to .png (see above)
* copy skull.obj and ref.obj to skull_original.obj and ref_original.obj
* open each original file in meshlab and delete unneeded faces
* to delete faces, use the "Select Faces in a rectangular region" tool to select unneeded faces
* then click "Delete the current set of faces and all the vertices surrounded by that faces"
* remove all faces that aren't: skull, ref object, craniotomy, implants
* remove all faces that are obviously errors
* export cleaned mesh as skull.obj (or ref.obj) with only the 'Vert - TexCoord' option selected


Analyzing new scans
===========================

The main analysis file is: /software/scan_analysis_pipeline/analyze_scans.py

The analysis file should be run only after all scans have skull.obj, skull.png, 
ref.obj, and ref.png files and the meshes have been cleaned (see Pre-Cleaning Scans).

It accepts 4 command line arguments

    python analyze_scans.py <scan dir> <skull scan index> <hat index> <final index>

and an optional 5th (output directory, will default to "output"). Where the index is the number 
corresponding to the scan (subfolder) containing the files for a given scan.

An example command might look like:

    python analyze_scans.py scans/S1 1 2 4

The analysis script includes the following steps that require user interaction (see example_images):

* identify skull landmarks in skull scan (using bezier curves)
* identify tc landmarks in hat scan (using line intersections)
* identify tc landmarks in final scan (in case there is a shift)

See panZoom.py below for controls.

When presented with the texture image from the skull scan add 3 bezier curves on the midline, 
bregmoidal and lamboidal sutures. When happy with the curves, get their intersections (which are bregma and lambda) 
and press shift+'Q' to save the points and quit.

When presented with the hat and final scan images. Identify the grid intersections by drawing 5 horizontal 
and 9 vertical lines, getting their intersections, and quitting with shift+'Q'.

After the script completes you will need to:

* clean & simplify resulting meshes (see Post-Cleaning Scans)
* create an animalCfg.py into the output folder [it is safe to copy one from a recent scan]


Post-Cleaning Scans
=============================

The following scans need to be cleaned: skullInSkull.obj hatInSkull.obj finalInSkull.obj
with this procedure:

* open scan in meshlab
* delete unnecessary faces (see old scans)
* remove all invalid faces (the analysis script tries to fill in ALL holes, resulting in many invalid faces)
* remove all but what is useful while running a physiology session [skull surface, craniotomy, grid points]
* save temporary file [skull/hat/final.obj] in case next step crashes meshlab [it is likely]
* Remesh/simplify using: Filters->Remeshing->Quadric Edge Collapse Decimation
* Options:

    Leave Target number of faces as default
    0.3 percent reduction
    Leave Quality Threshold as default
    Preserve Boundary
    Preserve Normal
    Preserve Topology
    Post-simplification cleaning

* save file as [skull/hat/final.obj]
* if file is larger than 1MB rerun Remeshing


panZoom.py
=============================

panZoom.py is used to identify points, lines, and curves in the texture images to aid in the selection of 
skull and tc landmarks. The basic controls are:

* z/x : zoom in/out
* w/a/s/d : pan up/left/down/right
* W/A/S/D : pan a larger distance
* c/C : change contrast [remove colors of points]
* l/L : add/delete line (using last 2 points)
* b/B : add/delete bezier curve (using last 4 points [endpoint, control, control, endpoint])
* i : calculate intersections of curves/lines and add them as points [this will delete lines/curves]
* Q : quit program and save data [this is a capital Q]
* left mouse button : add a point
* middle : move a point
* right : delete a point
