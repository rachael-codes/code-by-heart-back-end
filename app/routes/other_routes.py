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
        if decks.count() > 1:
            decks = decks.order_by(Deck.id)
        response = jsonify([deck.to_json() for deck in decks])
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 200

    # If user is not already in DB, add them in + return empty decks array...
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
def clean_error_message(output, language):
    if "output Limit reached." in output:
        return "You reached the output limit. Did you create an infinite loop?"
    elif "jdoodle" in output:
        if language == 'nodejs':
            starting_match = (re.search("Error", output))
            starting_idx = starting_match.span()[0]
            ending_match = (re.search("at", output))
            ending_idx = ending_match.span()[0]
            # print(frontend_output[starting_idx:ending_idx]) 
            return output[starting_idx:ending_idx]
        elif language == 'python3':
            match = (re.search("jdoodle", output))
            ending_idx = match.span()[1]
            return f"\"{output[ending_idx+1:]}"
        else: 
            match = (re.search("jdoodle", output))
            ending_idx = match.span()[1]
            return output[ending_idx+1:]
    else:
        return output

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
    
    # handle special case (python3 == python)
    if language == 'python': 
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
    output = response.json()["output"] 
    return clean_error_message(output, language)










