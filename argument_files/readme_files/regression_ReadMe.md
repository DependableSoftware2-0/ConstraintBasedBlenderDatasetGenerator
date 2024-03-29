# Regression Dataset

## Introduction
The datasets generated using [generate_regression_dataset.py](../../src/generate_regression_dataset.py) code, are in the form of a classification task but with extra information regarding scene
parameters such as camera pose, light intensity, and object-camera distance, depth of field value of camera, 2D pose of object in camera frame and other necessary details in the form of json file for each image.

<div style="display: flex; justify-content: space-between;">
  <img src="../../baseball.gif" alt="GIF" width="40%" />
  <img src="../../baseball_entropy.png" alt="Image" width="47%" />
</div>


### Folder structure
  - Dataset
      - class1
          - images
              - 000000.png
          - json_files
              - 00000.json
      - class2
          - images
              - 000000.png
          - json_files
              - 00000.json

## Generating Regression Datasets
For generating the datasets for the regression task, the parameters in the [requirements_regression.json](../requirements_regression.json) file has to be modified according to the requirement and the test case. Some of the important parameters to change are,


1. **output_path**: path for saving the generated datasets. If not provided the datasets will be saved in the results folder. For more information check [results_readme.md](../../results/readMe.md)

2. **dataset_name**: **ycb** or **robocup** . This will help is creating the class names for the 3D CAD models and also for the folder names.

3. **Num_images_per_class**: Number of images to render for one object.

4. **render_parameters**:
    * Here the default is set to CPU, so if no GPU is set then the rendering process is executed on CPU.
    * res_x,res_y: provide the resolution of the image for rendering. Higher resolution increases the rendering time.
    * render_engine: The tool works better in the CYCLES rendering engine.

5. **Trajectories**: For the distance constraint, we can generate a sequence of images in which the objects appear from far to near,

    - If the trajectories condition is set to False then only one sequence will be generated from near to far. 
    - If the condition is set to True then the dataset will be generated based on the number of trajectories.

6. **Parameters**: Enabling parameters such as `random_color` and `random_textures` affects dataset generation, only one of these two parameters has to be set to True based on the requirement for generating the dataset.
   - If `random_color` is enabled, the background for images will be a random RGB color.
   - If `random_textures` is enabled, a random PBR texture is chosen from the textures folder and applied as a background texture.
   - If `random_rotation_object` is enabled then the object present in the scene is randomly rotated.
   - If `random_placement_object` is enabled then the object is placed randomly in the image. If it is disabled then the object will always be in the center of the image.

7. **Test_cases**: These parameters are crucial for dataset generation. Set the condition to "True" inside each test case to generate corresponding datasets. For each test case, provide `min_value` and `max_value` to set limits for dataset generation. Recommended ranges for different test constraints are provided below:

   - Normal_lighting: (2,4)
   - Bright_lighting: (10,15)
   - Dark_lighting: (0.2,1.2)
   - Near_distance: (-40,-50)
   - Far_distance: (-10,-25)
   - Normal_distance: (-32,-40)
   - Blur: (0.05,0.2)
     
Based on your requirements, adjust the parameters in the test cases, render a small number of images, and check if the requirements are satisfied.
