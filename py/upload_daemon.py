import os
import sys
import boto
import gcs_oauth2_boto_plugin
from firebase import firebase
from ConfigParser import ConfigParser

from boto.gs.connection import GSConnection
from boto.gs.key import Key

from datetime import datetime
from time import sleep

captured_path = '/home/pi/photobooth/captured'
uploaded_path = '/home/pi/photobooth/uploaded'
py_path = '/home/pi/photobooth/py'

config = ConfigParser()
config.read(os.path.join(py_path,'config.secret'))

gs_project_id = config.get('Google', 'ProjectId') # my project
gs_bucket_name = gs_project_id + '.appspot.com'
gs_bucket_destination_prefix = 'photobooth'

conn = GSConnection()
bucket = conn.get_bucket(gs_bucket_name)

firebase_secret = config.get('Firebase', 'Secret')
firebase_destination_prefix = 'images'

auth = firebase.FirebaseAuthentication(firebase_secret, config.get('Firebase', 'Email')) # my email
user = auth.get_user()
app = firebase.FirebaseApplication(config.get('Firebase', 'App'),
                                   authentication=None)
app.authentication = auth

#Find the maximum key in Firebase right now, assume format is [0-9]{5}"""
all_things = app.get('/images', None)
i = int(max(all_things.keys())) if all_things else 0


def find_and_upload_photos():
    """Looks for photos in 'captured' folder, uploads them"""
    files = [f for f in os.listdir(captured_path) if f.endswith('.jpg')]
    if files:
        print "Uploading {0}".format(', '.join(files))
        for file_name in files:
            upload_photo(os.path.join(captured_path,file_name))
    else:
        print "Found no files to upload"


def upload_photo(file_path):
    """Uploads single photo f"""
    file_name = os.path.basename(file_path)

    global i
    i += 1

    print "Uploading {0} to Google Cloud Storage".format(file_name)
    k = Key(bucket)
    k.key = '{0}/{1}'.format(gs_bucket_destination_prefix, file_name)
    k.set_contents_from_filename(file_path)

    metadata = {'fileName': file_name}
    app.put('/{0}'.format(firebase_destination_prefix),
            '%.5i' % i, metadata)

    print "Moving {0}".format(file_name)
    os.rename(os.path.join(captured_path, file_name),
              os.path.join(uploaded_path, file_name))


def main():
    """Polls 'captured' folder every `interval` seconds, uploads photos"""

    interval = 1

    while True:

        print '{0} - Looking for files to upload'.format(datetime.now().strftime('%H:%m:%S'))

        find_and_upload_photos()

        print "Waiting for {0} seconds".format(interval)
        sleep(interval)


if __name__ == "__main__":
    sys.exit(main())