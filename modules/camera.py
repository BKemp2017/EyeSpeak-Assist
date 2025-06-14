from picamera2 import Picamera2
import cv2

class Camera:
    def __init__(self, width=640, height=480):
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(main={"format": "RGB888", "size": (width, height)})
        self.picam2.configure(config)
        self.picam2.start()

    def get_frame(self):
        return self.picam2.capture_array()

    def stop(self):
        self.picam2.stop()
        cv2.destroyAllWindows()

    def release(self):
        if self.cap:
            self.cap.release()

