from flask import Flask, jsonify, request
from uagents import Model
from uagents.query import query
import asyncio
from custom_input_agent import CustomInputResponse

app = Flask(__name__)

# Define the address of your agent
AGENT_ADDRESS = "agent1qd9m7gwn5ankrvlvdqkxyf6mnsxd6yvhf3xgrj97gv0fjjavj263qt890sm"

# Define data model for incoming requests
class PDFProcessRequest(Model):
    pdf_path: str
    image_dir: str

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@app.route("/process-pdf", methods=['POST'])
def process_pdf():
    data = request.json
    pdf_path = data.get('pdf_path')
    image_dir = data.get('image_dir')
    
    if not pdf_path or not image_dir:
        return jsonify({"error": "Missing pdf_path or image_dir", "status": "error"}), 400
    
    # Make a call to the agent with the request and handle the response
    msg_status = run_async(make_agent_call(PDFProcessRequest(pdf_path=pdf_path, image_dir=image_dir)))
    
    if msg_status is None:
        return jsonify({"error": "Failed to communicate with the agent", "status": "failed"}), 503
    
    response = msg_status.detail

    # Convert MsgStatus to a dictionary

    return response

async def make_agent_call(req: Model):
    try:
        response = await query(
            destination=AGENT_ADDRESS,
            message=req,
            timeout=15.0
        )
        return response
    except Exception as e:
        app.logger.error(f"Error communicating with agent: {str(e)}")
        return None

if __name__ == "__main__":
    app.run(debug=True)