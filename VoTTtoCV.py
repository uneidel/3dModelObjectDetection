import json
import os
from azure.cognitiveservices.vision.customvision.training import training_api
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntry, Region
import time








if __name__ == '__main__':
    # Replace with a valid key
    training_key = "<useyourown>"
    
    prjName="helmets"
    tagName =  "helmet"

    basePath="c:\\temp\\"
    tagged_images_with_regions = []
    trainer = training_api.TrainingApi(training_key)
    obj_detection_domain = next(domain for domain in trainer.get_domains() if domain.type == "ObjectDetection")
    print ("Creating project...")

    
    projects= trainer.get_projects()
   # print(projects)
    prjId =""
    tag=""
    for i in [x for x in projects if x.name == prjName]:
        prjId = i.id
        print("Projects %s exists" % (i.id))

    if not prjId:       
        project = trainer.create_project(prjName, domain_id=obj_detection_domain.id)
        tag = trainer.create_tag(project.id, tagName) #TODO check if tag the same
    else:
        project = trainer.get_project(prjId)
        
        for i in [x for x in trainer.get_tags(project.id) if x.name == tagName]:
            tag = i

        
         
    

    
    
   

    fullpath = os.path.join(basePath, "cvjson.json")
    print ("Loading Json: %s " % (fullpath))
   
    with open(fullpath) as f:
        imgList = json.load(f)

    print("Adding Images")
    for data in imgList:
        filePath = os.path.join(basePath,"img",data.get("Name"))
        
        print("Processing %s" % (data.get("Name")))
       
        regions = [Region(tag_id=tag.id, left=data.get("x"),top=data.get("y"),width=data.get("width"),height=data.get("height"))]
        #regions = [ Region(tag_id=fork_tag.id, left=x,top=y,width=w,height=h) ]

        with open(filePath, mode="rb") as image_contents:
            #There is a limit of 64 images and 20 tags.

            tagged_images_with_regions.append(ImageFileCreateEntry(name=data.get("Name"), contents=image_contents.read(), regions=regions))

    
    trainer.create_images_from_files(project.id, images=tagged_images_with_regions,raw=True)
    iteration = trainer.train_project(project.id)
    while (iteration.status != "Completed"):
        iteration = trainer.get_iteration(project.id, iteration.id)
        print ("Training status: " + iteration.status)
        time.sleep(1)

# The iteration is now trained. Make it the default project endpoint
trainer.update_iteration(project.id, iteration.id, is_default=True)
print ("Done!")
