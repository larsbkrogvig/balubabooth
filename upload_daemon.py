import os
import sys
from datetime import datetime
from time import sleep

captured_path = '/home/pi/photobooth/captured'
uploaded_path = '/home/pi/photobooth/uploaded'


def find_and_upload_photos():
    """Looks for photos in 'captured' folder, uploads them"""
    files = [f for f in os.listdir(captured_path) if f.endswith('.jpg')]
    if files:
        print "Uploading {0}".format(', '.join(files))
        for file_path in files:
            upload_photo(file_path)
    else:
        print "Found no files to upload"


def upload_photo(f):
    """Uploads single photo f"""
    file_name = os.path.basename(f)

    # UPLOAD PHOTO!

    print "Moving {0}".format(file_name)
    os.rename(os.path.join(captured_path, file_name),
              os.path.join(uploaded_path, file_name))
    pass


def main():
    """Polls 'captured' folder every `interval` seconds, uploads photos"""

    interval = 10

    while True:

        print '{0} - Looking for files to upload'.format(datetime.now().strftime('%H:%m:%S'))

        find_and_upload_photos()

        print "Waiting for {0} seconds".format(interval)
        sleep(interval)


if __name__ == "__main__":
    sys.exit(main())