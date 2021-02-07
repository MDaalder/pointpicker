# pointpicker
 Program to render, filter, segment, and manipulate medical images in 3D and select points for analyses.
 Uses VTK toolkit and marching cubes algorithm to render the surface. Optimized for bone.


 ###Inputs:  
  - medical image file (nifti, dicom, aim)  
 ###Outputs:  
  - picked points plain text file in a specified directory
 
 Main code: PointPicker_implement.py  
 Helper functions: vtk_helpers.py, points.py, echo_arguments.py  
 
 Example command line/terminal input:  
    >>>python PointPicker_implement.py \input\path\image.nii \output\directory\path\

Press 'p' to place a point at the location of your cursor.  
Press 'z' to remove a point at the location of your cursor.  
Press 't' to write a plaintext file containing the coordintaes of the points picked.  

## Setting up the environment to run this program:

1. Install Anaconda with the latest Python 3.0 version
2. Create a directory for the code base i.e. /Users/pointpicker and navigate to that directory
3. In the terminal or Git Bash, run `git clone <git url>`
4. Run `conda env create -f environment.yml` to create the conda environment (called imaging) while in the same directory as 2 and 3
5. Activate course environment with `conda activate imaging`
6. Deactivate the course environment with `conda deactivate`

## Setting up the environment from scratch:

Create virtual environments and add packages
  ### If running windows, use the Command Prompt or Anaconda Prompt (best)
  
  #### Update installation
  - `conda update conda`
  - `conda update anaconda`
  
  #### Create course environment
  - `conda create -n <env name> python=3`
  
  #### Install vtk package and others (ITK, pydicom)
  - `<env name>$ conda install vtk`
  - `<env name>$ conda install -c conda-forge itk`
  - `<env name>$ conda install -c conda-forge pydicom`
  
  #### Deactivate Environment
  - `<env name>conda deactivate`
  
  ### Check Installation
  - `conda activate <env name>`
  - `<env name>$ python`
  - `import vtk`
  - `print(vtk.vtkVersion.GetVTKSourceVersion())`
  - 'vtk version 8.2.0'
