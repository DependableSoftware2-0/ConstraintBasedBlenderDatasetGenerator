# import modules
import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

import bpy
import numpy as np

from blender_utils import Blender_helper


class Dataset_helper:

    def __init__(self) -> None:
        pass

    def get_test_cases(self, json_object):
        """
        This fuction returs the list of test cases for generating different datasets.

        Args: json_object - Json object which contains the data from requirements file.
        return : list(str)
        """

        assert type(
            json_object) == dict, "Json object should be of the form dict"

        test_cases = []
        for item in json_object['Test_cases'].items():
            if json_object['Test_cases'][item[0]]['condition'] == 'True':
                test_cases.append(item[0])
        return test_cases

    def get_parameters(self, json_object):
        """
        This function returns the list of parameters that are used to modify the datasets.

        Args: json_object - Json object which contains the data from requirements file.
        return : list(str)
        """

        assert type(
            json_object) == dict, "Json object should be of the form dict"
        parameters = []
        for item in json_object['Parameters'].items():
            if json_object['Parameters'][item[0]] == 'True':
                parameters.append(item[0])
        return parameters

    def get_min_max_values(self, test_case, json_object):
        """
        This function returns the minimum and maximum values from the json object for the particular test case

        Args:
            test_case: str
            json_object : json_object

        """
        min_value = json_object['Test_cases'][str(test_case)]['min_value']
        max_value = json_object['Test_cases'][str(test_case)]['max_value']

        return float(min_value), float(max_value)

    def get_object_render_per_split(self, json_object):

        test_cases = self.get_test_cases(json_object=json_object)
        num_images_per_class = int(json_object['Num_images_per_class'])
        obj_render_list = []
        for condition in test_cases:
            obj_render_list.append((condition, num_images_per_class))
        return obj_render_list

    def save_as_json_file(self, file_path, parameters_dict):

        with open(str(file_path), 'w', encoding='utf-8') as f:
            json.dump(parameters_dict, f, ensure_ascii=False, indent=4)

        return None

    def get_location_parameters(self, object):

        parameters = {'x': object.location.x,
                      'y': object.location.y,
                      'z': object.location.z}
        return parameters

    def get_rotation_parameters(self, object):

        parameters = {'x': object.rotation_euler.x,
                      'y': object.rotation_euler.y,
                      'z': object.rotation_euler.z}
        return parameters

    def get_sequential_step_values(self, test_case, num_elements,json_object):

        start_value,stop_value = self.get_min_max_values(test_case=test_case,json_object=json_object)

        step_value = (stop_value - start_value) / (num_elements - 1)
        numbers_list = np.arange(
            start_value, stop_value + step_value, step_value)

        return numbers_list
