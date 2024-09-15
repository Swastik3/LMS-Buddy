from flask import Flask, jsonify, request
from uagents import Model
from uagents.query import query
from uagents.envelope import Envelope
import asyncio
# from custom_input_agent import PDFInputResponse
import json
from gmail_agent import EmailRequest, EditRequest, EmailDraftResponse, EmailSentResponse, EmailConfirmation
app = Flask(__name__)

# Define the address of your agent
AGENT_ADDRESS = "agent1qd9m7gwn5ankrvlvdqkxyf6mnsxd6yvhf3xgrj97gv0fjjavj263qt890sm"
EMAIL_AGENT_ADDRESS = ""
# Define data model for incoming requests
class PDFProcessRequest(Model):
    pdf_path: str
    image_dir: str
    image_dir: str 
    json_name: str

class TestResponse(Model):
    response: str

@app.route("/process_pdf", methods=["POST"])
async def process_pdf():
    request_data = request.get_json()
    pdf_path = request_data['pdf']
    img_path = request_data['img']
    json_name = request_data['json_name']

    pdf_path="coinchanging.pdf"
    img_path="img_dir"

    print(f"PDF Path: {pdf_path}")
    print(f"Image Path: {img_path}")

    response = await query(destination = AGENT_ADDRESS, message = PDFProcessRequest(pdf_path = pdf_path, image_dir = img_path),timeout = 15.0)
    print(response)
    if isinstance(response, Envelope):
        data = json.loads(response.decode_payload())
        return data

    else:
        return "not an instance"

    # response = json.loads(response.decode_payload())
    # return data

@app.route("/draft-email", methods=["POST"])
async def draft_email():
    request_data = request.get_json()
    email = request_data['email_to']
    course_number = request_data['course_number']
    prompt = request_data['prompt']
    draft = request_data.get('draft', None)
    subject = request_data.get('subject', None)

    print(f"Email: {email}")
    print(f"PROMPT: {prompt}")
    if draft and subject:
        response = await query(destination = EMAIL_AGENT_ADDRESS, message = EditRequest(existing_draft=EmailDraftResponse(draft_content=draft, recipient_email=email, subject=subject), prompt=prompt, recipient_email= email),timeout = 15.0)
    else:
        response = await query(destination = EMAIL_AGENT_ADDRESS, message = EmailRequest(course_number= course_number, prompt=prompt, recipient_email= email),timeout = 15.0)
    print(response)
    return response

@app.route("/send-email", methods=["POST"])
async def send_email():
    request_data = request.get_json()
    email = request_data['email_to']
    draft = request_data.get('draft', None)
    subject = request_data.get('subject', None)

    print(f"Email: {email}")
    print(f"draft: {draft}")
    if draft and subject:
        response = process_sending_email(email, draft, subject)
    print(response.msgstatus)
    response = json.loads(response.decode_payload())
    return response

def process_sending_email(email: str, draft: str, subject: str):
    response = query(destination = EMAIL_AGENT_ADDRESS, message = EmailConfirmation(content= draft, recipient_email=email, subject=subject),timeout = 15.0)
    return response

if __name__ == "__main__":
    app.run(debug=True)
