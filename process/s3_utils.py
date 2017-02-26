import boto
from boto.s3.key import Key
import config as conf

def upload_to_s3(source_file):
    """
    This requirse Amazon boto module - pip install boto
    """
    bucket = conf.output_bucket
    aws_access_key_id = conf.s3_access_key
    aws_secret_access_key = conf.secret_access_key
    conn = boto.connect_s3(aws_access_key_id, aws_secret_access_key)
    bucket = conn.get_bucket(bucket, validate=True)
    dest_file = os.path.basename(source_file).replace(".txt", "")
    k = Key(bucket)
    k.key = dest_file
    target_size = os.path.getsize(source_file)
    uploaded_size = k.set_contents_from_filename(source_file)
    if target_size == uploaded_size:
        return True
    return False