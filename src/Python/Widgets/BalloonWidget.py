#!/usr/bin/env python
import vtk


def main():
    colors = vtk.vtkNamedColors()

    # Sphere
    sphereSource = vtk.vtkSphereSource()
    sphereSource.SetCenter(-4.0, 0.0, 0.0)
    sphereSource.SetRadius(4.0)

    sphereMapper = vtk.vtkPolyDataMapper()
    sphereMapper.SetInputConnection(sphereSource.GetOutputPort())

    sphereActor = vtk.vtkActor()
    sphereActor.SetMapper(sphereMapper)
    sphereActor.GetProperty().SetColor(colors.GetColor3d('MistyRose'))

    # Regular Polygon
    regularPolygonSource = vtk.vtkRegularPolygonSource()
    regularPolygonSource.SetCenter(4.0, 0.0, 0.0)
    regularPolygonSource.SetRadius(4.0)

    regularPolygonMapper = vtk.vtkPolyDataMapper()
    regularPolygonMapper.SetInputConnection(regularPolygonSource.GetOutputPort())

    regularPolygonActor = vtk.vtkActor()
    regularPolygonActor.SetMapper(regularPolygonMapper)
    regularPolygonActor.GetProperty().SetColor(colors.GetColor3d('Cornsilk'))

    # A renderer and render window
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetWindowName('BalloonWidget')

    # An interactor
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    # Create the widget
    balloonRep = vtk.vtkBalloonRepresentation()
    balloonRep.SetBalloonLayoutToImageRight()

    balloonWidget = vtk.vtkBalloonWidget()
    balloonWidget.SetInteractor(renderWindowInteractor)
    balloonWidget.SetRepresentation(balloonRep)
    balloonWidget.AddBalloon(sphereActor, 'This is a sphere')
    balloonWidget.AddBalloon(regularPolygonActor, 'This is a regular polygon')

    # Add the actors to the scene
    renderer.AddActor(sphereActor)
    renderer.AddActor(regularPolygonActor)
    renderer.SetBackground(colors.GetColor3d('SlateGray'))

    # Render an image (lights and cameras are created automatically)
    renderWindow.Render()
    balloonWidget.EnabledOn()

    # Begin mouse interaction
    renderWindowInteractor.Start()
    renderWindowInteractor.Initialize()


if __name__ == '__main__':
    main()
