from werkzeug.utils import secure_filename
from app import s3_bucket, ACCESS_KEY, SECRET_KEY

import boto3

bucket = s3_bucket
ACCESS_KEY = ACCESS_KEY
SECRET_KEY = SECRET_KEY


def upload_to_s3(user, content_type, image_file):
    client = boto3.client('s3',
                          region_name='ap-south-1',
                        #   endpoint_url='https://example.trip-gallery.amazonaws.com',
                          aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY)

    filename = secure_filename(image_file.filename)

    client.put_object(Body=image_file,
                      Bucket=bucket,
                      Key=filename,
                      ContentType=content_type)
    object_url = f"https://{bucket}.s3.amazonaws.com/{filename}"
    return object_url