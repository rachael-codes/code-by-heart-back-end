from flask import Blueprint, request
import requests, json
import re 
import os 
from dotenv import load_dotenv

compiler_bp = Blueprint('compiler', __name__, url_prefix="/compile")

def clean_error_message(msg):
    match = (re.search("jdoodle", msg))
    ending_idx = match.span()[1]
    return msg[ending_idx+1:]

# Route to run Python code through Jdoodle's compiler! 
@compiler_bp.route("", methods=["POST"])
def compile():
    '''
    Purpose: Calls Jdoodle Code Compiler API
    Returns: either an empty string (if there was no `print` statement), 
            a string error message (if the code couldn't be compiled),
            or some string output (if code was compiled AND there was a print statement)
    '''
    path = "https://api.jdoodle.com/v1/execute"
    request_body = request.get_json()
    code_to_compile, language = request_body["code"], request_body["language"]
    if language == 'python': # Note: Python is only special case that needs a num
        language = 'python3'

    payload = {
        "script": f"{code_to_compile}", 
        "stdin": "",
        "language": f"{language}",
        "versionIndex": "3", 
        "clientId": os.environ.get("JDOODLE_CLIENT_ID"),
        "clientSecret": os.environ.get("JDOODLE_CLIENT_SECRET")
    }
    headers = {"Content-Type" : "application/json"}
    response = requests.post(url=path, headers=headers, data=json.dumps(payload))

    # get either code output or error message output; if error message, shorten it 
    frontend_output = response.json()["output"] 
    if "jdoodle" in frontend_output:
        if language == 'python3': # as usual, python is an exception
            return f"\"{clean_error_message(frontend_output)}"
        else:
            return clean_error_message(frontend_output)

    # return custom message in case of infinite loop 
    if "output Limit reached." in frontend_output:
        return "You reached your output limit. Did you create an infinite loop?"

    # TO-DO: handle error so something still gets returned to front-end in case of 404 
    return frontend_output