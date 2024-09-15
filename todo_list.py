from canvasapi import Canvas
import json
from datetime import datetime, date
from bs4 import BeautifulSoup

API_URL = "https://umd.instructure.com"
API_KEY = "1133~EGumCJWevvwkZmNKhDW8YBaQxMG3yvtc8ARQhtWXrEFutKc6XBT4tHGKEFwRxCK8"

data = {}

canvas = Canvas(API_URL, API_KEY)

user = canvas.get_user('self')

def get_todo():
  out=""
  for course in user.get_courses(enrollment_state='active'):
    if "comm107" in course.name.lower() or "math240" in course.name.lower() or "math241" in course.name.lower() or "math246" in course.name.lower() or "cmsc351" in course.name.lower() or "cmsc320" in course.name.lower():
        for item in course.get_todo_items():
            out+=item.assignment["name"]
            out+="For course: " + item.context_name
            due_date = datetime.strptime(item.assignment["due_at"], "%Y-%m-%dT%H:%M:%SZ")
            out+="Due at: " + due_date.strftime("%B %d, %Y %I:%M %p")
  return out