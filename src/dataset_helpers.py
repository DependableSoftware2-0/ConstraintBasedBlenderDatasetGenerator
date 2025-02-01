# import modules
import os
import sys
import argparse
import numpy as np
import json
from pathlib import Path
import time
import bpy
import random
import skfuzzy
from skfuzzy import control as ctrl


# Refactor the code for changing the utilites to utils folder

from blender_utils import Blender_helper

Blender_helper = Blender_helper()

class Dataset_helper():

    def __init__(self) -> None:
        pass

    def get_test_cases(self,json_object):
        """
        This fuction returs the list of test cases for generating different datasets.

        Args: json_object - Json object which contains the data from requirements file.
        return : list(str)
        """
        
        assert type(json_object)==dict,"Json object should be of the form dict"

        test_cases = []
        for item in json_object['Test_cases'].items():
            if json_object['Test_cases'][item[0]]['condition'] == 'True':
                test_cases.append(item[0])
        return test_cases

    def get_parameters(self,json_object):
        """
        This function returns the list of parameters that are used to modify the datasets.

        Args: json_object - Json object which contains the data from requirements file.
        return : list(str)
        """

        assert type(json_object)==dict,"Json object should be of the form dict"
        parameters = []
        for item in json_object['Parameters'].items():
            if json_object['Parameters'][item[0]] == 'True':
                parameters.append(item[0])
        return parameters

    def get_min_max_values(self,test_case,json_object):
        """
        This function returns the minimum and maximum values from the json object for the particular test case
        
        Args:
            test_case: str
            json_object : json_object
        
        """
        min_value = json_object['Test_cases'][str(test_case)]['min_value']
        max_value = json_object['Test_cases'][str(test_case)]['max_value']

        return float(min_value),float(max_value)

    def get_object_render_per_split(self,json_object,num_images_per_class):

        test_cases = self.get_test_cases(json_object=json_object)
        obj_render_list = []
        for condition in test_cases:
            obj_render_list.append((condition,num_images_per_class))
        return obj_render_list  


    def compute_uncertianty_distance(self,focal_length):
        uncertainty_value = 0.0
        # Range of the domains
        distance = ctrl.Antecedent(np.arange(40,110,1),'distance')
        uncertainty = ctrl.Consequent(np.arange(0,2.7,0.01),'uncertainty')

        # Membership function for Light
        distance['far'] = skfuzzy.trimf(distance.universe, [40,40,55])
        distance['little_far'] = skfuzzy.trimf(distance.universe,[50,55,60])
        distance['normal'] = skfuzzy.trimf(distance.universe, [58,65,72])
        distance['little_near'] = skfuzzy.trimf(distance.universe,[70,80,90])
        distance['near'] = skfuzzy.trimf(distance.universe, [80, 110,110])


         # Membership function for Uncertainty
        # uncertainty['Low'] = fuzz.sigmf(uncertainty.universe, center, width_control)
        # uncertainty['Low'] = skfuzzy.trimf(uncertainty.universe,[0,0,0.5])
        uncertainty['Low']= skfuzzy.zmf(uncertainty.universe, 0,0.3)
        uncertainty['Little_high']= skfuzzy.gaussmf(uncertainty.universe, 0.8,0.05)
        # uncertainty['High'] = skfuzzy.trimf(uncertainty.universe,[0.6,1,1])
        uncertainty['High'] = skfuzzy.smf(uncertainty.universe, 1.0, 2.7)
        uncertainty['Medium'] = skfuzzy.gaussmf(uncertainty.universe, 0.5, 0.05)


        # Defining the fuzzy rules
        rule1 = ctrl.Rule(distance['far'] ,uncertainty['High'])
        rule2 = ctrl.Rule(distance['normal'],uncertainty['Low'])
        rule3 = ctrl.Rule(distance['little_far'] ,uncertainty['Little_high'])
        rule4 = ctrl.Rule(distance['near'] ,uncertainty['High'])
        rule5 = ctrl.Rule(distance['little_near'] ,uncertainty['Little_high'])

        # Control system for calculating uncertainty
        uncertainty_ctrl = ctrl.ControlSystem([rule1,rule2,rule3,rule4,rule5])
        uncertainty_check = ctrl.ControlSystemSimulation(uncertainty_ctrl)
        uncertainty_check.input['distance'] = focal_length
        uncertainty_check.compute()
        uncertainty_value = uncertainty_check.output['uncertainty']

        return round(uncertainty_value,6)
    
    def compute_uncertianty_lighting(self,light_value):
        """ computes uncertainty for the light values  from blender
        """
        uncertainty_value = 0.0
        # Range of the domains
        light = ctrl.Antecedent(np.arange(0,25,0.1),'light')
        uncertainty = ctrl.Consequent(np.arange(0,1.0,0.01),'uncertainty')

        # Membership function for Light
        light['dark'] = skfuzzy.trimf(light.universe, [0,0,2])
        light['little_dark'] = skfuzzy.trimf(light.universe,[1.5,2.5,3.5])
        light['normal'] = skfuzzy.trimf(light.universe, [2.8,6,8])
        light['little_bright'] = skfuzzy.trimf(light.universe,[7.5,11,16])
        light['bright'] = skfuzzy.trimf(light.universe, [15, 19, 25])

        # Membership function for Uncertainty
        # uncertainty['Low'] = fuzz.sigmf(uncertainty.universe, center, width_control)
        uncertainty['Low'] = skfuzzy.trimf(uncertainty.universe,[0,0,0.5])
        uncertainty['High'] = skfuzzy.trimf(uncertainty.universe,[0.6,1,1])
        # uncertainty['High'] = fuzz.sigmf(uncertainty.universe, center, width_control)

        # Defining the fuzzy rules
        rule1 = ctrl.Rule(light['bright'] ,uncertainty['High'])
        rule2 = ctrl.Rule(light['normal'],uncertainty['Low'])
        rule3 = ctrl.Rule(light['little_bright'] ,uncertainty['High'])
        rule4 = ctrl.Rule(light['dark'] ,uncertainty['High'])
        rule5 = ctrl.Rule(light['little_dark'] ,uncertainty['High'])

        # Control system for calculating uncertainty
        uncertainty_ctrl = ctrl.ControlSystem([rule1,rule2,rule3,rule4,rule5])
        uncertainty_check = ctrl.ControlSystemSimulation(uncertainty_ctrl)
        uncertainty_check.input['light'] = light_value
        uncertainty_check.compute()
        uncertainty_value = uncertainty_check.output['uncertainty']

        # print("Light value : ",light_value , "uncertainty_value : ",round(uncertainty_value,2))

        return uncertainty_value


    def save_as_json_file(self,file_path,parameters_dict):
        
        with open(str(file_path),'w',encoding='utf-8') as f:
            json.dump(parameters_dict, f, ensure_ascii=False, indent=4)

        return None


    def generate_classification_dataset(self,json_object,dataset_name):
        
        # create dict to store the parameters
        parameters_dict = {}
        
        distractor_obj = None
        material = None
        # Modify the code later refactor
        # Get the parameters from the json object
        output_path = Path(str(json_object['output_path']))
        num_images_per_class = int(json_object['Num_images_per_class'])
        textures_path = str(json_object['textures_path'])

        
        # Get the test cases list
        test_cases = self.get_test_cases(json_object=json_object)

        # Get the parameters list
        parameters = self.get_parameters(json_object=json_object)

        # Load the objects into the scene. check if you may need to create a .blend file before implementing this.

        # Set the camera and light with default values.

        # Set the scene no collision

        # Set the image resolution ---> get the value from the json requirements

        # Get the names of the objects.
        obj_names = Blender_helper.get_object_names(background_plane_name='Floor')
        
        # Set all objects to be hidden initially while rendering.
        Blender_helper.hide_objects(obj_names=obj_names)

        new_obj_names = []
        distractor_obj_names = []
        for name in obj_names:
            if name.startswith('ycb'):
                print("YCB OBJECT : ",name)
                distractor_obj_names.append(name)
            else:
                new_obj_names.append(name)
        
        if len(new_obj_names)!=0:
            pass
        obj_names = new_obj_names
        num_objects = len(obj_names)

        # Get tuple of test_cases and numnber of images to render.
        obj_renders_per_split = self.get_object_render_per_split(json_object,num_images_per_class)
        total_render_count = sum([num_objects*r[1] for r in obj_renders_per_split])
        
        

        # Create start index for the images and starting time
        start_time = time.time()
        camera = bpy.data.objects['Camera']
        # Loop through each split of the test cases for generating the test datasets.
        # test case == split name
        print("Rendering objects names",obj_names)
        for test_case,renders_per_object in obj_renders_per_split:
            print(f'Starting split: {test_case} | Total renders: {renders_per_object * num_objects}')
            print('**'*30)

            # Loop through the objects present in the scene.
            for obj_name in obj_names:
                
                # Set the camera to track the object: object will change every time.


                # print the name of the object.
                print(f'Starting object: {test_case}/{obj_name}')
                print('..'*30)

                # get the object and make it visible during rendering.
                obj_to_render = Blender_helper.get_object(obj_name=obj_name)
                obj_to_render.hide_render = False


                start_idx = 0
                # Loop though number of images to render and render the images.
                for i in range(start_idx,start_idx+renders_per_object):
                    
                    if distractor_obj_names != []:
                        # Unhide distractor objects randomly
                        distractor_obj = Blender_helper.get_object(obj_name=random.choice(distractor_obj_names))
                        distractor_obj.hide_render = False
                        # Randomly rotate distractor object
                        Blender_helper.set_random_rotation(distractor_obj)


                    # Check for the parameters and generate images accordingly.
                    if str('random_rotation') in parameters:
                        Blender_helper.set_random_rotation(obj_to_render)
                    else:
                        obj_to_render.rotation_euler = (0.0,0.0,0.0)

                    if str('random_lighting') in parameters:
                        Blender_helper.set_random_lighting(light_source_name='Sun',min_value=3,max_value=7)
                    else:
                        bpy.data.lights['Sun'].energy = 5

                    if str('random_distance') in parameters:
                        Blender_helper.set_random_focal_length(camera_name='Camera',min_value=45,max_value=65)
                    else:
                        bpy.data.cameras['Camera'].lens = 70 #min_value=100,max_value=120)

                    if str('random_color') in parameters:
                        # Debug this code later 'NoneType' object has no attribute 'node_tree' do you actually need this?
                        Blender_helper.set_random_background_color(obj_name='Floor')
                    elif str('random_textures') in parameters:
                        material = Blender_helper.set_random_pbr_img_textures(textures_path=textures_path,obj_name='Floor')
                    else:
                        pass

                    # Check for random position of the objects ----> only in one direction assume x 

                    
                    # Check for the test conditions and generate images accordingly
                    if test_case == 'normal_lighting':
                        # get the threshold values.
                        min_value,max_value = self.get_min_max_values(test_case=test_case,json_object=json_object)
                        Blender_helper.set_random_lighting(light_source_name='Sun',min_value=min_value,max_value=max_value)

                        # Uncertainty
                        light_value = bpy.data.lights[str('Sun')].energy
                        uncertainty_value = self.compute_uncertianty_lighting(light_value)
                    
                    elif test_case == 'bright_lighting':
                        # get the threshold values.
                        min_value,max_value = self.get_min_max_values(test_case=test_case,json_object=json_object)
                        Blender_helper.set_random_lighting(light_source_name='Sun',min_value=min_value,max_value=max_value)

                        # Uncertainty
                        light_value = bpy.data.lights[str('Sun')].energy
                        uncertainty_value = self.compute_uncertianty_lighting(light_value)

                    elif test_case == 'dark_lighting':
                        # get the threshold values.
                        min_value,max_value = self.get_min_max_values(test_case=test_case,json_object=json_object)
                        Blender_helper.set_random_lighting(light_source_name='Sun',min_value=min_value,max_value=max_value) 

                        # Uncertainty
                        light_value = bpy.data.lights[str('Sun')].energy
                        uncertainty_value = self.compute_uncertianty_lighting(light_value)

                    elif test_case == 'near_distance':
                        min_value,max_value = self.get_min_max_values(test_case=test_case,json_object=json_object)
                        Blender_helper.set_random_focal_length(camera_name='Camera',min_value=min_value,max_value=max_value)

                        # uncertainty
                        focal_length = bpy.data.cameras['Camera'].lens
                        uncertainty_value = self.compute_uncertianty_distance(focal_length)

                    elif test_case == 'far_distance':
                        min_value,max_value = self.get_min_max_values(test_case=test_case,json_object=json_object)
                        Blender_helper.set_random_focal_length(camera_name='Camera',min_value=min_value,max_value=max_value)

                        # uncertainty
                        focal_length = bpy.data.cameras['Camera'].lens
                        uncertainty_value = self.compute_uncertianty_distance(focal_length)

                    elif test_case == 'normal_distance':
                        min_value,max_value = self.get_min_max_values(test_case=test_case,json_object=json_object)
                        Blender_helper.set_random_focal_length(camera_name='Camera',min_value=min_value,max_value=max_value)

                        # uncertainty
                        focal_length = bpy.data.cameras['Camera'].lens
                        uncertainty_value = self.compute_uncertianty_distance(focal_length)

                    elif test_case == 'random_background_colors':
                        Blender_helper.set_random_background_color(material_name='Floor')
                        # Else condition will be taken care from setting up the scene in the top where a default floor color will be set.
                    elif test_case == 'random_background_textures':
                        material = Blender_helper.set_random_pbr_img_textures(textures_path=textures_path,obj_name='Floor')

                    elif test_case == 'blur_images': # After completing the rendering process set depth of field to false/disable.
                        Blender_helper.add_blur_dof(focus_background_name='Floor')
                        
                    elif test_case == 'distractor_objects':
                        Blender_helper.track_camera_object(object_to_track=obj_to_render)
                        distractor_name = random.choice(obj_names)
                        distractor_obj = Blender_helper.get_object(obj_name=distractor_name)
                        distractor_obj.location = (obj_to_render.location[0]+1,obj_to_render.location[1],obj_to_render.location[2])#reset distractor location again
                        distractor_obj.hide_render = False

                    elif test_case == 'deformed_objects':
                        Blender_helper.deform_objects(obj_to_deform=obj_to_render)
                    
                    elif test_case == 'all_variations':
                        if i >= (renders_per_object*0.25) and i< (renders_per_object*0.4):
                            # dark lighting
                            Blender_helper.set_random_lighting(light_source_name='Sun',min_value=0,max_value=2)
                        elif i>= (renders_per_object*0.4) and i<(renders_per_object*0.55):
                            # bright lighting
                            Blender_helper.set_random_lighting(light_source_name='Sun',min_value=15,max_value=25)
                        elif i>=(renders_per_object*0.55) and i<(renders_per_object*0.7):
                            # near distance
                            Blender_helper.set_random_focal_length(camera_name='Camera',min_value=90,max_value=140)
                        elif i>=(renders_per_object*0.7) and i<(renders_per_object*0.85):
                            # Far distance
                            Blender_helper.set_random_focal_length(camera_name='Camera',min_value=25,max_value=45)
                        elif i>=(renders_per_object*0.85):
                            # blur images
                            Blender_helper.add_blur_dof(focus_background_name='Floor')
                            Blender_helper.set_random_lighting(light_source_name='Sun',min_value=4,max_value=8)
                            Blender_helper.set_random_focal_length(camera_name='Camera',min_value=50,max_value=70)
                        else:
                            Blender_helper.set_random_lighting(light_source_name='Sun',min_value=4,max_value=8)
                            Blender_helper.set_random_focal_length(camera_name='Camera',min_value=50,max_value=70)
                        
                
                    print(f'Rendering image {i +1} of {total_render_count}')
                    seconds_per_render = (time.time() - start_time) / (i+1)
                    seconds_remaining = seconds_per_render * (total_render_count - i -1)
                    print(f'Estimated time remaining: {time.strftime("%H:%M:%S", time.gmtime(seconds_remaining))}')

                    folder_name = str(dataset_name)+str(test_case)
                    # Update file path and render
                    bpy.context.scene.render.filepath = str(output_path / folder_name / obj_name / f'{str(i).zfill(6)}.png')
                    bpy.ops.render.render(write_still = True)
                    
                    # Save the uncertainty labels as json file
                    # uncertainty_distribution = self.compute_uncertainty(obj_name=obj_name,material_threshold_dict=material_threshold_dict,light_value=10,obj_names=obj_names)
                    parameters_dict['image_path'] = bpy.context.scene.render.filepath
                    parameters_dict['obj_name'] = obj_name
                    parameters_dict['focal_length'] = focal_length
                    parameters_dict['uncertainty_label'] = uncertainty_value
                    parameters_dict['low_threshold'] = 40
                    parameters_dict['high_threshold'] = 110
                    # parameters_dict['uncertainty_distribution'] = uncertainty_distribution
                    parameters_dict['Total_num_classes'] = len(obj_names)
                    
                     
                    uncertainty_labels_file_path = str(output_path / folder_name  / obj_name/ f'{str(i).zfill(6)}.json')
         
                    self.save_as_json_file(file_path=uncertainty_labels_file_path,parameters_dict=parameters_dict)
                    
                    # Remove the material again from the scene so that it won't cause problem.
                    if material != None:
                        bpy.data.materials.remove(material)
                    else:
                        pass

                    if distractor_obj!=None:
                        # distractor_obj.location = (obj_to_render.location[0]-1,obj_to_render.location[1],obj_to_render.location[2])
                        distractor_obj.hide_render = True

                    # Set the blur value back to normal ie, turn off depth of field
                    camera.data.dof.use_dof = False
                
                # Hide the object again so that it will not appear in the next iteration.
                obj_to_render.hide_render = True
                # Update the starting index 
                start_idx += renders_per_object
