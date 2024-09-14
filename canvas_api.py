from canvasapi import Canvas
import json
from datetime import datetime, date
from bs4 import BeautifulSoup

API_URL = "https://umd.instructure.com"
API_KEY = "1133~EGumCJWevvwkZmNKhDW8YBaQxMG3yvtc8ARQhtWXrEFutKc6XBT4tHGKEFwRxCK8"

data = {}

canvas = Canvas(API_URL, API_KEY)

user = canvas.get_user('self')
data["name"] = user.name

data["courses"] = {}
courses = user.get_courses(enrollment_state='active')
for course in courses:
    course_data = {}
    course_data["name"] = course.name
    course_data["assignments"] = {}
    assignments = course.get_assignments()
    for assignment in assignments:
        import requests

        assignment_data = {}
        assignment_data["name"] = assignment.name
        assignment_data["due_at"] = assignment.due_at
        assignment_data["points_possible"] = assignment.points_possible

        # Making a GET request to fetch the score
        response = requests.get(f"{API_URL}/api/v1/courses/{course.id}/assignments/{assignment.id}/submissions/self", headers={"Authorization": f"Bearer {API_KEY}"})
        if response.status_code == 200:
            submission_data = response.json()
            assignment_data["score"] = submission_data.get("score")
        else:
            assignment_data["score"] = None

        if assignment.description:
            soup = BeautifulSoup(assignment.description, "html.parser")
            assignment_data["description"] = soup.get_text(separator=' ', strip=True)
        else:
            assignment_data["description"] = None
        course_data["assignments"][assignment.id] = assignment_data

    course_data["files"] = {}
    try:
        files = course.get_files()
        for file in files:
            file_data = {}
            file_data["display_name"] = file.display_name
            file_data["url"] = file.url
            course_data["files"][file.id] = file_data
        print("files recieved course: " + course.name)
    except Exception as e:
        if "unauthorized" in str(e).lower():
            pass
        else:
            raise e

    data["courses"][course.id] = course_data

with open('canvas_data.json', 'w') as outfile:
    json.dump(data, outfile)