
# Prerquisites
Blender - tested with 2.79 - www.blender.org
VOTT - https://github.com/Microsoft/VoTT
pip install azure-cognitiveservices-vision-customvision
# Blender Activties
Add Stl to empty Blender

## Set Active Camera
Move Active Camera to View
Hotkey:	Ctrl-Alt-Numpad0
# Check with
Hotkey:	Numpad0


#Run Script
path "c:\Program Files\Blender Foundation\Blender\2.79\"
#Run via blender to ease the use of bpy module
blender --background -P render.py




# Process
![alt text](https://github.com/uneidel/3dModelObjectDetection/Images/architecture.PNG "Architecture")


After the Process you receive a json file with metadata including Boundingboxes and the rendered pictures

# Object Detection Yolo

Download actual build from https://github.com/Microsoft/VoTT for a Visual Tagging Tool

 ![alt text](https://github.com/uneidel/3dModelObjectDetection/Images/vott.png "VoTT")

USE Azure DataScienceVM to train the model:


# Setup GPU Machine for Darknet Training
## Install Cuda on 18.04
wget https://developer.nvidia.com/compute/cuda/9.2/Prod2/local_installers/cuda_9.2.148_396.37_linux
wget https://developer.nvidia.com/compute/cuda/9.2/Prod2/patches/1/cuda_9.2.148.1_linux 
sudo apt install -y make gcc  freeglut3 freeglut3-dev libxi-dev libxmu-dev
Sudo sh cuda_9.2.148_396.37_linux

Follow the instructions
    -   accept Eula
    -   agree to non unspported configuration
    -   agree to NVIDIA Accelerated Graphics Driver
    -   agree to OPENGL Driver
    -   disagree to nvidia-xconfig
    -   agree to CUDA 9.2 Toolkit (use default for the subsequent)
    -   agree to install the Samples


*Install patch**
Sudo sh cuda_9.2.148.1_linux

''Testing Installation**
Change to deviceQuery Folder:
cd  samples/1_Utilities/deviceQuery/
make 
Query for existing CUDA enabled Cards:
./devicequery


## Install Darknet and Compile for GPU
git clone https://github.com/pjreddie/darknet
edit Makefile 
and change GPU=0 to GPU=1 (DEGUG=0 to DEBUG=1)
make 

# test installation 
./darknet detect cfg/yolov3.cfg yolov3.weights data/dog.jpg

#Train the model
[!TODO]



# Build and Test

# Contribute


# Export to customvision
![alt text](https://github.com/uneidel/3dModelObjectDetection/Images/customvision.png "customvision")