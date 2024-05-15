# Constraint based Dataset Generator
Blender based dataset generation by setting some fixed constraint and randomized other parameters such as camera pose, light intensity, and object-camera distance, depth of field value of camera, 2D pose of object in camera frame and other necessary details.

<div style="display: flex; justify-content: space-between;">
  <img src="../../baseball.gif" alt="GIF" width="40%" />
  <img src="../../baseball_entropy.png" alt="Image" width="47%" />
</div>

## Installation 

* Download blender (version 3.6) from the official website [blender.org](https://www.blender.org/download/).
* Clone the repository and install the requirements
```
$> pip install requirements.txt
```

## Usage

* Dowlnoad the ycb CAD models using [download_ycb_models.py](download_ycb_models.py).
  ```
  python3 download_ycb_models.py
  ```

## Classification dataset
* Set the parameters in the classification config file, [requirements_classification.json](argument_files/requirements_classification.json) file in the argument_files folder.
* For information on setting the parameters check the [classification_ReadMe.md](argument_files/readme_files/classification_ReadMe.md) file 

```
$> cd src/
$> blender -b -P generate_classification_dataset.py 
```

## Regression dataset
* Set the parameters in the regression config file, [requirements_regression.json](argument_files/requirements_regression.json) file in the argument_files folder.
* For information on setting the parameters check the [regression_ReadMe.md](argument_files/readme_files/regression_ReadMe.md) file
```
$> cd src/
$> blender -b -P generate_regression_dataset.py 
```


## Object detection dataset
* For information on setting the parameters check the [object_detection_ReadMe.md](argument_files/readme_files/object_detection_ReadMe.md) file
```
$> cd src/
$> blender -b -P object_detection_bop.py 
```
