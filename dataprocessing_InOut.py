import os
from pypylon import pylondataprocessing
from pypylon import pylon
from pypylon import genicam
import sys

class MyUpdateObserver(pylondataprocessing.UpdateObserver):
    def __init__(self):
        pylondataprocessing.UpdateObserver.__init__(self)

    def UpdateDone(self, recipe, update, userProvidedId):
        print("UpdateDone")

def main():
    try:
        pylonImg = pylon.PylonImage()
        camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)        
        
        resultCollector = pylondataprocessing.GenericOutputObserver()   
        updateObserver = MyUpdateObserver()
        
        recipe = pylondataprocessing.Recipe()

        thisdir = os.path.dirname(__file__)
        recipefilename = os.path.join(thisdir, 'InOut.precipe')
        recipe.Load(recipefilename)


        recipe.RegisterAllOutputsObserver(resultCollector, pylon.RegistrationMode_Append);
        recipe.PreAllocateResources()        
        recipe.Start()
        u = 0
        if(camera.IsGrabbing() == True):        
            grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            pylonImg.AttachGrabResultBuffer(grabResult)    
            pImg = pylondataprocessing.Variant(pylonImg)  

            recipe.TriggerUpdate({"image" : pImg}, 1000, pylon.TimeoutHandling_ThrowException, updateObserver, u)
            u += 1
            result = resultCollector.RetrieveResult()
            
            variant = result["result"]
            if not variant.HasError():
                pylonimage = variant.ToImage()
                pylonimage.Save(pylon.ImageFileFormat_Png, "output.png")

        recipe.Stop()
        recipe.DeallocateResources()
        recipe.Unload()
        
    except genicam.GenericException as e:
        # Error handling.
        print("An exception occurred.")
        print(e)
        exitCode = 1
    except Exception as e:
        print("An unexpected exception occurred.")
        print(e)
        exitCode = 1

    sys.exit(exitCode)
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(str(e))
