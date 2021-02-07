
# Imports
import argparse
import os
import vtk

from bonelab.util.echo_arguments import echo_arguments
from bonelab.io.points import write_points
from bonelab.io.vtk_helpers import get_vtk_reader

def PointPicker(input_filename, output_filename, overwrite=False):
    # Check if output exists and should overwrite
    if os.path.isfile(output_filename) and not overwrite:
        result = input('File \"{}\" already exists. Overwrite? [y/n]: '.format(output_filename))
        if result.lower() not in ['y', 'yes']:
            print('Not overwriting. Exiting...')
            os.sys.exit()

    # Read input
    if not os.path.isfile(input_filename):
        os.sys.exit('[ERROR] Cannot find file \"{}\"'.format(input_filename))

    reader = get_vtk_reader(input_filename)
    if reader is None:
        os.sys.exit('[ERROR] Cannot find reader for file \"{}\"'.format(input_filename))

    print('Reading input image ' + input_filename)
    reader.SetFileName(input_filename)
    reader.Update()
    
    # TODO: Matt's **crazy** work
    
    # apply filter(s) to images to smooth it out
    filteredImg = vtk.vtkImageGaussianSmooth()
    filteredImg.SetInputConnection(reader.GetOutputPort())
    filteredImg.SetStandardDeviation(1)
    filteredImg.SetRadiusFactors(1,1,1)
    filteredImg.SetDimensionality(3)
    filteredImg.Update()
    
    
    """ render and display the image """
    
       
    #set threshold values for segmentation
    loThresh = 200
    hiThresh = 3000
    
    # Threshold the image and segment
    segmentImg = vtk.vtkImageThreshold()
    segmentImg.SetInputData(filteredImg.GetOutput())
    segmentImg.ThresholdBetween(loThresh, hiThresh)
    segmentImg.ReplaceInOn()
    segmentImg.SetInValue(1)
    segmentImg.ReplaceOutOn()
    segmentImg.SetOutValue(0)
    segmentImg.SetOutputScalarTypeToFloat()
    segmentImg.Update()
    
    # initialise 3D marching cubes render
    marchingCubes = vtk.vtkMarchingCubes()
    marchingCubes.SetInputConnection(segmentImg.GetOutputPort())
    marchingCubes.ComputeNormalsOn()
    marchingCubes.SetValue(0, 1.0)

    # # get largest object only (remove noise or unwanted objects)
    # largestObject = vtk.vtkPolyDataConnectivityFilter()
    # largestObject.SetInputConnection(marchingCubes.GetOutputPort())
    # largestObject.SetExtractionModeToLargestRegion()
    # largestObject.ColorRegionsOn()
    # largestObject.Update()
    
    # Filter to smooth the surface
    smoothImg = vtk.vtkSmoothPolyDataFilter()
    smoothImg.SetInputConnection(marchingCubes.GetOutputPort())
    smoothImg.SetNumberOfIterations(5)
    smoothImg.SetRelaxationFactor(0.2)
    smoothImg.FeatureEdgeSmoothingOff()
    smoothImg.BoundarySmoothingOn()
    smoothImg.Update()
    
    # Calculate normals for triangle strips
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(smoothImg.GetOutputPort())
    normals.ComputePointNormalsOn()
    normals.ComputeCellNormalsOn()
    normals.ConsistencyOn()
    normals.Update()
    
    # create a dict of preset colors (i.e. bone, skin, blood, etc)
    colors = {}
    colors = {'skin':(0.90, 0.76, 0.6), 
              'bone':(0.83, 0.8, 0.81), 
              'red':(0.65, 0.1, 0.1), 
              'green':(0, 0.9, 0.2), 
              'purple':(0.7, 0.61, 0.85)}

    # initialise mapper of opaque 3D image
    mapper3DOpaque = vtk.vtkPolyDataMapper()
    mapper3DOpaque.SetInputConnection(normals.GetOutputPort())
    mapper3DOpaque.ScalarVisibilityOff()

    # initialise the opaque actor
    actor3DOpaque = vtk.vtkActor()
    actor3DOpaque.SetMapper(mapper3DOpaque)
    actor3DOpaque.GetProperty().SetOpacity(1.0)
    actor3DOpaque.GetProperty().SetColor(colors['bone'])

    # create the renderer and add actors
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor3DOpaque)
    
    # create the render window
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(1000, 1000)
    
    # Connect an interactor to the image viewer
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    # interactor.SetInteractorStyle(vtk.vtkInteractorStyleImage())
    
    def pickCell(interactor, event):
        
        keyPress = interactor.GetKeySym()
        
        if keyPress == 'p' or keyPress =='P':
                    
            x, y = interactor.GetEventPosition()
            
            cellPicker = vtk.vtkCellPicker()
            cellPicker.PickFromListOn()
            cellPicker.AddPickList(actor3DOpaque)
            cellPicker.SetTolerance(0.00001)
            cellPicker.Pick(x, y, 0, renderer)
            
            points = cellPicker.GetPickedPositions()
            numPoints = points.GetNumberOfPoints()
            if numPoints < 1:
                return()
            pnt = points.GetPoint(0)
            mark(*pnt)
    
    def deleteCell(interactor, event):
        
        keyPress = interactor.GetKeySym()
        
        if keyPress == 'z' or keyPress == 'Z':
            
            x, y = interactor.GetEventPosition()
            
            for point, posn in pointsDict.iteritems():
                if round(x, 0) == posn[0] or ( round(x, 0)-1 ) == posn[0] or ( round(x, 0)+1 ) == posn[0]:
                    if round(y, 0) == posn[0] or ( round(y, 0)-1 ) == posn[0] or ( round(y, 0)+1 ) == posn[0]:
                        keyPoint = point
            
            try:
                del pointsDict[keyPoint]
                #event = pointsDict.pop(keyPoint, "No point found at these coordinates")
                
                print("Deleted point #: ", keyPoint)
                print("Number of points remaining: ", str(len(pointsDict.keys())) )
                
            except KeyError:
                print("No point found at these coordinates")
                
            
    def mark(x, y, z):
        sphere = vtk.vtkSphereSource()
        sphere.SetRadius(0.005 * (reader.GetOutput().GetDimensions()[1]))
        res = 20
        sphere.SetThetaResolution(res)
        sphere.SetPhiResolution(res)
        sphere.SetCenter(x, y, z)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        
        marker = vtk.vtkActor()
        marker.SetMapper(mapper)
        renderer.AddActor(marker)
        marker.GetProperty().SetColor(1, 0, 0)
        interactor.Render()
        
        if len(pointsDict.keys()) > 0:
            pointNum = max(pointsDict.keys())
        else:
            pointNum = 0
        
        pointsList.append([pointNum + 1, round(x, 2), round(y, 2), round(z, 2)])
        pointsDict.update({pointNum + 1:[round(x, 2), round(y, 2), round(z, 2)]})
     
    pointsList = []
    pointsDict = {}
    
    interactor.AddObserver('KeyPressEvent', pickCell) #Change this to be a keypress
    interactor.AddObserver('KeyPressEvent', deleteCell)
    
    # initialise the interactor
    interactor.Initialize()
    
    # render the scene with all actors in it
    renderWindow.Render()
    
    # Start the event loop for the interactor
    interactor.Start()
    
    print(pointsList[:])
    print(pointsDict)
    
    """ marching cubes vs ray casting """
    
    
    
#     # Colour lookup table for raycasting
#     # Add tissue types as needed
#     colorTable = {}
#     colorTable = {'background':[(-4000, 0.0, 0.0, 0.0),(200, 0.0, 0.0, 0.0)],
#                   'bone':[(220, 0.83, 0.8, 0.81), (3000, 0.83, 0.8, 0.81)]}
    
#     # initialise raycast mapper
#     rayMapper = vtk.vtkGPUVolumeRayCastMapper()
#     rayMapper.SetInputConnection(filteredImg.GetOutputPort())
    
#     # map voxel intensities to colours
#     # add tissue types as needed
#     itemColor = vtk.vtkColorTransferFunction()
#     itemColor.AddRGBPoint(*(colorTable['background'][0]))
#     itemColor.AddRGBPoint(*(colorTable['background'][1]))
#     itemColor.AddRGBPoint(*(colorTable['bone'][0]))
#     itemColor.AddRGBPoint(*(colorTable['bone'][1]))
    
#     # set opacity so bone is opaque
#     # add tissue types as needed
#     itemScalarOpacity = vtk.vtkPiecewiseFunction()
#     itemScalarOpacity.AddPoint(float(colorTable['background'][0][0]), 0)
#     itemScalarOpacity.AddPoint(float(colorTable['background'][1][0]), 0)
#     itemScalarOpacity.AddPoint(float(colorTable['bone'][0][0]), 1.0)
#     itemScalarOpacity.AddPoint(float(colorTable['bone'][1][0]), 1.0)
    
#     # set properties of the items to be rendered
#     itemProperty = vtk.vtkVolumeProperty()
#     itemProperty.SetColor(itemColor)
#     itemProperty.SetScalarOpacity(itemScalarOpacity)
# #    itemProperty.SetGradientOpacity(itemGradientOpacity) 
#     itemProperty.SetInterpolationTypeToLinear()
#     itemProperty.ShadeOn()
    
#     # initialise the volume to be rendered
#     rayActor = vtk.vtkVolume()
#     rayActor.SetMapper(rayMapper)
#     rayActor.SetProperty(itemProperty)
    
#     # create the renderer and add volume
#     renderer = vtk.vtkRenderer()
#     renderer.AddViewProp(rayActor)
#     renderer.ResetCamera()
    
#     # create the render window
#     renderWindow = vtk.vtkRenderWindow()
#     renderWindow.AddRenderer(renderer)
#     renderWindow.SetSize(1000, 1000)
    
#     # Connect an interactor to the image viewer
#     interactor = vtk.vtkRenderWindowInteractor()
#     interactor.SetRenderWindow(renderWindow)
#     interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    
#     # initialise the interactor
#     interactor.Initialize()
    
#     # render the scene with all actors in it
#     renderWindow.Render()
    
#     # Start the event loop for the interactor
#     interactor.Start()


    
    """ pick your points """
    
    
        
    

    
def main():
    # Setup description
    description='''Pick points on an image

This function allows one to pick points on an image. Points are written to a plain
text file for use in other programs
'''

    # Setup argument parsing
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        prog="blPointPicker",
        description=description
    )
    parser.add_argument('input_filename', help='Input image file')
    parser.add_argument('output_filename', help='Output textfile listing picked points')
    parser.add_argument('-o', '--overwrite', action='store_true', help='Overwrite output without asking')

    # Parse and display
    args = parser.parse_args()
    print(echo_arguments('PointPicker', vars(args)))

    # Run program
    PointPicker(**vars(args))

if __name__ == '__main__':
    main()
