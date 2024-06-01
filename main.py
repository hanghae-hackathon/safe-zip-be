import os, io, requests, uuid, time, json
from pdf2image import convert_from_bytes
from starlette.datastructures import Headers
from fastapi import FastAPI, UploadFile, File, Form
from dotenv import load_dotenv
from rag import get_rag_response

load_dotenv()

app = FastAPI(
    title="Safe Zip",
    description="Safe Zip BE",
)

@app.post("/ocr")
def get(image_file: UploadFile = File(...), is_landlord: str = Form("0")):
    image_files = [image_file]
    
    file_extension = get_file_extension(image_file.filename)
    if file_extension == '.pdf':
        image_files = split_files(image_file)

    texts = [get_text(image_file) for image_file in image_files]
    text = '\n\n'.join(texts) 
    response = get_response(text, is_landlord)
    
    return response

def get_file_extension(filename):
    _, file_extension = os.path.splitext(filename)
    return file_extension

def split_files(image_file):
    image_files = []
    images = convert_from_bytes(image_file.file.read())
        
    for i, image in enumerate(images):
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        jpg_file = UploadFile(
            filename=f"page_{i + 1}.jpg", 
            file=img_byte_arr, 
        )
        
        jpg_file.size = len(img_byte_arr.getvalue())
        jpg_file.headers = Headers({
            "content-disposition": f'form-data; name="image_file"; filename="page_{i + 1}.jpg"',
        })
        
        image_files.append(jpg_file)
    
    return image_files

def get_text(image_file):
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
    'X-OCR-SECRET': os.environ["CLOVA_OCR_SECRET_KEY"]
    }

    response = requests.request("POST", os.environ["CLOVA_OCR_API_URL"], headers=headers, data = payload, files = files)
    result = response.json()

    text = ""
    for field in result['images'][0]['fields']:
        text += field['inferText']

        if field['lineBreak']:
            text += '\n'
        else:
            text += ' '

    return text

def get_response(contract, is_landlord):
    return get_rag_response(contract, is_landlord)

# uvicorn main:app --host 0.0.0.0 --port 8000
# http://localhost:8000/docs