import os
import bpy
import random
import math
from mathutils import Euler, Color,Vector
import re


class Blender_helper():

    def __init__(self) -> None:
        pass

    def add_basic_scene(self):
        """
        This function adds  basic setup like, camera, light and floor for the objects

        use the functions below
        """
        # add light source and set it to desired place
        self.add_light_source(type='sun',obj_name='Sun',shadow=True)
        # add camera and set it to desired place
        self.add_camera(camera_name='Camera')

    def import_objects(self):
        """
        This function adds objects from cad format along with their materials.
        when you import the objects you should change the origin point for the objects to center of the object.
        """

    def add_background_scene(self):
        """
        This function adds the background plane to the scene along with a default material.
        """
    
    def add_camera(self,camera_name:str):
        """
        Adds a camera to the origin of the scene 

        Keyword arguments:
        camera_name -- Name for the camera: str 
        """
        bpy.ops.object.camera_add(location=(0.0,0.0,0.0),rotation=(0.0,0.0,0.0))
        bpy.context.object.data.lens = 50
        bpy.context.object.data.name = str(camera_name)

    def set_camera(self):
        """
        This function sets the camera to the desired location and orientation.
        """

    def add_light_source(self,type:str,obj_name:str,shadow:bool):
        """
        Adds a light source with respective type to the origin of the scene.

        Keyword arguments:
        type -- The type of light source, default SUN, other: POINT,AREA,SPOT
        obj_name -- Name for the object: str
        shadow -- Enable or Disable shadows: bool
        """
        bpy.ops.object.light_add(type=str(type).upper(),radius=1,location=(0,0,0))
        bpy.context.object.data.name = str(obj_name)
        bpy.context.object.data.energy = 5
        bpy.context.object.data.use_shadow = shadow
        bpy.context.object.data.use_contact_shadow = shadow


    def set_light_source(self,obj_name:str,position:tuple,rotation:tuple):
        """
        Sets the light source to the desired loacation,orientation and energy values.
        
        Keyword arguments:
        obj_name -- Name of the light object: str
        position -- Position values of the light object: (float,float,float)
        rotation -- Rotation values of the light object: (float,float,float)
        """
        bpy.data.lights[str(obj_name)].location = position
        bpy.data.lights[str(obj_name)].Rotation = rotation

    def get_object_names(self,background_plane_name):
        """
        This function returns list of object names present in the scene after removing unnecessary things.

        Keyword arguments:
        background_plane_name--name of the background plane object: str
        """

        obj_names = bpy.context.scene.objects.keys()
        for name in bpy.data.cameras.keys():
            obj_names.remove(name)
        for name in bpy.data.lights.keys():
            obj_names.remove(name)

        obj_names.remove(str(background_plane_name))
        return sorted(obj_names)
    
    def hide_objects(self,obj_names):
        """
        This function hides the objects present in the scene during rendering.
        """
        for name in obj_names:
            bpy.context.scene.objects[name].hide_render = True

    def get_object(self,obj_name):
        """
        Returns the object present in the scene.
        """
        return bpy.context.scene.objects[obj_name]

    def set_random_rotation(self,obj_to_change):
        """
        Applies a random rotation to the given object.

        Keyword arguments:
        obj_to_change: blender object
        """
        random_rotat_values = [random.random()*2*math.pi,random.random()*2*math.pi,random.random()*2*math.pi]
        obj_to_change.rotation_euler = Euler(random_rotat_values,'XYZ')

    def set_random_lighting(self,light_source_name,min_value,max_value):
        """
        Applies random light intensities to the scene.

        Keyword arguments:
        light_source_name:str
        min_value: float
        max_value: float
        """
        # bpy.data.lights[str(light_source_name)].energy = round(random.uniform(min_value,max_value),2)
        bpy.data.lights[str(light_source_name)].energy = random.uniform(min_value,max_value)

    def set_random_focal_length(self,camera_name,min_value,max_value):
        value = random.randint(min_value,max_value)
        bpy.data.cameras[str(camera_name)].lens =  float(value)

    def set_random_background_color(self,obj_name):
        """Applies Materials randomly to the object, Changes specially the Principled BSDf Base color values for the given object's material.
    
        Keyword arguments:
        obj_name: str
        """
        print("\nmaterials list : ",bpy.data.materials)
        material_to_change = bpy.data.objects[str(obj_name)].active_material
        # bpy.data.materials[material_name]
        color = Color()
        hue = random.random()  # Random hue between 0 and 1
        color.hsv = (hue,0.85,0.85)
        rgba = [color.r, color.g, color.b, 1]
        material_to_change.node_tree.nodes['Principled BSDF'].inputs[0].default_value = rgba

    
    def set_render_parameters(self,device,res_x,res_y,num_samples):
        """Sets the active scene with the specified render parameters.

        Keyword arguments:
        device-- Type of the device CPU or GPU : str
        res_x-- resolution width of the image to render: int
        res_y-- resolution height of the image to render: int
        num_samples-- number of render samples 
        """
        scene = bpy.context.scene
        scene.render.engine = "CYCLES"
        scene.cycles.device = str(device).upper()
        scene.render.resolution_x = int(res_x)
        scene.render.resolution_y = int(res_y)
        scene.render.resolution_percentage = 100
        scene.cycles.samples = num_samples
        scene.render.image_settings.file_format = "PNG"
    
    def get_texture_map_paths(self,texture_folder):
        """Returns paths for the images which can be used for image textures.

        Keyword arguments:
        texture_folder-- Path for the folder containing the images.
        """
        texture_dict = {
                        "normal_map": None,
                        "base_color":None,
                        "disp_map":None,
                        "metal_map":None,
                        "roughness_map":None
                        }
        
        files = os.listdir(path=texture_folder)
        for file in files:
            # Match the files and seperate
            nrm_match = re.search(r'\wnormal', file) or re.search(r'\wNRM', file) or re.search(r'\wnor', file)
            base_match = re.search(r'\wbasecolor', file) or re.search(r'\wCOL_VAR1', file) or re.search(r'\wdiff', file) or re.search(r'\wcol', file)
            disp_match = re.search(r'\wDISP_4K',file) or re.search(r'\wheight',file) or re.search(r'\wdisplacement',file) or re.search(r'\wdisp',file)
            metal_match = re.search(r'\wmetallic',file) or re.search(r'\wREFL',file) or re.search(r'\wmetal',file)
            rough_match = re.search(r'\wroughness',file) or re.search(r'\wGLOSS',file) or re.search(r'\wrough',file)

            if nrm_match:
                normal_map = os.path.join(texture_folder,file)
                texture_dict['normal_map'] = normal_map

            if base_match:
                base_color = os.path.join(texture_folder,file)
                texture_dict['base_color'] = base_color
            if disp_match:
                disp_map = os.path.join(texture_folder,file)
                texture_dict['disp_map'] = disp_map
            if metal_match:
                metal_map = os.path.join(texture_folder,file)
                texture_dict['metal_map'] = metal_map
            if rough_match:
                roughness_map = os.path.join(texture_folder,file)
                texture_dict['roughness_map'] = roughness_map
        return texture_dict
      
    def get_texture_paths(self,texture_dir):
        """Gets the paths for all the texture_folders from the main textures folder and returns them as a list
        
        Keyword arguments:
        texture_dir-- path for the directory containig the textures.
        """
        bnames = os.listdir(texture_dir)
        for i, cs in enumerate(zip(*bnames)):
            if len(set(cs)) != 1:
                break
        for _i, cs in enumerate(zip(*[b[::-1] for b in bnames])):
            if len(set(cs)) != 1:
                break
        texture_paths = [os.path.join(texture_dir, bname+'/') for bname in bnames]
        return texture_paths

    
    def set_random_pbr_img_textures(self,textures_path,obj_name):
        """Applies image textures randomly from the available images to the specified object.
        
        Keyword arguments:
        texture_paths-- list of paths for the texture folders.
        obj_name-- name of the object to change the materail/texture
        """

        texture_paths = self.get_texture_paths(textures_path)

        texture_path = random.choice(texture_paths)

        material_name = str(texture_path.split('/')[-2])
        # print("Material name : ", material_name)
        texture_dict = self.get_texture_map_paths(texture_folder=texture_path)


        # create a new material with the name.
        material = bpy.data.materials.new(name=material_name) # Change name everytime
        material.use_nodes =True
        

        # Create the nodes for the material
        
        # Nodes for controlling the texture
        texture_coordinate = material.node_tree.nodes.new(type="ShaderNodeTexCoord")
        mapping_node = material.node_tree.nodes.new(type="ShaderNodeMapping")

        # Create vector nodes
        normal_map = material.node_tree.nodes.new(type="ShaderNodeNormalMap")
        displacement_map = material.node_tree.nodes.new(type="ShaderNodeDisplacement")
        bump_map = material.node_tree.nodes.new(type="ShaderNodeBump")
        invert_node = material.node_tree.nodes.new(type="ShaderNodeInvert")
        

        # Nodes for principled bsdf and output
        principled_bsdf =  material.node_tree.nodes['Principled BSDF']
        material_output = material.node_tree.nodes['Material Output']

        # Connect the nodes 
        material.node_tree.links.new(texture_coordinate.outputs['UV'],mapping_node.inputs['Vector'])
        # Nodes for image textures
        # Base color
        if texture_dict['base_color'] != None: 
            base_color_img = material.node_tree.nodes.new(type="ShaderNodeTexImage")
            base_color_img.image = bpy.data.images.load(texture_dict['base_color'])
            material.node_tree.links.new(mapping_node.outputs['Vector'],base_color_img.inputs['Vector'])
            material.node_tree.links.new(base_color_img.outputs['Color'],principled_bsdf.inputs['Base Color'])
            # print("created base color")
        # Normal map
        if texture_dict['normal_map'] != None: 
            normal_img = material.node_tree.nodes.new(type="ShaderNodeTexImage" )
            normal_img.image = bpy.data.images.load(texture_dict['normal_map'])
            material.node_tree.links.new(mapping_node.outputs['Vector'],normal_img.inputs['Vector'])
            material.node_tree.links.new(normal_img.outputs['Color'],normal_map.inputs['Color'])
            material.node_tree.links.new(normal_map.outputs['Normal'],principled_bsdf.inputs['Normal'])
            # print("created Normal map")
        # Displacement map
        if texture_dict['disp_map'] != None:
            displacement_img = material.node_tree.nodes.new(type="ShaderNodeTexImage" )
            displacement_img.image = bpy.data.images.load(texture_dict['disp_map'])
            material.node_tree.links.new(mapping_node.outputs['Vector'],displacement_img.inputs['Vector'])
            material.node_tree.links.new(displacement_img.outputs['Color'],displacement_map.inputs['Height'])
            material.node_tree.links.new(displacement_map.outputs['Displacement'],material_output.inputs['Displacement'])
            # print("created Displacement map")
        # Roughness map
        if texture_dict['roughness_map'] !=None:
            roughness_img = material.node_tree.nodes.new(type="ShaderNodeTexImage" )
            roughness_img.image = bpy.data.images.load(texture_dict['roughness_map'])
            material.node_tree.links.new(mapping_node.outputs['Vector'],roughness_img.inputs['Vector'])
            material.node_tree.links.new(roughness_img.outputs['Color'],invert_node.inputs['Color'])
            material.node_tree.links.new(invert_node.outputs['Color'],principled_bsdf.inputs['Roughness'])
            # print("created Roughness map")
        # Metal map
        if texture_dict['metal_map'] !=None:
            metallic_img = material.node_tree.nodes.new(type="ShaderNodeTexImage" )
            metallic_img.image = bpy.data.images.load(texture_dict['metal_map'])
            material.node_tree.links.new(mapping_node.outputs['Vector'],metallic_img.inputs['Vector'])
            material.node_tree.links.new(metallic_img.outputs['Color'],principled_bsdf.inputs['Metallic'])
            # print("created Metal map map")
        # Set material final output
        material.node_tree.links.new(principled_bsdf.outputs['BSDF'],material_output.inputs['Surface'])
        # print("created output relation to material output")
        # Set the material to the object

        obj = bpy.data.objects[obj_name]

        if obj.data.materials:
            obj.data.materials.append(material)
            obj.active_material = bpy.data.materials[material_name]
        else:
            obj.data.materials.append(material)
            obj.active_material = material

        print("List of materials : ", bpy.data.materials.keys())

        return material

    def add_blur_dof(self,focus_background_name):
        """Adds blur effect to the images using depth of field parameter of the camera.
        
        Keyword arguments:
        focus_background_name: name of the backgrond plane
        """

        camera = bpy.data.objects['Camera']
        camera.data.dof.use_dof = True
        # camera.data.dof.focus_object = bpy.data.objects[str(focus_background_name)]
        # camera.data.dof.aperture_fstop= random.uniform(0,0.2)
        camera.data.dof.focus_distance = random.uniform(0,0.8)
        
    def deform_objects(self,obj_to_deform):
        """ Deforms the object using simple deform modifer properties
    
        Keyword arguments:
            obj_to_deform: blender object to deform
        """
    
        if not 'simple_deform' in obj_to_deform.modifiers.keys():
            obj_to_deform.modifiers.new(name="simple_deform",type = 'SIMPLE_DEFORM')
            deform_modifier = obj_to_deform.modifiers['simple_deform']
        else:
            deform_modifier = obj_to_deform.modifiers['simple_deform']
        deform_modifier.deform_method = 'BEND'
    
        deform_modifier.deform_axis = 'Z'
        deform_modifier.angle = random.uniform(-0.523,-3.14)

    
    def get_ycb_objects_names(self,models_dir):
        """gets the names of the objects present the folders
            .obj objects and modifies the names and returns the 
            required names.
        """
        object_names = []
        # Iterate through all subdirectories in the base path
        for root, dirs, files in os.walk(models_dir):
            # Iterate through all files in the current directory
            for file in files:
                # Check if the file is an OBJ file
                if file.endswith(".obj"):
                    # Construct the full path to the OBJ file
                    object_file = os.path.join(root, file)
                    obj_name = "ycb_"+"_".join(object_file.split('/')[-3].split('_')[1::])
                    object_names.append(obj_name)
        return object_names
    
    def import_ycb_objects(self,models_dir):
        """Imports all the ycb objects/ .obj file in the root directory
        """
        object_names = []
        # Iterate through all subdirectories in the base path
        for root, dirs, files in os.walk(models_dir):
            # Iterate through all files in the current directory
            for file in files:
                # Check if the file is an OBJ file
                if file.endswith(".obj"):
                    # Construct the full path to the OBJ file
                    object_file = os.path.join(root, file)
                    obj_name = "ycb_"+"_".join(object_file.split('/')[-3].split('_')[1::])
                    
                    # Import the OBJ file
                    bpy.ops.import_scene.obj(filepath=object_file)
                    
                    # Set the active object to the imported object
                    object = bpy.context.selected_objects[0]

                    # Check if the object is valid
                    if object is not None:
                        # Change the name of the object
                        object.name = obj_name
                        object_names.append(obj_name)
                    else:
                        print("Error: Object is None")
        print(object_names)        
        return object_names
    
    def distractor_objects(self):
        pass

    def track_camera_object(self,object_to_track):
        camera = bpy.data.objects['Camera']
        if not str('Track To') in camera.constraints.keys() :
            camera.constraints.new(type="TRACK_TO")
            camera.constraints['Track To'].target = object_to_track
