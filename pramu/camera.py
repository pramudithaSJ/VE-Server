from picamera2 import Picamera2

class Camera:

    def __init__(self):
        # Initialize Picamera
        self.picam2 = Picamera2()
        self.picam2.preview_configuration.main.size = (1920, 1080)
        self.picam2.preview_configuration.main.format = "RGB888"
        self.picam2.preview_configuration.align()
        self.picam2.configure("preview")
        self.picam2.start()
    
    def get_frame(self):
        return self.picam2.capture_array()