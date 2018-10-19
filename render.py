import bpy
import math
import json
import os,sys
from mathutils import Vector
import random
import numpy as np
# py -m pip install bpy

def camera_view_bounds_2d(scene, camera_object, mesh_object):
    matrix = camera_object.matrix_world.normalized().inverted()
    mesh = mesh_object.to_mesh(scene, True, 'PREVIEW')
    mesh.transform(mesh_object.matrix_world)
    mesh.transform(matrix)

    frame = [-v for v in camera_object.data.view_frame(scene=scene)[:3]]
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

    bpy.data.meshes.remove(mesh)

    if not lx or not ly:
        return None

    min_x = clamp(min(lx), 0.0, 1.0)
    max_x = clamp(max(lx), 0.0, 1.0)
    min_y = clamp(min(ly), 0.0, 1.0)
    max_y = clamp(max(ly), 0.0, 1.0)

    if min_x == max_x or min_y == max_y:
        return None

    render = scene.render
    fac = render.resolution_percentage * 0.01
    dim_x = render.resolution_x * fac
    dim_y = render.resolution_y * fac

    return (min_x, min_y), (max_x, max_y)
    #return Box(min_x, min_y, max_x, max_y, dim_x, dim_y)

def clamp(x, minimum, maximum):
    return max(minimum, min(x, maximum))




def StoreJson(filepath, data): 
    with open(filepath, 'w') as outfile:
        json.dump(data, outfile)

def simulate(scene, mesh_objects, spawn_range, p_visible):
    scene.frame_set(0)
    for object in mesh_objects:
        if random.uniform(0, 1) <= p_visible:
            object.hide = False
            object.hide_render = False
        else:
            object.hide = True
            object.hide_render = True

        object.location.x = random.randrange(spawn_range[0][0], spawn_range[0][1])
        object.location.y = random.randrange(spawn_range[1][0], spawn_range[1][1])
        object.location.z = random.randrange(spawn_range[2][0], spawn_range[2][1])

    for i in range(1, 100):
        scene.frame_set(i)


def add_background(filepath):
    img = bpy.data.images.load(filepath)
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            space_data = area.spaces.active
            bg = space_data.background_images.new()
            bg.image = img
            space_data.show_background_images = True
            break

    texture = bpy.data.textures.new("Texture.001", 'IMAGE')
    texture.image = img
    bpy.data.worlds['World'].active_texture = texture
    bpy.context.scene.world.texture_slots[0].use_map_horizon = True


def resetCameraView(camera):
    cmat = camera.matrix_world
    camera_z = Vector([cmat[i][2] for i in range(3)])
    print("Reset Camera View")
    # this is the new center of the camera view
    l_0 = Vector((0,0,0))
    l = camera_z
    n = camera_z
    p_0 = camera.location

    new_loc = (p_0 - l_0).dot(n)/l.dot(n) * l + l_0

    camera.location = new_loc


def GetDistanceCamMesh(cam, ob):
    if cam and ob and ob.type == 'MESH':
        camloc = cam.matrix_world.translation
        mw = ob.matrix_world
        me = ob.data # mesh
        camdists = [(mw * v.co - camloc).length for v in me.vertices]
        print(camdists)


def CreateFrameInfo(box,scene,idcounter,tagName):

    x1= (box[0][0]*scene.render.resolution_x)
    y1= (box[0][1]*scene.render.resolution_y)
    x2= (box[1][0]*scene.render.resolution_x)
    y2= (box[1][1]*scene.render.resolution_y)

    frame = {
            'x1':x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'id': idcounter, 
            'width': scene.render.resolution_x,
            'height': scene.render.resolution_y,
            'type': "Rectangle",
            'name': 1
    }
    print (frame)
    
    tags = []
    
    tags.append(tagName)
    frame["tags"] = tags
       
    return frame


def CreateCVFrameInfo(box, idcounter, basePath):
    fileName = "img%d.png" % (idcounter);
    fullfileName = os.path.join(basePath,"img",fileName)
    print(fullfileName)
    bpy.context.scene.render.filepath = fullfileName

    cvFrame = {
        'Name' : fileName,
        'x' : box[0][0],
        'y' : box[0][1],
        'width': (box[1][0]-box[0][0]),
        'height': (box[1][1] -box[0][1])
    }
    return cvFrame


def SupressLogInfo():
    # redirect output to log file
        logfile = 'blender_render.log'
        open(logfile, 'a').close()
        old = os.dup(1)
        sys.stdout.flush()
        os.close(1)
        os.open(logfile, os.O_WRONLY)

      

        # disable output redirection
        os.close(1)
        os.dup(old)
        os.close(old)

def Simulate(scene,cam_ob, mesh,tagName,basePath, bgimageFolder):
    total = 20
    resolutionx=416
    resolutiony=416
    rotate_by = 4.21875   
    start_angle = 45     

    if mesh is None: 
        print (" Cannot find the mesh... exiting.")
        quit()
    if cam_ob is None:
        print("cannot find a Camera - Please check")
        quit()

    framecoll = {}
    cvframes = []
    visitedFrames = []
    idcounter=0
    mesh.rotation_mode = 'XYZ'
    scene.render.resolution_x = resolutionx
    scene.render.resolution_y = resolutiony
    scene.render.resolution_percentage = 100


    syntheticJson = {}
    syntheticJson["framerate"] = 1
    syntheticJson["inputTags"] = tagName
    syntheticJson["suggestiontype"] = "track"
    syntheticJson["scd"] = False

   
    resetCameraView(cam_ob)


    
    GetDistanceCamMesh(cam_ob, mesh)
    
    for file in os.listdir(bgimageFolder):
        add_background(os.path.join(bgimageFolder,file))
        for x in range(1,total):
    
            frame = {}
            cvFrame={}
            angle = (start_angle * (math.pi/180)) + (x*-1) * (rotate_by * (math.pi/180))
            mesh.rotation_euler = ( 0, 0, angle )
        
            
            # Set image of empty        
            box = camera_view_bounds_2d(scene, cam_ob, mesh)
            if box is None:
                print("Bounding Box is empty... exiting")
                quit()
            

        
            visitedFrames.append(x-1)
            
            frame = CreateFrameInfo(box, scene, idcounter, tagName)
            cvFrame = CreateCVFrameInfo(box, idcounter, basePath)
        

            SupressLogInfo()
            # do the rendering
            bpy.ops.render.render(write_still=True)
            print ("Successfully created Render: %i" % (idcounter))
            idcounter=idcounter+1
            f = []
            f.append(frame)
            cvframes.append(cvFrame)
            framecoll[x-1]= f # check why is wrapped again

    syntheticJson["frames"] = framecoll
    syntheticJson["visitedFrames"] = visitedFrames

    StoreJson("C:\\temp\\images.json", syntheticJson)
    StoreJson("c:\\temp\\cvjson.json", cvframes)
    
    print("Json stored.")


def CreateRenderFromScene(location, meshName):
    bpy.ops.wm.open_mainfile(filepath=location)
    meshName = meshName
    scene = bpy.context.scene
    mesh = bpy.data.objects[meshName]
    cam_ob = bpy.data.objects["Camera"]     
    cam_loc = cam_ob.location
    cam_rot = cam_ob.rotation_euler
    #print (cam_rot)
    bgImageFolder = "c:\\temp\\bg\\"
    Simulate(scene, cam_ob, mesh,meshName,"c:\\temp\\", bgImageFolder)


def CreateFromScratch(pathToStl,targetPath):
    print ("Create from Scratch.")
    path, file = os.path.split(pathToStl)
    DeleteAllObjects()
    bpy.ops.import_mesh.stl(filepath=pathToStl, filter_glob="*.stl",  files=[{"name":file}], directory=path)
    bpy.ops.object.camera_add(view_align=False, location=[14,0,0], rotation=(1.5708, 0, 1.5708))
    bpy.ops.wm.save_as_mainfile(filepath=targetPath)

def DeleteAllObjects():
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.object.select_by_type(type='CAMERA')
    bpy.ops.object.delete(use_global=False)
    for item in bpy.data.meshes:
        bpy.data.meshes.remove(item)

####################  MAIN ###############################################

 


  

if __name__ == '__main__':
    pathToStl="C:\\Users\\uneidel\\Documents\\GitHub\\Generation4\\helmet.stl"
    #CreateFromScratch(pathToStl,"c:\\temp\\render.blend")
    CreateRenderFromScene("C:\\Users\\uneidel\\Documents\\GitHub\\Generation4\\Helmet.blend", "Helmet")
   
    