from flask import Flask, jsonify, request
from uagents import Model
from uagents.query import query
from uagents.envelope import Envelope
import asyncio
from custom_input_agent import PDFInputResponse
import json

app = Flask(__name__)

# Define the address of your agent
AGENT_ADDRESS = "agent1qd9m7gwn5ankrvlvdqkxyf6mnsxd6yvhf3xgrj97gv0fjjavj263qt890sm"

# Define data model for incoming requests
class PDFProcessRequest(Model):
    pdf_path: str
    image_dir: str 

class TestResponse(Model):
    response: str

@app.route("/process_pdf", methods=["POST"])
async def process_pdf():
    request_data = request.get_json()
    pdf_path = request_data['pdf']
    img_path = request_data['img']

    print(f"PDF Path: {pdf_path}")
    print(f"Image Path: {img_path}")

    response = await query(destination = AGENT_ADDRESS, message = PDFProcessRequest(pdf_path = pdf_path, image_dir = img_path),timeout = 15.0)

    response = json.loads(response.decode_payload())
    return response

if __name__ == "__main__":
    app.run(debug=True)