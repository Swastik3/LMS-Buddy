import requests
import base64
import json
from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low
from dotenv import load_dotenv
import os
import time


prompt = '''Create a visually appealing and comprehensive study schedule image for a college student with the following specifications:
Overall Layout:

Design a weekly calendar grid (Monday to Sunday) with time slots from 8 AM to 11 PM.
Use a clean, modern design with a soft color palette (light blues, greens, and grays) to enhance readability.
Include a small monthly overview calendar in the top right corner, highlighting important dates.

Header:

At the top, display "Sarah's Study Schedule: Spring Semester 2025" in a stylish, sans-serif font.
Below the title, add the current week's dates (e.g., "May 1 - May 7, 2025").

Subject Color Coding:

Assign distinct pastel colors to each subject:

Mathematics (Calculus II): Light Blue
Physics (Quantum Mechanics): Soft Green
Computer Science (Data Structures): Pale Yellow
Literature (20th Century American Novels): Light Pink
Psychology (Cognitive Neuroscience): Lavender



Schedule Details:

Mathematics:

Monday, Wednesday, Friday: 10 AM - 11:30 AM (Class)
Tuesday, Thursday: 2 PM - 4 PM (Study sessions)
Problem set due every Friday at 11:59 PM


Physics:

Tuesday, Thursday: 9 AM - 10:30 AM (Class)
Monday, Wednesday: 3 PM - 5 PM (Lab sessions)
Problem set due every Monday at 8 AM


Computer Science:

Monday, Wednesday, Friday: 1 PM - 2:30 PM (Class)
Saturday: 10 AM - 12 PM (Programming practice)
Coding project due May 15th


Literature:

Tuesday, Thursday: 11 AM - 12:30 PM (Class)
Wednesday, Friday: 7 PM - 8:30 PM (Reading time)
Essay on "The Great Gatsby" due May 10th


Psychology:

Monday, Wednesday: 8:30 AM - 10 AM (Class)
Friday: 4 PM - 6 PM (Research group meeting)
Midterm exam on May 12th



Additional Elements:

Study Blocks:

Allocate 2-hour study blocks for each subject, distributed throughout the week.
Label each block with the subject name and specific topics to cover.


Exam Preparation:

Highlight May 12th for the Psychology midterm.
Add extra study sessions for Psychology on May 10th and 11th.


Assignment Reminders:

Use small icons (e.g., a document symbol) to mark assignment due dates.
Add text reminders for upcoming deadlines in a sidebar.


Productivity Tips:

Include a small section with 3-4 productivity tips, such as:

"Use the Pomodoro Technique: 25 min study, 5 min break"
"Review notes within 24 hours of each class"
"Stay hydrated and take regular breaks"




Progress Tracking:

Add a mini habit tracker for daily goals like "Reviewed flash cards" or "Completed practice problems".


Extracurricular Activities:

Include time slots for:

Gym sessions (Tuesday, Thursday, Saturday: 7 AM - 8 AM)
Chess club meeting (Wednesday: 6 PM - 7 PM)
Part-time job at the library (Saturday: 1 PM - 5 PM)




Meal Planning:

Mark breakfast, lunch, and dinner times with small plate icons.
Highlight Sunday evening for meal prep.


Relaxation Time:

Designate Friday evening and Sunday afternoon as "Free Time" with a fun icon.


Sleep Schedule:

Shade the hours from 11 PM to 7 AM in a light gray to emphasize a consistent sleep schedule.



Visual Elements:

Use clean lines and subtle shadows to separate different sections.
Incorporate small, relevant icons for each subject (e.g., calculator for Math, atom for Physics).
Add motivational quotes in elegant typography at the bottom of the schedule.
Create a visually pleasing legend explaining the color coding and icons used.

Accessibility Features:

Ensure high contrast between text and background colors.
Use patterns in addition to colors to differentiate subjects for color-blind users.

Remember to balance information density with visual clarity to create an effective and visually appealing study schedule.'''
# Load environment variables
load_dotenv()

# Define a model for the image generation request
class ImageRequest(Model):
    prompt: str
    steps: int = 50

# Define a model for the image generation response
class ImageResponse(Model):
    success: bool
    message: str
    file_path: str = ""

image_protocol = Protocol("Image Generation")

@image_protocol.on_message(model=ImageRequest, replies = ImageResponse)
async def handle_image_request(ctx: Context, sender: str, msg: ImageRequest):
    start_time = time.time()
    ctx.logger.info(f"Received image generation request from {sender}")

    try:
        # Prepare the payload
        payload = {
            "prompt": msg.prompt,
            "steps": msg.steps
        }

        # Call model endpoint
        res = requests.post(
            f"https://model-{MODEL_ID}.api.baseten.co/production/predict",
            headers={"Authorization": f"Api-Key {BASETEN_API_KEY}"},
            json=payload
        )

        res.raise_for_status()  # Raise an exception for bad responses

        img_b64 = json.loads(res.text).get("data")
        img = base64.b64decode(img_b64)

        # Generate a unique filename
        # file_name = f"generated_image_{ctx.storage.get('image_counter', 0)}.png"
        # ctx.storage.set('image_counter', ctx.storage.get('image_counter', 0) + 1)

        # Save the image
        with open("bruh.png", "wb") as img_file:
            img_file.write(img)
        ctx.logger.info(f"Time Taken:  {time.time()-start_time}")
        await ctx.send(sender, ImageResponse(success=True, message="Image generated successfully", file_path="bruh.png"))

    except Exception as e:
        ctx.logger.error(f"Error generating image: {str(e)}")
        await ctx.send(sender, ImageResponse(success=False, message=f"Error generating image: {str(e)}"))

# Create the agent
image_agent = Agent(name="image_generator", seed="your_seed_here", endpoint="http://localhost:8000", port=8000, mailbox="aee14fad-54fc-4463-89c7-17b57012561e")
fund_agent_if_low(image_agent.wallet.address())
image_agent.include(image_protocol)
MODEL_ID = "7qk7m1dw"
BASETEN_API_KEY = os.getenv("BASETEN_API_KEY")

@image_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Image Generator Agent is starting up with addres {ctx.agent.address}")
    req = ImageRequest(prompt=prompt, steps=50)
    await ctx.send(ctx.agent.address, req)


if __name__ == "__main__":
    start_time = time.time()
    image_agent.run()