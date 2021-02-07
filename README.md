# pointpicker
 Program to render, filter, segment, and manipulate medical images in 3D and select points for analyses.
 Uses VTK toolkit and marching cubes algorithm to render the surface. Optimized for bone.

 
 Inputs: medical image file (nifti, dicom, aim)
 Outputs: picked points plain text file in a specified directory
 
 Main code: PointPicker_implement.py
 Helper functions: vtk_helpers.py, points.py, echo_arguments.py
 
 Example command line/terminal input:
    >>>python PointPicker_implement.py \input\path\image.nii \output\directory\path\

Press 'p' to place a point at the location of your cursor.
Press 'z' to remove a point at the location of your cursor.
Press 't' to write a plaintext file containing the coordintaes of the points picked.
