from pypylon import pylon
from pypylon import genicam
import numpy


def main():
    imageWindow = pylon.PylonImageWindow()
    imageWindow.Create(1)
    # Create an instant camera object with the camera device found first.
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    camera.Open()

    # Print the model name of the camera.
    print("Using device ", camera.GetDeviceInfo().GetModelName())

    # demonstrate some feature access

    # The parameter MaxNumBuffer can be used to control the count of buffers
    # allocated for grabbing. The default value of this parameter is 10.
    camera.MaxNumBuffer = 5

    camera.TriggerSelector.Value = "FrameStart"
    camera.TriggerMode.Value = "On"
    camera.TriggerSource.Value = "Software"

    camera.SequencerMode.Value = "Off"
    camera.SequencerConfigurationMode = "On"
    camera.SequencerSetSelector.Value = 0
    camera.ExposureTime.Value = 35000
    camera.SequencerSetSave.Value = "Execute"

    camera.SequencerSetSelector.Value = 1
    camera.ExposureTime.Value = 20000
    camera.SequencerSetNext.Value = 0
    camera.SequencerSetSave.Value = "Execute"
    camera.SequencerConfigurationMode = "Off"
    camera.SequencerMode.Value = "On"

    # Start the grabbing of c_countOfImagesToGrab images.
    # The camera device is parameterized with a default configuration which
    # sets up free-running continuous acquisition.
    camera.StartGrabbing(pylon.GrabStrategy_OneByOne)

    clear_buffer(camera)

    while camera.IsGrabbing():
        if camera.WaitForFrameTriggerReady(200, pylon.TimeoutHandling_ThrowException):
            camera.ExecuteSoftwareTrigger()
        # Wait for an image and then retrieve it. A timeout of 5000 ms is used.
        grabResult = camera.RetrieveResult(200, pylon.TimeoutHandling_ThrowException)
        try:
            # Image grabbed successfully?
            if grabResult.GrabSucceeded():
                imageWindow.SetImage(grabResult)
                imageWindow.Show()
            else:
                print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
        except genicam.GenericException as e:
            # Error handling.
            print("An exception occurred.")
            print(e.GetDescription())
        finally:
            grabResult.Release()
    camera.Close()
    imageWindow.Close()


r"""
Clear buffer in camera queue.
"""


def clear_buffer(camera):
    while camera.NumReadyBuffers.GetValue() > 0:
        camera.RetrieveResult(5000, pylon.TimeoutHandling_Return)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(str(e))
