# Functions responsible for accessing flask api.
import requests
import json


api_hostname = "http://api:5000"


def get_json_api(limit, offset, api_url):
    payload = {"limit": limit, "offset": offset}
    response = requests.get(f"{api_hostname}/{api_url}", params=payload)
    content = response.content
    y = json.loads(content)
    return y


def get_all_api():
    response = requests.get("http://api:5000/")
    content = response.content
    y = json.loads(content)
    return y
