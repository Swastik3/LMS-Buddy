import os
from uagents import Agent, Context, Model, Bureau
from openai import OpenAI
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
from uagents.setup import fund_agent_if_low
from uagents.query import query
import time
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class EmailRequest(Model):
    prompt: str
    course_number: str
    recipient_email: str

class EmailConfirmation(Model):
    # confirmed: bool # not needed
    content: str = ""
    recipient_email: str
    subject: str

# Define the response models
class EmailDraftResponse(Model):
    status: str = "draft_ready"
    draft_content: str
    recipient_email: str
    subject: str

class EmailSentResponse(Model):
    status: str = "success"
    message: str

class EditRequest(Model):
    prompt: str
    existing_draft: EmailDraftResponse


# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r'../credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def send_email(to, subject, body):
    service = get_gmail_service()
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    try:
        message = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        print(f'Message Id: {message["id"]}')
        return message
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

# Define the agent
email_agent = Agent(name="email_curator", seed="your_unique_seed_here", endpoint=["http://localhost:8002/submit"], port=8002)
fund_agent_if_low(email_agent.wallet.address())
print(email_agent.address)
# Define the request models

#don't even need this
# @user_agent.on_event("startup")
# async def startup(ctx: Context):
#     ctx.logger.info(f"User Agent is starting up with address {ctx.agent.address}")
#     time.sleep(1)
#     starting_prompt = input("What do you want the email for: ")
#     req = EmailRequest(prompt=starting_prompt, course_number="CMSC216", recipient_email="swastik3@terpmail.umd.edu")
#     res = await ctx.send(ctx.agent.address, req)
#     print(isinstance(res, EmailDraftResponse))
#     print("Response from the first req: ", res)
#     conf = ""
#     while conf != 'y':
#         conf = input("Enter 'y' to confirm: ")
#         if conf == 'y':
#             await ctx.send(ctx.agent.address, EmailConfirmation(content = "sample", recipient_email="swastik3@terpmail.umd.edu", subject="why hello"))
#         else:
#             edit_prompt = input("How do you want to edit the email: ")
#             await ctx.send(ctx.agent.address, EditRequest(existing_draft=req, prompt= edit_prompt))


@email_agent.on_query(model=EmailRequest, replies={EmailDraftResponse})
async def handle_email_request(ctx: Context, sender: str, msg: EmailRequest):
    ctx.logger.info(f"Received email request: {msg}")

    # Generate email content using OpenAI
    email_content = generate_email_content(msg.prompt, msg.course_number)

    # Prepare and send draft response
    subject = f"Course Information: {msg.course_number}"
    response = EmailDraftResponse(
        status="draft_ready",
        draft_content=email_content["content"],
        recipient_email=msg.recipient_email,
        subject=subject
    )

    temp_json_data = {
        "prompt": msg.prompt,
        "course_number": msg.course_number,
        "email_content": email_content["content"],
        "recipient_email": msg.recipient_email,
        "subject": subject
    }

    temp_json_path = "temp_email_data.json"
    with open(temp_json_path, 'w') as temp_json_file:
        json.dump(temp_json_data, temp_json_file, indent=4)
        
    await ctx.send(sender, response)

@email_agent.on_query(model=EditRequest, replies={EmailDraftResponse})
async def handle_edit_request(ctx: Context, sender : str, msg: EditRequest):
    ctx.logger.info(f"Received email request: {msg}")

    # Generate email content using OpenAI
    output = edit_email_content(msg.prompt, msg.existing_draft.draft_content)
    email_content = output['content']
    subject = output['subject']

    # Prepare and send draft response
    response = EmailDraftResponse(
        status="draft_ready",
        draft_content=email_content,
        recipient_email=msg.recipient_email,
        subject=subject
    )

    temp_json_data = {
        "prompt": msg.prompt,
        "course_number": msg.course_number,
        "email_content": email_content["content"],
        "recipient_email": msg.recipient_email,
        "subject": subject
    }

    temp_json_path = "temp_email_data.json"
    with open(temp_json_path, 'w') as temp_json_file:
        json.dump(temp_json_data, temp_json_file, indent=4)

    print("hello")
    
    await ctx.send(sender, response)

@email_agent.on_query(model=EmailConfirmation, replies={EmailSentResponse})
async def handle_email_confirmation(ctx: Context, sender: str, msg: EmailConfirmation):
    ctx.logger.info(f"Received email confirmation: {msg}")
    # Send email using Gmail API
    content_to_send = msg.content if msg.content else msg.draft_content
    send_status = send_email(msg.recipient_email, msg.subject, content_to_send)

    # Prepare and send response
    response = EmailSentResponse(
        status="success" if send_status else "failure",
        message="Email sent successfully" if send_status else "Failed to send email"
    )

    await ctx.send(sender, response)

def generate_email_content(prompt: str, course_number: str) -> str:
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates email content. You will reply only with the JSON itself, and no other descriptive or explanatory text. Json format must be {content: <text>, subject: <text>}"},
                {"role": "user", "content": f"Create an email about a question to the professor of the course {course_number} based on this prompt: {prompt}"}
            ]
        )
        output = json.loads(response.choices[0].message.content)
        print("Content: ", output['content'],
              "Subject: ", output['subject'])
        return output
    
    except Exception as e:
        print(f"Error generating email content: {e}")
        return f"Unable to generate email content for course {course_number}."
    
def edit_email_content(draft: str, prompt: str) -> str:
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that edits email content. You will reply only with the JSON itself, and no other descriptive or explanatory text. Json format must be {content: <text>, subject: <text>}"},
                {"role": "user", "content": f"Edit this email '{draft}' based on this prompt: {prompt}"}
            ]
        )
        output = json.loads(response.choices[0].message.content)
        print("Content: ", output['content'],
              "Subject: ", output['subject'])
        return output
    except Exception as e:
        print(f"Error generating email content: {e}")
        return f"Unable to generate edit content for."

if __name__ == "__main__":
    email_agent.run()