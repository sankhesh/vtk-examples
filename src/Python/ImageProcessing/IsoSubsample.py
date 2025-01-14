#!/usr/bin/env python

import vtk


def main():
    colors = vtk.vtkNamedColors()

    file_name = get_program_parameters()

    # Read the image.
    reader_factory = vtk.vtkImageReader2Factory()
    reader = reader_factory.CreateImageReader2(file_name)
    reader.SetFileName(file_name)
    reader.Update()

    # Smoothed pipeline.
    smooth = vtk.vtkImageGaussianSmooth()
    smooth.SetDimensionality(3)
    smooth.SetInputConnection(reader.GetOutputPort())
    smooth.SetStandardDeviations(1.75, 1.75, 0.0)
    smooth.SetRadiusFactor(2)

    subsample_smoothed = vtk.vtkImageShrink3D()
    subsample_smoothed.SetInputConnection(smooth.GetOutputPort())
    subsample_smoothed.SetShrinkFactors(4, 4, 1)

    iso_smoothed = vtk.vtkImageMarchingCubes()
    iso_smoothed.SetInputConnection(smooth.GetOutputPort())
    iso_smoothed.SetValue(0, 1150)

    iso_smoothed_mapper = vtk.vtkPolyDataMapper()
    iso_smoothed_mapper.SetInputConnection(iso_smoothed.GetOutputPort())
    iso_smoothed_mapper.ScalarVisibilityOff()

    iso_smoothed_actor = vtk.vtkActor()
    iso_smoothed_actor.SetMapper(iso_smoothed_mapper)
    iso_smoothed_actor.GetProperty().SetColor(colors.GetColor3d("Ivory"))

    # Unsmoothed pipeline.
    # Sub sample the data.
    subsample = vtk.vtkImageShrink3D()
    subsample.SetInputConnection(reader.GetOutputPort())
    subsample.SetShrinkFactors(4, 4, 1)

    iso = vtk.vtkImageMarchingCubes()
    iso.SetInputConnection(subsample.GetOutputPort())
    iso.SetValue(0, 1150)

    iso_mapper = vtk.vtkPolyDataMapper()
    iso_mapper.SetInputConnection(iso.GetOutputPort())
    iso_mapper.ScalarVisibilityOff()

    iso_actor = vtk.vtkActor()
    iso_actor.SetMapper(iso_mapper)
    iso_actor.GetProperty().SetColor(colors.GetColor3d("Ivory"))

    # The rendering Pipeline.

    # Setup the render window, renderer, and interactor.
    left_viewport = [0.0, 0.0, 0.5, 1.0]
    right_viewport = [0.5, 0.0, 1.0, 1.0]

    renderer_left = vtk.vtkRenderer()
    renderer_left.SetViewport(left_viewport)

    renderer_right = vtk.vtkRenderer()
    renderer_right.SetViewport(right_viewport)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer_left)
    render_window.AddRenderer(renderer_right)

    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    renderer_left.AddActor(iso_actor)
    renderer_right.AddActor(iso_smoothed_actor)

    renderer_left.GetActiveCamera().SetFocalPoint(0.0, 0.0, 0.0)
    renderer_left.GetActiveCamera().SetPosition(0.0, -1.0, 0.0)
    renderer_left.GetActiveCamera().SetViewUp(0.0, 0.0, -1.0)
    renderer_left.ResetCamera()
    renderer_left.GetActiveCamera().Azimuth(-20.0)
    renderer_left.GetActiveCamera().Elevation(20.0)
    renderer_left.ResetCameraClippingRange()

    renderer_left.SetBackground(colors.GetColor3d("SlateGray"))
    renderer_right.SetBackground(colors.GetColor3d("LightSlateGray"))
    renderer_right.SetActiveCamera(renderer_left.GetActiveCamera())

    render_window.SetSize(640, 480)
    render_window.SetWindowName('IsoSubsample')
    render_window.Render()

    render_window_interactor.Start()


def get_program_parameters():
    import argparse
    description = 'This figure demonstrates aliasing that occurs when a high-frequency signal is subsampled.'
    epilogue = '''
    High frequencies appear as low frequency artifacts.
    The left image is an isosurface of a skull after subsampling.
    The right image used a low-pass filter before subsampling to reduce aliasing.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='FullHead.mhd.')
    args = parser.parse_args()
    return args.filename


if __name__ == '__main__':
    main()
