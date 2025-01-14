#include <vtkActor.h>
#include <vtkBillboardTextActor3D.h>
#include <vtkCallbackCommand.h>
#include <vtkMath.h>
#include <vtkNew.h>
#include <vtkPolyData.h>
#include <vtkPolyDataMapper.h>
#include <vtkProperty.h>
#include <vtkRenderWindow.h>
#include <vtkRenderWindowInteractor.h>
#include <vtkRenderer.h>
#include <vtkNew.h>
#include <vtkSphereSource.h>
#include <vtkTextProperty.h>
#include <vtkNamedColors.h>
#include <vtkNew.h>
#include <vtkProperty.h>

#include <sstream>

namespace {
void ActorCallback(vtkObject* caller, long unsigned int vtkNotUsed(eventId),
                   void* clientData, void* vtkNotUsed(callData))
{
  auto textActor =
      static_cast<vtkBillboardTextActor3D*>(clientData);
  auto actor = static_cast<vtkActor*>(caller);
  std::ostringstream label;
  label << std::setprecision(3) << actor->GetPosition()[0] << ", "
        << actor->GetPosition()[1] << ", " << actor->GetPosition()[2]
        << std::endl;
  textActor->SetPosition(actor->GetPosition());
  textActor->SetInput(label.str().c_str());
}
}

int main(int, char*[])
{
  vtkNew<vtkNamedColors> colors;

  // For testing
  vtkMath::RandomSeed(8775070);

  // Create a sphere
  vtkNew<vtkSphereSource> sphereSource;
  sphereSource->SetCenter(0.0, 0.0, 0.0);
  sphereSource->SetRadius(1.0);

  // Create an actor
  vtkNew<vtkPolyDataMapper> mapper2;
  mapper2->SetInputConnection(sphereSource->GetOutputPort());
  vtkNew<vtkActor> actor2;
  actor2->SetMapper(mapper2);
  actor2->SetPosition(0, 0, 0);
  actor2->GetProperty()->SetColor(colors->GetColor3d("Peacock").GetData());

  // Create a renderer
  vtkNew<vtkRenderer> renderer;
  renderer->SetBackground(colors->GetColor3d("DarkSlateGray").GetData());
  renderer->AddActor(actor2);

  // Create a render window
  vtkNew<vtkRenderWindow> renderWindow;
  renderWindow->AddRenderer(renderer);
  renderWindow->SetWindowName("BillboardTextActor3D");

  // Create an interactor
  vtkNew<vtkRenderWindowInteractor> renderWindowInteractor;
  renderWindowInteractor->SetRenderWindow(renderWindow);

  for (int i = 0; i < 10; ++i)
  {
    // Create a mapper
    vtkNew<vtkPolyDataMapper> mapper;
    mapper->SetInputConnection(sphereSource->GetOutputPort());

    // Create an actor
    vtkNew<vtkActor> actor;
    actor->SetMapper(mapper);
    actor->SetPosition(0, 0, 0);
    actor->GetProperty()->SetColor(colors->GetColor3d("MistyRose").GetData());

    // Setup the text and add it to the renderer
    vtkNew<vtkBillboardTextActor3D> textActor;
    textActor->SetInput("");
    textActor->SetPosition(actor->GetPosition());
    textActor->GetTextProperty()->SetFontSize(12);
    textActor->GetTextProperty()->SetColor(
        colors->GetColor3d("Gold").GetData());
    textActor->GetTextProperty()->SetJustificationToCentered();

    renderer->AddActor(actor);
    renderer->AddActor(textActor);

    vtkNew<vtkCallbackCommand> actorCallback;
    actorCallback->SetCallback(ActorCallback);
    actorCallback->SetClientData(textActor);
    actor->AddObserver(vtkCommand::ModifiedEvent, actorCallback);
    actor->SetPosition(vtkMath::Random(-10.0, 10.0),
                       vtkMath::Random(-10.0, 10.0),
                       vtkMath::Random(-10.0, 10.0));
  }
  renderWindow->Render();
  renderWindowInteractor->Start();

  return EXIT_SUCCESS;
}
