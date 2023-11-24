# Object Detection Dataset

## CAD Models

- The present code can generate object detection dataset for the following 21 YCB objects. Download the models and place them in the models folder [ycb_models](../../blender_files/models/ycb_models).
- The following models will be imported with original size and placed in a circular arrangement and the camera moves in a circular path to render the images along with the depth and bounding box information in the BOP format.
- dataset_info = {'1': 'masterchefcan','2': 'crackerbox','3': 'sugarbox','4': 'tomatosoupcan','5': 'mustardbottle','6': 'tunafishcan','7': 'puddingbox','8': 'gelatinbox','9': 'pottedmeatcan','10': 'banana','11': 'pitcherbase','12': 'bleachcleanser','13': 'bowl','14': 'mug',
                '15': 'powerdrill','16': 'woodblock','17': 'scissors','18': 'largemarker','19': 'largeclamp','20': 'extralargeclamp','21': 'foambrick'}

## Parameters

In the file [object_detection_bop.py](../../src/object_detection_bop.py), change the following parameters based on the requirement.

1. NUM_OF_IMAGES: int, Number of images to render.
2. RES_X: int, width of the resolution
3. RES_Y: int, height of the resolution 
