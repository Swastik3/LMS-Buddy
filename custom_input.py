import shutil
import fitz  # PyMuPDF
import io
from PIL import Image
import os
import google.generativeai as genai
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # Replace with your actual API key
print("This is your api key: ", GEMINI_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
# GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent'

def extract_pdf_content(file_path, image_output_dir):
    # Open the PDF file
    pdf_document = fitz.open(file_path)
    
    # Initialize variables to store text and image information
    text_content = ""
    image_count = 0

    # Ensure the output directory exists
    if os.path.exists(image_output_dir):
        # Delete the contents of the directory
        for filename in os.listdir(image_output_dir):
            file_path = os.path.join(image_output_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    os.makedirs(image_output_dir, exist_ok=True)
    
    # Iterate through all pages
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        
        # Extract text
        text_content += page.get_text()
        print("the page text is ")
        # Extract images
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Save the image
            image = Image.open(io.BytesIO(image_bytes))
            image_count += 1
            image_filename = f"image_{page_num + 1}_{img_index + 1}.png"
            image_path = os.path.join(image_output_dir, image_filename)
            image.save(image_path)

    pdf_document.close()
    
    return text_content, image_count

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def perform_ocr_with_gemini(image_path):
    # Encode the image
    base64_image = encode_image(image_path)
    # Set up the model
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Create the contents list with the image and prompt
    contents = [
        {
            "parts": [
                {"text": "Perform OCR on this image and extract all visible text. Return only the extracted text without any additional commentary or explanation. Please DONT output LaTeX"},
                {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}}
            ]
        }
    ]
    # Generate content
    response = model.generate_content(contents)
    return response.text


def process_images_with_ocr(image_dir):
    ocr_results = {}
    for filename in os.listdir(image_dir):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_dir, filename)
            ocr_text = perform_ocr_with_gemini(image_path)
            ocr_results[filename] = ocr_text
    return ocr_results

# Example usage
if __name__ == "__main__":
    

    pdf_path = "sample_pdfs/sample2.pdf"  # Replace with the actual path to your PDF file
    image_dir = "extracted_images"  # Directory to save extracted images
    
    text_content, num_images = extract_pdf_content(pdf_path, image_dir)
    
    print("Extracted Text:")
    print(text_content)
    print(f"\nNumber of images extracted: {num_images}")
    print(f"Images saved in directory: {image_dir}")
    
    # Perform OCR on extracted images
    print("\nPerforming OCR on extracted images...")
    ocr_results = process_images_with_ocr(image_dir)
    print(ocr_results)