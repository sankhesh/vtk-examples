#include <vtkSmartPointer.h>

#include <vtkCamera.h>
#include <vtkRenderer.h>
#include <vtkRenderWindow.h>
#include <vtkShaderProgram.h>
#include <vtkActor.h>
#include <vtkOpenGLPolyDataMapper.h>
#include <vtkProperty.h>
#include <vtkPolyDataNormals.h>

#include <vtkTransform.h>
#include <vtkTransformPolyDataFilter.h>
#include <vtkTriangleMeshPointNormals.h>
#include <vtkTriangleFilter.h>

#include <vtkNamedColors.h>
#include <vtkRenderWindowInteractor.h>

#include <vtksys/SystemTools.hxx>
#include <vtkBYUReader.h>
#include <vtkOBJReader.h>
#include <vtkPLYReader.h>
#include <vtkPolyDataReader.h>
#include <vtkSTLReader.h>
#include <vtkXMLPolyDataReader.h>
#include <vtkSphereSource.h>

#include <fstream>
#include <sstream>

namespace
{
// -----------------------------------------------------------------------
// Update a uniform in the shader for each render. We do this with a
// callback for the UpdateShaderEvent
class vtkShaderCallback : public vtkCommand
{
public:
  static vtkShaderCallback *New()
    { return new vtkShaderCallback; }
  vtkRenderer *Renderer;
  float k;
  void Execute(vtkObject *, unsigned long, void* calldata) override
  {
    vtkShaderProgram *program = reinterpret_cast<vtkShaderProgram*>(calldata);
    if (program)
    {
      program->SetUniformf("k", k);
    }
  }
  vtkShaderCallback() { this->Renderer = nullptr; this->k = 5;}

};
}

namespace
{
vtkSmartPointer<vtkPolyData> ReadPolyData(const char *fileName);
}

//----------------------------------------------------------------------------
int main(int argc, char *argv[])
{
  if (argc < 2)
  {
    std::cout << "Usage: " << argv[0] << " PerlnNoise.glsl " << "[polydataFile] [k]" << std::endl;
    return EXIT_FAILURE;
  }
  vtkSmartPointer<vtkPolyData> polyData =
    ReadPolyData(argc > 2 ? argv[2] : "");

  std::ifstream shaderFile(argv[1]);
  std::ostringstream shaderCode;
  shaderCode << shaderFile.rdbuf();

// Create a transform to rescale model
  double center[3];
  polyData->GetCenter(center);
  double bounds[6];
  polyData->GetBounds(bounds);
  double maxBound = std::max(std::max(bounds[1] - bounds[0],  bounds[3] - bounds[2]), bounds[5] - bounds[4]);

  vtkSmartPointer<vtkNamedColors> colors =
    vtkSmartPointer<vtkNamedColors>::New();

  vtkSmartPointer<vtkActor> actor =
    vtkSmartPointer<vtkActor>::New();
  vtkSmartPointer<vtkRenderer> renderer =
    vtkSmartPointer<vtkRenderer>::New();
  vtkSmartPointer<vtkOpenGLPolyDataMapper> mapper =
    vtkSmartPointer<vtkOpenGLPolyDataMapper>::New();
  renderer->SetBackground(colors->GetColor3d("SlateGray").GetData());

  vtkSmartPointer<vtkRenderWindow> renderWindow =
    vtkSmartPointer<vtkRenderWindow>::New();
  renderWindow->SetSize(640, 480);
  renderWindow->AddRenderer(renderer);
  renderer->AddActor(actor);

  vtkSmartPointer<vtkRenderWindowInteractor>  interactor =
    vtkSmartPointer<vtkRenderWindowInteractor>::New();
  interactor->SetRenderWindow(renderWindow);

  // Rescale polydata to [-1,1]
  vtkSmartPointer<vtkTransform> userTransform =
    vtkSmartPointer<vtkTransform>::New();
  userTransform->Translate(-center[0], -center[1], -center[2]);
  userTransform->Scale(1.0/maxBound, 1.0/maxBound, 1.0/maxBound);
  vtkSmartPointer<vtkTransformPolyDataFilter> transform =
    vtkSmartPointer<vtkTransformPolyDataFilter>::New();
  transform->SetTransform(userTransform);
  transform->SetInputData(polyData);

  vtkSmartPointer<vtkTriangleFilter> triangles =
    vtkSmartPointer<vtkTriangleFilter>::New();
  triangles->SetInputConnection(transform->GetOutputPort());

  vtkSmartPointer<vtkTriangleMeshPointNormals> norms =
    vtkSmartPointer<vtkTriangleMeshPointNormals>::New();
  norms->SetInputConnection(triangles->GetOutputPort());

  mapper->SetInputConnection(norms->GetOutputPort());
  mapper->ScalarVisibilityOff();

  actor->SetMapper(mapper);
  actor->GetProperty()->SetAmbientColor(0.2, 0.2, 1.0);
  actor->GetProperty()->SetDiffuseColor(1.0, 1.0, 1.0);
  actor->GetProperty()->SetSpecularColor(1.0, 1.0, 1.0);
  actor->GetProperty()->SetSpecular(0.5);
  actor->GetProperty()->SetDiffuse(0.7);
  actor->GetProperty()->SetAmbient(0.1);
  actor->GetProperty()->SetSpecularPower(100.0);
  actor->GetProperty()->SetOpacity(1.0);

  // Modify the vertex shader to pass the position of the vertex
  mapper->AddShaderReplacement(
    vtkShader::Vertex,
    "//VTK::Normal::Dec", // replace the normal block
    true, // before the standard replacements
    "//VTK::Normal::Dec\n" // we still want the default
    "  out vec4 myVertexMC;\n"
    ,
    false // only do it once
    );
  mapper->AddShaderReplacement(
    vtkShader::Vertex,
    "//VTK::Normal::Impl", // replace the normal block
    true, // before the standard replacements
    "//VTK::Normal::Impl\n" // we still want the default
    "  myVertexMC = vertexMC;\n"
    ,
    false // only do it once
    );

  // Add the code to generate noise
  // These functions need to be defined outside of main. Use the System::Dec
  // to declare and implement
  mapper->AddShaderReplacement(
    vtkShader::Fragment,
    "//VTK::System::Dec", 
    false, // before the standard replacements
    shaderCode.str(),
    false // only do it once
    );

  // define varying and uniforms for the fragment shader here
  mapper->AddShaderReplacement(
    vtkShader::Fragment,  // in the fragment shader
    "//VTK::Normal::Dec", // replace the normal block
    true, // before the standard replacements
    "//VTK::Normal::Dec\n" // we still want the default
    "  varying vec4 myVertexMC;\n"
    "  uniform float k = 1.0;\n"
    ,
    false // only do it once
    );

  mapper->AddShaderReplacement(
    vtkShader::Fragment,  // in the fragment shader
    "//VTK::Light::Impl", // replace the light block
    false, // after the standard replacements
    "//VTK::Light::Impl\n" // we still want the default calc
    "  vec3 noisyColor;\n"
    "  noisyColor.r = noise(k * 10.0 * myVertexMC);\n"
    "  noisyColor.g = noise(k * 11.0 * myVertexMC);\n"
    "  noisyColor.b = noise(k * 12.0 * myVertexMC);\n"
    "  /* map ranges of noise values into different colors */\n"
    "  int i;\n"
    "  float lowerValue = .3;\n"
    "  float upperValue = .6;\n"
    "  for ( i=0; i<3; i+=1)\n"
    "  {\n"
    "    noisyColor[i] = (noisyColor[i] + 1.0) / 2.0;\n"
    "    if (noisyColor[i] < lowerValue) \n"
    "    {\n"
    "      noisyColor[i] = lowerValue;\n"
    "    }\n"
    "    else\n"
    "    {\n"
    "      if (noisyColor[i] < upperValue)\n"
    "      {\n"
    "        noisyColor[i] = upperValue;\n"
    "      }\n"
    "      else\n"
    "      {\n"
    "        noisyColor[i] = 1.0;\n"
    "      }\n"
    "    }\n"
    "  }\n"
    "  fragOutput0.rgb = opacity * vec3(ambientColor + noisyColor * diffuse + specular);\n"
    "  fragOutput0.a = opacity;\n"    
    ,
    false // only do it once
    );
  vtkSmartPointer<vtkShaderCallback> myCallback =
    vtkSmartPointer<vtkShaderCallback>::New();
  myCallback->Renderer = renderer;
  if (argc == 2 || argc == 3)
  {
    myCallback->k = 1;
  }
  else
  {
  myCallback->k = atof(argv[3]);
  }
  mapper->AddObserver(vtkCommand::UpdateShaderEvent, myCallback);

  renderWindow->Render();
  renderer->GetActiveCamera()->SetPosition(-.3, 0, .08);
  renderer->GetActiveCamera()->SetFocalPoint(0,0,0);
  renderer->GetActiveCamera()->SetViewUp(.26, 0.0, .96);
  renderer->ResetCamera();
  renderer->GetActiveCamera()->Zoom(1.5);
  renderWindow->Render();
  interactor->Start();

  transform->GetOutput()->GetBounds(bounds);
  std::cout << "Range: "
            << " x " << bounds[1] - bounds[0]
            << " y " << bounds[3] - bounds[2]
            << " y " << bounds[5] - bounds[4]
            << std::endl;
  return EXIT_SUCCESS;
}

namespace
{
vtkSmartPointer<vtkPolyData> ReadPolyData(const char *fileName)
{
  vtkSmartPointer<vtkPolyData> polyData;
  std::string extension = vtksys::SystemTools::GetFilenameExtension(std::string(fileName));
  if (extension == ".ply")
  {
    vtkSmartPointer<vtkPLYReader> reader =
      vtkSmartPointer<vtkPLYReader>::New();
    reader->SetFileName (fileName);
    reader->Update();
    polyData = reader->GetOutput();
  }
  else if (extension == ".vtp")
  {
    vtkSmartPointer<vtkXMLPolyDataReader> reader =
      vtkSmartPointer<vtkXMLPolyDataReader>::New();
    reader->SetFileName (fileName);
    reader->Update();
    polyData = reader->GetOutput();
  }
  else if (extension == ".obj")
  {
    vtkSmartPointer<vtkOBJReader> reader =
      vtkSmartPointer<vtkOBJReader>::New();
    reader->SetFileName (fileName);
    reader->Update();
    polyData = reader->GetOutput();
  }
  else if (extension == ".stl")
  {
    vtkSmartPointer<vtkSTLReader> reader =
      vtkSmartPointer<vtkSTLReader>::New();
    reader->SetFileName (fileName);
    reader->Update();
    polyData = reader->GetOutput();
  }
  else if (extension == ".vtk")
  {
    vtkSmartPointer<vtkPolyDataReader> reader =
      vtkSmartPointer<vtkPolyDataReader>::New();
    reader->SetFileName (fileName);
    reader->Update();
    polyData = reader->GetOutput();
  }
  else if (extension == ".g")
  {
    vtkSmartPointer<vtkBYUReader> reader =
      vtkSmartPointer<vtkBYUReader>::New();
    reader->SetGeometryFileName (fileName);
    reader->Update();
    polyData = reader->GetOutput();
  }
  else
  {
    vtkSmartPointer<vtkSphereSource> source =
      vtkSmartPointer<vtkSphereSource>::New();
    source->SetPhiResolution(25);
    source->SetThetaResolution(25);
    source->Update();
    polyData = source->GetOutput();
  }
  return polyData;
}
}
