#!/usr/bin/env python

# Python example translated directly from Tcl test
# [vtk_source]/Graphics/Testing/Tcl/progGlyphs.tcl

import vtk


def main():
    res = 6
    plane = vtk.vtkPlaneSource()
    plane.SetResolution(res, res)
    colors = vtk.vtkElevationFilter()
    colors.SetInputConnection(plane.GetOutputPort())
    colors.SetLowPoint(-0.25, -0.25, -0.25)
    colors.SetHighPoint(0.25, 0.25, 0.25)
    planeMapper = vtk.vtkPolyDataMapper()
    planeMapper.SetInputData(colors.GetPolyDataOutput())
    planeActor = vtk.vtkActor()
    planeActor.SetMapper(planeMapper)
    planeActor.GetProperty().SetRepresentationToWireframe()

    # create simple poly data so we can apply glyph
    squad = vtk.vtkSuperquadricSource()

    def Glyph():
        """
        # procedure for generating glyphs
        :return:
        """
        xyz = glypher.GetPoint()
        x = xyz[0]
        y = xyz[1]
        length = glypher.GetInput(0).GetLength()
        scale = length / (2.0 * res)

        squad.SetScale(scale, scale, scale)
        squad.SetCenter(xyz)
        squad.SetPhiRoundness(abs(x) * 5.0)
        squad.SetThetaRoundness(abs(y) * 5.0)

    glypher = vtk.vtkProgrammableGlyphFilter()
    glypher.SetInputConnection(colors.GetOutputPort())
    glypher.SetSourceConnection(squad.GetOutputPort())
    glypher.SetGlyphMethod(Glyph)
    glyphMapper = vtk.vtkPolyDataMapper()
    glyphMapper.SetInputConnection(glypher.GetOutputPort())
    glyphActor = vtk.vtkActor()
    glyphActor.SetMapper(glyphMapper)

    colors = vtk.vtkNamedColors()

    # Create the rendering stuff
    ren1 = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.SetMultiSamples(0)
    renWin.AddRenderer(ren1)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    ren1.AddActor(planeActor)
    ren1.AddActor(glyphActor)
    ren1.SetBackground(colors.GetColor3d('Silver'))

    renWin.SetSize(450, 450)
    renWin.SetWindowName('ProgrammableGlyphs')
    renWin.Render()

    ren1.GetActiveCamera().Zoom(1.3)

    iren.Start()


if __name__ == '__main__':
    main()
