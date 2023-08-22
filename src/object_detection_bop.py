import os
import bpy
import math
import numpy as np
import random 
import math
import re
from pathlib import Path
import json
from itertools import chain
import sys

sys.path.append(os.getcwd())
from blender_utils import Blender_helper
from dataset_utils import Dataset_helper
print("All modules are sucessfully imported")

class BopUtils():

    def __init__(self,mesh2class):
        self.mesh2class = mesh2class

    def get_all_coordinates(self, mesh_name):
        print("Mesh name is : ", mesh_name)
        b_box = self.find_bounding_box(bpy.data.objects[mesh_name])

        if b_box:
            return self.format_coordinates(b_box, mesh_name)

        return ''

    def format_coordinates(self, coordinates, mesh_name):
        if coordinates: 
            ## Change coordinates reference frame
            x1 = (coordinates[0][0])
            x2 = (coordinates[1][0])
            y1 = (1 - coordinates[1][1])
            y2 = (1 - coordinates[0][1])

            ## Get final bounding box information
            width = (x2-x1)  # Calculate the absolute width of the bounding box
            height = (y2-y1) # Calculate the absolute height of the bounding box
            # Calculate the absolute center of the bounding box
            cx = x1 + (width/2) 
            cy = y1 + (height/2)

            ## Formulate line corresponding to the bounding box of one class top left width and height
            # txt_coordinates = str(_class) + ' ' + str(x1) + ' ' + str(y2) + ' ' + str(width) + ' ' + str(height) + '\n'
            txt_coordinates = {
                "bbox_obj":[x1,x2,width,height],
                "bbox_visib": [x1,x2,width,height],
                "class_label": self.mesh2class[mesh_name],
                "class_name": mesh_name
            }
            return txt_coordinates
        # If the current class isn't in view of the camera, then pass
        else:
            pass

    def find_bounding_box(self, obj):
        camera_object = bpy.data.objects['Camera']
        matrix = camera_object.matrix_world.normalized().inverted()
        """ Create a new mesh data block, using the inverse transform matrix to undo any transformations. """
        
        print("Name of the object is : ", obj)
        mesh = obj.to_mesh(preserve_all_data_layers=True)
        mesh.transform(obj.matrix_world)
        mesh.transform(matrix)
        """ Get the world coordinates for the camera frame bounding box, before any transformations. """
        frame = [-v for v in camera_object.data.view_frame(scene=bpy.context.scene)[:3]]

        lx = []
        ly = []

        for v in mesh.vertices:
            co_local = v.co
            z = -co_local.z

            if z <= 0.0:
                """ Vertex is behind the camera; ignore it. """
                continue
            else:
                """ Perspective division """
                frame = [(v / (v.z / z)) for v in frame]

            min_x, max_x = frame[1].x, frame[2].x
            min_y, max_y = frame[0].y, frame[1].y

            x = (co_local.x - min_x) / (max_x - min_x)
            y = (co_local.y - min_y) / (max_y - min_y)

            lx.append(x)
            ly.append(y)

        """ Image is not in view if all the mesh verts were ignored """
        if not lx or not ly:
            return None

        min_x = np.clip(min(lx), 0.0, 1.0)
        min_y = np.clip(min(ly), 0.0, 1.0)
        max_x = np.clip(max(lx), 0.0, 1.0)
        max_y = np.clip(max(ly), 0.0, 1.0)

        """ Image is not in view if both bounding points exist on the same side """
        if min_x == max_x or min_y == max_y:
            return None

        """ Figure out the rendered image size """
        render = bpy.context.scene.render
        fac = render.resolution_percentage * 0.01
        dim_x = render.resolution_x * fac
        dim_y = render.resolution_y * fac
        
        ## Verify there's no coordinates equal to zero
        coord_list = [min_x, min_y, max_x, max_y]
        if min(coord_list) == 0.0:
            indexmin = coord_list.index(min(coord_list))
            coord_list[indexmin] = coord_list[indexmin] + 0.0000001

        return (min_x, min_y), (max_x, max_y)
    
    def get_scene_gt_info_parameters(self,object_names):

        annotations = []
        for obj_name in object_names:
            obj_annotations = self.get_all_coordinates(mesh_name=obj_name)
            annotations.append(obj_annotations)

        return annotations
       
    def save_as_json_file(self,annotations_dict,file_path):
        with open(file_path,'w') as file:
            json.dump(annotations_dict, file)

    def get_k_matrix(self):
        # https://mcarletti.github.io/articles/blenderintrinsicparams/
        camera = bpy.data.objects['Camera']
        scene = bpy.context.scene
        
        scale = scene.render.resolution_percentage / 100
        width = scene.render.resolution_x * scale # px
        height = scene.render.resolution_y * scale # px
        
        camdata = camera.data



        focal = camdata.lens # mm
        sensor_width = camdata.sensor_width # mm
        sensor_height = camdata.sensor_height # mm
        pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y

        if (camdata.sensor_fit == 'VERTICAL'):
            # the sensor height is fixed (sensor fit is horizontal), 
            # the sensor width is effectively changed with the pixel aspect ratio
            s_u = width / sensor_width / pixel_aspect_ratio 
            s_v = height / sensor_height
        else: # 'HORIZONTAL' and 'AUTO'
            # the sensor width is fixed (sensor fit is horizontal), 
            # the sensor height is effectively changed with the pixel aspect ratio
            pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
            s_u = width / sensor_width
            s_v = height * pixel_aspect_ratio / sensor_height

        # parameters of intrinsic calibration matrix K
        alpha_u = focal * s_u
        alpha_v = focal * s_v
        u_0 = width / 2
        v_0 = height / 2
        skew = 0 # only use rectangular pixels

        K = np.array([
            [alpha_u,    skew, u_0],
            [      0, alpha_v, v_0],
            [      0,       0,   1]
        ], dtype=np.float32)
        # s = intrinsics.skew

        cam_K = K.flatten().tolist()
        return cam_K

    def get_scene_camera_parameters(self):
        
        camera_object = bpy.data.objects['Camera']

        # transformation of camera with respect to world.
        T_C_W = camera_object.matrix_world

        # transformation of world with respect to camera.
        T_W_C = np.linalg.inv(T_C_W)

        cam_R_w2c = T_W_C[:3, :3].flatten().tolist()
        cam_t_w2c = T_W_C[:3,3].flatten().tolist()

        scene_parameters = {"cam_K": self.get_k_matrix(), 
                            "cam_R_w2c": cam_R_w2c, 
                            "cam_t_w2c": cam_t_w2c,  
                            "depth_scale": 1}

        return scene_parameters
    
    def calculate_scene_gt_parameters(self,obj_name):
        
        obj = bpy.data.objects[obj_name]
        cam = bpy.data.objects['Camera']

        T_m2w = np.array(obj.matrix_world)
        T_c2w = np.array(cam.matrix_world)

        T_m2c = T_m2w @ np.linalg.inv(T_c2w)
        
        cam_R_m2c = T_m2c[:3, :3].flatten().tolist()
        cam_t_m2c = T_m2c[:3, 3].flatten().tolist()

        gt_parameters = {
            "cam_R_m2c":cam_R_m2c,
            "cam_t_m2c":cam_t_m2c,
            "obj_id": self.mesh2class[obj_name],
            "obj_name": obj_name
        }
        return gt_parameters
    
    def get_scene_gt_parameters(self, object_names):
        final_parameters = []
        for obj_name in object_names:
            param = self.calculate_scene_gt_parameters(obj_name=obj_name)
            final_parameters.append(param)

        return final_parameters
    


if __name__ == '__main__':
    
    print("Things to be done! 2000 images has to be rendered.\n1. Create the scene and the basic code. \n2. RGB images (1280 x 720)\n3. Depth Images (1280 x 720)\n4. scene_camera.json file\n5. scene_gt.json file\n6. scene_gt_info.")
    
    # Paths for the directories
#    PARENT_DIR = os.path.normpath(os.getcwd() + os.sep + os.pardir)
    PARENT_DIR = os.path.normpath(os.getcwd()+os.sep+os.pardir)
    TEXTURES_DIR = os.path.join(PARENT_DIR,'blender_files/textures/')
    MODELS_DIR = os.path.join(PARENT_DIR,'blender_files/models/')
    SAVE_DIR = os.path.join(os.getcwd(),'results/')
    
    RGB_DIR = SAVE_DIR+'rgb/'
    DEPTH_DIR = SAVE_DIR+'depth/'
    JSON_DIR = SAVE_DIR
    
    NUM_OF_SAMPLES = 5
    
    # Create instance for the blender helper class
    blender_helper = Blender_helper()
    dataset_helper = Dataset_helper()

    object_names = blender_helper.get_object_names(background_plane_name='Background_plane',camera_track='camera_track',light_track='light_track')
    print("Objects present in the scene are : ", object_names )
    
    # Set render parameters.
    blender_helper.set_render_parameters(device='GPU',
                                        render_engine='CYCLES',
                                        res_x=1280,
                                        res_y=720,
                                        num_samples=100)
    # Dictionary for class names to index
    class_to_idx = {value:key for key,value in enumerate(object_names)}
    print("Class to index values : ", class_to_idx)
    
    # Create instance for the bounding box helper class
    bounding_box_helper = BopUtils(mesh2class=class_to_idx)
    
    step_value = (100-0)/NUM_OF_SAMPLES
    rendering_values = np.arange(0,100,step_value)
    
    # Setup compositor
    bpy.context.scene.view_layers["ViewLayer"].use_pass_mist = True
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree


    if not tree.nodes['Render Layers']:
        render_layers_node = tree.nodes.new(type='CompositorNodeRLayers')
    else:
        render_layers_node = tree.nodes['Render Layers']

    if not tree.nodes['Composite']:
        output_node = tree.nodes.new(type='Composite')
    else:
        output_node = tree.nodes['Composite']

    links = tree.links
    # links.new(render_layers.outputs["Image"], compos.inputs['Image'])
    # links.new(render_layers.outputs["Depth"], compos.inputs['Image'])
    # 
    # Create dictionaries to store the labels
    scene_camera_params = {}
    scene_gt_params = {}
    scene_gt_info_params = {}     

    for idx,value in enumerate(rendering_values):

        print(f"Rendering Image : {idx} / {len(rendering_values)}")

        blender_helper.set_camera_postion_on_path(camera_name='Camera',distance_value=value)
        
        # Update file path for rgb images and render
        bpy.context.scene.render.filepath = os.path.join(RGB_DIR, str(f"{str(idx).zfill(6)}.png"))
        print("File name of rgb image is  : ", bpy.context.scene.render.filepath)
        links.new(render_layers_node.outputs["Image"], output_node.inputs['Image'])
        bpy.ops.render.render(write_still = True)

        # Store the json labels
        scene_camera_params[str(idx)] = bounding_box_helper.get_scene_camera_parameters()
        scene_gt_params[str(idx)] = bounding_box_helper.get_scene_gt_parameters(object_names=object_names)
        scene_gt_info_params[str(idx)] = bounding_box_helper.get_scene_gt_info_parameters(object_names=object_names)

        # Create depth images
        bpy.context.scene.render.filepath = os.path.join(DEPTH_DIR, str(f"{str(idx).zfill(6)}.png"))
        print("File name of depth image is  : ", bpy.context.scene.render.filepath)
        

        links.new(render_layers_node.outputs["Depth"], output_node.inputs['Image'])

        bpy.ops.render.render(write_still = True)

    scene_cam_path = JSON_DIR + 'scene_camera.json'
    scene_gt_path = JSON_DIR + 'scene_gt.json'
    scene_gt_info_path = JSON_DIR + 'scene_gt_info.json'

    bounding_box_helper.save_as_json_file(annotations_dict=scene_camera_params,file_path=scene_cam_path)
    bounding_box_helper.save_as_json_file(annotations_dict=scene_gt_params,file_path=scene_gt_path)
    bounding_box_helper.save_as_json_file(annotations_dict=scene_gt_info_params,file_path=scene_gt_info_path)

    print("Completed Rendering process")
