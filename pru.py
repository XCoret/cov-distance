
import os
from google.cloud import storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"key.json"
os.environ['GCP_BUCKET_NAME'] = 'cov-distance-bucket'

def list_blobs():
    """Lists all the blobs in the bucket."""
    # bucket_name = "your-bucket-name"
    bucket_name = os.environ.get('GCP_BUCKET_NAME')
    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    for blob in blobs:
        if blob.name == 'TownCentreXVID_short.mp4':
            blob.download_to_filename('static/Tounnnwn.mp4')
        print(blob.name)





def get_blob(source_blob):
    if not source_blob in os.listdir('input_data'):
        dest_file_name = 'input_data/{}'.format(source_blob)

        bucket_name = os.environ.get('GCP_BUCKET_NAME')
        storage_client = storage.Client()

        # Note: Client.list_blobs requires at least package version 1.17.0.
        blobs = storage_client.list_blobs(bucket_name)
        for blob in blobs:
            if blob.name == source_blob:
                blob.download_to_filename(dest_file_name)
    else:
        dest_file_name = 'input_data/{}'.format(source_blob)

    return dest_file_name

print(get_blob('TownCentreXVID_short.mp4'))


