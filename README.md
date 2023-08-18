# constraint_based_dataset_generator
Blender based dataset generation using setting soem fixed constraint and randomized other settings.

## Installation 

ToDO

## Usage
1. First fill the config file in [requirements_classification.json](argument_files/requirements_classification.json) file in argument_files folder.
    * Edit the "output_path" with path of the outputs
    * Number of images per class
    * Change the remaining as per your requirements 
2.  Execution
```
$> blender -b -P src/generate_classification_dataset.py 
```
