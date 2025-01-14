#!/usr/bin/env python

'''
'''

import vtk


def main():
    colors = vtk.vtkNamedColors()

    fileName = get_program_parameters()

    renderer1 = vtk.vtkRenderer()
    renderer1.SetViewport(0.0, 0.0, 0.5, 1.0)

    renderer2 = vtk.vtkRenderer()
    renderer2.SetViewport(0.5, 0.0, 1.0, 1.0)

    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer1)
    renderWindow.AddRenderer(renderer2)
    renderWindow.SetWindowName('StripFran')
    

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)

    # Create a cyberware source.
    #
    cyber = vtk.vtkPolyDataReader()
    cyber.SetFileName(fileName)

    deci = vtk.vtkDecimatePro()
    deci.SetInputConnection(cyber.GetOutputPort())
    deci.SetTargetReduction(0.7)
    deci.PreserveTopologyOn()

    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(deci.GetOutputPort())

    mask = vtk.vtkMaskPolyData()
    mask.SetInputConnection(deci.GetOutputPort())
    mask.SetOnRatio(2)

    cyberMapper = vtk.vtkPolyDataMapper()
    cyberMapper.SetInputConnection(mask.GetOutputPort())

    cyberActor = vtk.vtkActor()
    cyberActor.SetMapper(cyberMapper)
    cyberActor.GetProperty().SetColor(colors.GetColor3d('Flesh'))

    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(cyber.GetOutputPort())

    stripperMask = vtk.vtkMaskPolyData()
    stripperMask.SetInputConnection(stripper.GetOutputPort())
    stripperMask.SetOnRatio(2)

    stripperMapper = vtk.vtkPolyDataMapper()
    stripperMapper.SetInputConnection(stripperMask.GetOutputPort())

    stripperActor = vtk.vtkActor()
    stripperActor.SetMapper(stripperMapper)
    stripperActor.GetProperty().SetColor(colors.GetColor3d('Flesh'))

    # Add the actors to the renderer, set the background and size.
    #
    renderer1.AddActor(stripperActor)
    renderer2.AddActor(cyberActor)
    renderer1.SetBackground(colors.GetColor3d('Wheat'))
    renderer2.SetBackground(colors.GetColor3d('Papaya_Whip'))
    renderWindow.SetSize(1024, 640)

    # Render the image.
    #
    cam1 = vtk.vtkCamera()
    cam1.SetFocalPoint(0, 0, 0)
    cam1.SetPosition(1, 0, 0)
    cam1.SetViewUp(0, 1, 0)
    renderer1.SetActiveCamera(cam1)
    renderer2.SetActiveCamera(cam1)
    renderer1.ResetCamera()
    cam1.Azimuth(30)
    cam1.Elevation(30)
    cam1.Dolly(1.4)
    renderer1.ResetCameraClippingRange()

    interactor.Start()


def get_program_parameters():
    import argparse
    description = 'Triangle strip examples.'
    epilogue = '''
    a) Structured triangle mesh consisting of 134 strips each of 390 triangles (stripF.tcl).
    
    b) Unstructured triangle mesh consisting of 2227 strips of average length 3.94,
        longest strip 101 triangles.
        Images are generated by displaying every other triangle strip (uStripeF.tcl).
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename1', help='fran_cut.vtk.')
    args = parser.parse_args()
    return args.filename1


if __name__ == '__main__':
    main()
