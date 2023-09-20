# Constraint based Dataset Generator
Blender based dataset generation by setting soeme fixed constraint and randomized other settings.

## Installation 


ToDO

## Usage

1. First fill the config file in [requirements_classification.json](argument_files/requirements_classification.json) file in argument_files folder.
    * Edit the "output_path" with the path of the outputs
    * Number of images per class
    * Change the remaining as per your requirements 
2.  Execution


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
* Set the parameters in the regression config file, [requirements_object_detection.json](argument_files/requirements_object_detection.json) file in the argument_files folder.
* For information on setting the parameters check the [object_detection_ReadMe.md](argument_files/readme_files/object_detection_ReadMe.md) file
```
$> cd src/
$> blender -b -P object_detection_bop.py 
```
