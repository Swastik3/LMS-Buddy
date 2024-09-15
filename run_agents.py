import requests

BASE_URL = "http://localhost:8001/process-pdf"
headers = {
    "Content-Type": "application/json"
}
data = {
    "pdf_path": "sample_pdfs/sample2.pdf",
    "image_dir": "extracted_images"
}

response = requests.post(BASE_URL, json=data, headers=headers)