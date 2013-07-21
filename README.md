structured_light_stereotaxy
===========================

Structured light imaging of rat skulls


Flexscan scan structure
==========================

A Flexscan project (one per surgery) will contain several scans (in numbered subfolders) each 
with the following files:

*  Scan<index>.3d3 (one version of the 3D mesh)
*  View1/ (images & data for camera 1)
*  View2/ (images & data for camera 2)
*  skull.mtl
*  skull.jpg (this is actually a png, so you will need to rename it to skull.png)
*  skull.obj
*  ref.mtl
*  ref.jpg (also actually a png, so rename this)
*  ref.obj
*  <various other files>


Cleaning scans
===========================

This should be done prior to analyzing.

TODO add notes here


Analyzing new scans
===========================

The main analysis file is: /software/scan_analysis_pipeline/analyze_scans.py

The analysis file should be run only after all scans have skull.obj, skull.png, 
ref.obj, and ref.png files and the meshes have been cleaned.

It accepts 4 command line arguments

  python analyze_scans.py <scan dir> <skull scan index> <hat index> <final index>

and an optional 5th (output directory, will default to "output"). Where the index is the number 
corresponding to the scan (subfolder) containing the files for a given scan.

TODO finish notes
