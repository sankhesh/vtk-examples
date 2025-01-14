#!/usr/bin/env python

import vtk


def main():
    # vtkFlyingEdges3D was introduced in VTK >= 8.2
    use_flying_edges = vtk_version_ok(8, 2, 0)

    file_name = get_program_parameters()

    colors = vtk.vtkNamedColors()

    # Create the RenderWindow, Renderer and Interactor.
    #

    ren = vtk.vtkRenderer()

    ren_win = vtk.vtkRenderWindow()
    ren_win.AddRenderer(ren)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    # Create the pipeline.
    #

    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(file_name)
    reader.Update()

    locator = vtk.vtkMergePoints()
    locator.SetDivisions(64, 64, 92)
    locator.SetNumberOfPointsPerBucket(2)
    locator.AutomaticOff()

    if use_flying_edges:
        try:
            using_marching_cubes = False
            iso = vtk.vtkDiscreteFlyingEdges3D()
        except AttributeError:
            using_marching_cubes = True
            iso = vtk.vtkDiscreteMarchingCubes()
    else:
        using_marching_cubes = True
        iso = vtk.vtkDiscreteMarchingCubes()
    iso.SetInputConnection(reader.GetOutputPort())
    iso.ComputeGradientsOn()
    iso.ComputeScalarsOff()
    iso.SetValue(0, 1150)
    if using_marching_cubes:
        iso.SetLocator(locator)

    iso_mapper = vtk.vtkPolyDataMapper()
    iso_mapper.SetInputConnection(iso.GetOutputPort())
    iso_mapper.ScalarVisibilityOff()

    iso_actor = vtk.vtkActor()
    iso_actor.SetMapper(iso_mapper)
    iso_actor.GetProperty().SetColor(colors.GetColor3d('Ivory'))

    outline = vtk.vtkOutlineFilter()
    outline.SetInputConnection(reader.GetOutputPort())

    outline_mapper = vtk.vtkPolyDataMapper()
    outline_mapper.SetInputConnection(outline.GetOutputPort())

    outline_actor = vtk.vtkActor()
    outline_actor.SetMapper(outline_mapper)

    # Add the actors to the renderer, set the background and size.
    #
    ren.AddActor(outline_actor)
    ren.AddActor(iso_actor)
    ren.SetBackground(colors.GetColor3d('SlateGray'))
    ren.GetActiveCamera().SetFocalPoint(0, 0, 0)
    ren.GetActiveCamera().SetPosition(0, -1, 0)
    ren.GetActiveCamera().SetViewUp(0, 0, -1)
    ren.ResetCamera()
    ren.GetActiveCamera().Dolly(1.5)
    ren.ResetCameraClippingRange()

    ren_win.SetSize(640, 480)
    ren_win.SetWindowName('HeadBone')

    ren_win.Render()
    iren.Start()


def get_program_parameters():
    import argparse
    description = 'Marching cubes surface of human bone.'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='FullHead.mhd.')
    args = parser.parse_args()
    return args.filename


def vtk_version_ok(major, minor, build):
    """
    Check the VTK version.

    :param major: Major version.
    :param minor: Minor version.
    :param build: Build version.
    :return: True if the requested VTK version is greater or equal to the actual VTK version.
    """
    needed_version = 10000000000 * int(major) + 100000000 * int(minor) + int(build)
    try:
        vtk_version_number = vtk.VTK_VERSION_NUMBER
    except AttributeError:  # as error:
        ver = vtk.vtkVersion()
        vtk_version_number = 10000000000 * ver.GetVTKMajorVersion() + 100000000 * ver.GetVTKMinorVersion() \
                             + ver.GetVTKBuildVersion()
    if vtk_version_number >= needed_version:
        return True
    else:
        return False


if __name__ == '__main__':
    main()
