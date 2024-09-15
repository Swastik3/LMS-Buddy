from flask import Flask, jsonify, request
from uagents import Model
from uagents.query import query
from uagents.envelope import Envelope
import asyncio
# from custom_input_agent import PDFInputResponse
import json
from gmail_agent import EmailRequest
import os

app = Flask(__name__)

# Define the address of your agent
AGENT_ADDRESS = "agent1qd9m7gwn5ankrvlvdqkxyf6mnsxd6yvhf3xgrj97gv0fjjavj263qt890sm"
EMAIL_AGENT_ADDRESS = "agent1qv9hk62657mx0429je92hltn48vrq3uwdghd20a9l69pzqclp7qhkc6hf8n"

# Define data model for incoming requests
class PDFProcessRequest(Model):
    pdf_path: str
    image_dir: str

class TestResponse(Model):
    response: str

@app.route("/draft_email", methods=["POST"])
async def draft_email():
    request_data = request.get_json()
    email = request_data['email_to']
    course_number = request_data['course_number']
    prompt = request_data['prompt']

    print(f"Email: {email}")
    print(f"Prompt: {prompt}")

    response = await query(destination = EMAIL_AGENT_ADDRESS, message = EmailRequest(prompt = prompt, course_number = course_number, recipient_email = email),timeout = 15.0)

    if response.status == "delivered":
        temp_json_path = "temp_email_data.json"
        try:
            with open(temp_json_path, 'r') as temp_json_file:
                data = json.load(temp_json_file)
            os.remove(temp_json_path)
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)})

    # response = json.loads(response.decode_payload())
    # return data

@app.route("/process_pdf", methods=["POST"])
async def process_pdf():
    request_data = request.get_json()
    pdf_path = request_data['pdf']
    img_path = request_data['img']

    print(f"PDF Path: {pdf_path}")
    print(f"Image Path: {img_path}")

    response = await query(destination = AGENT_ADDRESS, message = PDFProcessRequest(pdf_path = pdf_path, image_dir = img_path),timeout = 15.0)
    print(response)
    if response.status == "delivered":
        temp_json_path = "temp_data.json"
        try:
            with open(temp_json_path, 'r') as temp_json_file:
                data = json.load(temp_json_file)
            os.remove(temp_json_path)
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)})

    # response = json.loads(response.decode_payload())
    # return data

if __name__ == "__main__":
    app.run(debug=True)