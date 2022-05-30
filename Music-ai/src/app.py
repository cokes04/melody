import time
import random
import pickle
import boto3

from generate import get_midi
from model import load_models
from constants import *

s3_resource = boto3.resource("s3")
s3_client = boto3.client("s3")

model, att_model = load_models(MODEL_PATH)
data_for_emotion = pickle.loads(s3_resource.Object(BUCKET_NAME, "tmp/data").get()["Body"].read())
note_to_int, int_to_note, duration_to_int, int_to_duration = pickle.loads(s3_resource.Object(BUCKET_NAME, "tmp/table").get()["Body"].read())
tables = (note_to_int, int_to_note, duration_to_int, int_to_duration)

os.makedirs(GENERATE_DIR, exist_ok=True)

def handler(event, context) :
    input_data = event
    print(f"Input Data : {input_data}")

    emotion, music_len, noise_num = input_data['emotion'], input_data['music_len'], input_data['noise_num']
    result_midi = get_midi(model, data_for_emotion, emotion, music_len, noise_num, tables)

    url, upload_result = upload_file_s3(result_midi)

    response = {
        "result": upload_result,
        "url": url,
    }
    print(f"Output Data : {response}")
    return response

def upload_file_s3(midistream):
    try:
        timestr = time.strftime("%Y%m%d%H%M%S")
        rand = str(random.randint(10000, 99999))
        file_name = rand + timestr + ".midi"

        file = midistream.write("midi", fp=os.path.join(GENERATE_DIR, file_name))
        s3_client.upload_file(file, BUCKET_NAME,  f"generatedMusic/{file_name}", ExtraArgs={'ACL':'public-read'})
        url = S3_GENERATED_MUSIC_URL + "/" + file_name
        print("S3 UPLOAD SUCCESS")
        return [url, True]

    except Exception as e :
        print("S3 UPLOAD FAILED")
        print(e)
        return [None, False]

    finally:
        if os.path.exists(file):
            os.remove(file)