from canvasapi import Canvas
import json
from datetime import datetime, date
from bs4 import BeautifulSoup

API_URL = "https://umd.instructure.com"
API_KEY = "1133~EGumCJWevvwkZmNKhDW8YBaQxMG3yvtc8ARQhtWXrEFutKc6XBT4tHGKEFwRxCK8"

data = {}

canvas = Canvas(API_URL, API_KEY)

user = canvas.get_user('self')

for course in user.get_courses(enrollment_state='active'):
    for item in course.get_todo_items():
        print(item.assignment["name"])
        print("For course: " + item.context_name)
        due_date = datetime.strptime(item.assignment["due_at"], "%Y-%m-%dT%H:%M:%SZ")
        print("Due at: " + due_date.strftime("%B %d, %Y %I:%M %p"))
        print("\n\n")