from flask import Blueprint, request, jsonify
from app import db
import requests, json
import re 
import os 
from dotenv import load_dotenv
from app.models.deck import Deck
from app.models.client import Client

app_bp = Blueprint('app', __name__)

@app_bp.route("/load-user-decks", methods=["POST"])
def load_decks():
    '''
    Purpose: Checks if a user is in the DB (after Google authenticates them
    in the frontend), and then either:
        1) returns an array of user's decks (if user was already in the DB) 
        OR
        2) adds the user to the DB and returns an empty array of decks for 
        the user to start out with 

    request_body = { "id" : id, "email" : email, "displayName" : displayName }
    '''
    request_body = request.get_json()

    # Check if user is already in the DB, and if so, load their decks...
    client = Client.query.filter_by(email=request_body["email"]).first()
    if client:
        decks = Deck.query.filter_by(owner_id=client.id) 
        response = jsonify([deck.to_json() for deck in decks])
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 200

    # If user is not already in the DB, add them in, and return an empty decks array...
    new_client = Client(
        id = request_body["uid"],
        email = request_body["email"],
        display_name = request_body["displayName"]
    )
    db.session.add(new_client)
    db.session.commit()

    response = jsonify([]) # new clients should start out with empty decks array
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200

# ---------- # ---------- # ---------- # ---------- # ---------- # ---------- # 

# helper used in compile route immediately below
def clean_error_message(msg):
    match = (re.search("jdoodle", msg))
    ending_idx = match.span()[1]
    return msg[ending_idx+1:]

# Runs code via Jdoodle's compiler API
@app_bp.route("/compile", methods=["POST"])
def compile():
    '''
    Purpose: Calls Jdoodle Code Compiler API
    Returns: either an empty string (if there was no `print` statement), 
            a string error message (if the code couldn't be compiled),
            or some string output (if code was compiled + there was a `print`)
    '''
    path = "https://api.jdoodle.com/v1/execute"
    request_body = request.get_json()
    code_to_compile, language = request_body["code"], request_body["language"]
    if language == 'python': # Note: python is special case that needs a num
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
    print(frontend_output) 
    return frontend_output








