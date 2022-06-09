import time
import random
import pickle
import boto3
import json

from generate import get_midi
from model import load_models
from constants import *

s3_resource = boto3.resource("s3")
s3_client = boto3.client("s3")

s3_client.download_file(BUCKET_NAME,  "tmp/model.h5", MODEL_PATH)
model, att_model = load_models(MODEL_PATH)

data_for_emotion = pickle.loads(s3_resource.Object(BUCKET_NAME, "tmp/data").get()["Body"].read())
note_to_int, int_to_note, duration_to_int, int_to_duration = pickle.loads(s3_resource.Object(BUCKET_NAME, "tmp/table").get()["Body"].read())
tables = (note_to_int, int_to_note, duration_to_int, int_to_duration)

os.makedirs(OUTPUT_DIR, exist_ok=True)

def handler(event, context) :
    input_data = json.loads(event["body"])
    print(f"Input Data : {input_data}")

    validation_result = validate(input_data)
    if validation_result != True :
        return validation_result


    emotion, music_len, noise_num = input_data['emotion'], input_data['music_len'], input_data['noise_num']

    save = False
    result_midi = get_midi(model, data_for_emotion, tables, emotion, music_len, noise_num, save)

    url, upload_result = upload_file_s3(result_midi)

    response = {
        "statusCode": 200,
        "body": json.dumps({
            "result": upload_result,
            "url": url,
        })
    }
    print(f"Output Data : {response}")
    return response

def upload_file_s3(midistream):
    try:
        timestr = time.strftime("%Y%m%d%H%M%S")
        rand = str(random.randint(10000, 99999))
        file_name = f"{rand}{timestr}.mid"


        file = midistream.write("midi", fp=os.path.join(OUTPUT_DIR, file_name))
        print("SAVE midi : ", file)

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

def validate(input_data) :
    status_code = 400
    try:
        emotion = input_data['emotion']
        if emotion not in EMOTIONS :
            raise ValueError
    except (KeyError, ValueError) as e :
        return error_response(status_code, f"emotion : {', '.join(EMOTIONS)} 중 하나를 입력해 주세요.")

    try:
        music_len = input_data['music_len']
        if type(music_len) != int:
            raise ValueError
        elif not music_len >= 1 :
            raise ValueError

    except (KeyError, ValueError) as e:
        return error_response(status_code, f"music_len : 1 이상의 정수를 입력해 주세요.")

    try:
        noise_num = input_data['noise_num']
        if type(noise_num) != int:
            raise ValueError
        elif not noise_num >= 0:
            raise ValueError

    except (KeyError, ValueError) as e:
        return error_response(status_code, f"noise_num : 0 이상의 정수를 입력해 주세요.")

    return True

def error_response(code, message) :
    return {
        "statusCode": code,
        "body": json.dumps({
            "result": False,
            "message": message,
        })
    }