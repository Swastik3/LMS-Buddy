import json
import requests
import os
from PyPDF2 import PdfMerger

def download_and_combine_pdfs(json_file, course_name):
    # Load JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
  
    pdf_files = []

    # Download PDF files
    for file_id, file_info in data['files'].items():
        if file_info['display_name'].endswith('.pdf'):
            response = requests.get(file_info['url'])
            if response.status_code == 200:
                filename = file_info['display_name']
                with open(filename, 'wb') as f:
                    f.write(response.content)
                pdf_files.append(filename)
                print(f"Downloaded: {filename}")

    # Combine PDF files
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    
    output_filename = f"{course_name}_combined.pdf"
    merger.write(output_filename)
    merger.close()

    # Clean up individual PDF files
    for pdf in pdf_files:
        os.remove(pdf)

    print(f"Combined PDF saved as: {output_filename}")

# Usage
json_file = 'canassign\MATH246.json'  # Replace with your JSON file name
download_and_combine_pdfs(json_file, 'MATH246')