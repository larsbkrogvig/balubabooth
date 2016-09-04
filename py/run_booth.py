import logging
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
import sys

from datetime import datetime

import gphoto2 as gp


class Booth(object):

    def __init__(self, localpath='/tmp'):
        """Initiate joystick, context, camera"""
        logging.basicConfig(format='%(levelname)s: %(na'
                                   'me)s: %(message)s', level=logging.WARNING)
        gp.check_result(gp.use_python_logging())

        self.context = gp.gp_context_new()
        self.camera = gp.check_result(gp.gp_camera_new())
        gp.check_result(gp.gp_camera_init(self.camera, self.context))

        self.localpath = localpath

        # The order of things here might not be correct, but it should work
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0) # Take first joystick
        self.joystick.init()
        pygame.init()
        self.event = pygame.event

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        gp.gp_camera_exit(self.camera, self.context)
        print "Camera connection closed"

    def wait_for_x_press(self):

        self.event.get() # Discards all waiting events

        while True:
            event = self.event.wait()
            if event.dict.get('button') == 2 and event.type == 11:
                # X was pressed down
                break
            else:
                print "Other button pressed/unpressed"

        print "X was pressed"

    def capture_and_save(self):
        """Capture an image, save it and return the local path"""
        print('Capturing image')
        file_path = gp.check_result(gp.gp_camera_capture(self.camera,
                                                         gp.GP_CAPTURE_IMAGE,
                                                         self.context))
        capture_time = datetime.now().strftime("%Y%m%d-%H:%M:%S.%f")[:-4]
        filename = capture_time+'.jpg'

        print('Camera file path: {0}/{1}'.format(file_path.folder, filename)) #file_path.name

        target = os.path.join(self.localpath, filename)

        print('Copying image to', target)
        camera_file = gp.check_result(gp.gp_camera_file_get(self.camera,
                                                            file_path.folder,
                                                            file_path.name,
                                                            gp.GP_FILE_TYPE_NORMAL,
                                                            self.context))

        gp.check_result(gp.gp_file_save(camera_file, target))

        return target


def main():
    """Continuously wait for users to press X for photo, save photos"""

    with Booth('/home/pi/photobooth/captured') as photobooth:

        while True:
            print "Press X for photo"
            photobooth.wait_for_x_press()
            try:
                photobooth.capture_and_save()
            except gp.GPhoto2Error as err:
                print err

    return 0


if __name__ == "__main__":
    sys.exit(main())

