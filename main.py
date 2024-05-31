import requests
import uuid
import time
import json
from fastapi import FastAPI, UploadFile, File

app = FastAPI(
    title="Safe Zip",
    description="TBD",
)

@app.post("/ocr")
def get_ocr(image_file: UploadFile = File(...)):
    
    api_url = 'https://uiahhptqhu.apigw.ntruss.com/custom/v1/31400/63b4cddbeedd991ab8086d51dd7c6cbe9369fa1e2c03e4e8be8dbaae8a614488/general'
    secret_key = 'Y0tTRHRCbE1Ka1lKaHl1YmlZTlp3Z3JTYU5TcEpjS1c='
    
    request_json = {
        'images': [
            {
                'format': 'jpg',
                'name': 'demo'
            }
        ],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }

    payload = {'message': json.dumps(request_json).encode('UTF-8')}
    files = [
    ('file', image_file.file)
    ]
    headers = {
    'X-OCR-SECRET': secret_key
    }

    response = requests.request("POST", api_url, headers=headers, data = payload, files = files)

    result = response.json()
    text = ""
    for field in result['images'][0]['fields']:
        text += field['inferText']

        if field['lineBreak']:
            text += '\n'
        else:
            text += ' '

    print('-------------------')
    print(text)
    print('-------------------')
    return text


# uvicorn main:app --host 0.0.0.0 --port 8000
# http://localhost:8000/docs