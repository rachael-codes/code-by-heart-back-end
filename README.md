# Code by Heart

## Introduction
Code By Heart is a flashcard app that lets you create and save decks of flashcards, and then later review these cards at optimally-spaced intervals according to a spaced repetition algorithm (based on SM-2: https://www.supermemo.com/en/archives1990-2015/english/ol/sm2). Each flashcard can take the form of either a code snippet (in a variety of programming languages) or plain text. Programming languages supported: Python, JavaScript, Go, C++, C, C#, Objective C, Ruby, Java, Scala, Swift, Rust, Kotlin, Elixir. 

## Demo 

https://user-images.githubusercontent.com/71302837/153945654-b4b682f9-dde8-4a2f-ac17-cc1ae07bd66e.mov


## Installation 

### Back-end 

1. Clone this repository. 
2. Set up a virtual environment: `python3 -m venv venv` and `source venv/bin/activate`. 
3. Install the requirements: `pip install -r requirements.txt`. 
4. Get a free API key from: https://www.jdoodle.com/, and then create a `.env` file with:
```
JDOODLE_CLIENT_ID=whatever_your_client_id_is
JDOODLE_CLIENT_SECRET=whatever_your_client_secret_is
```
5. Create a local PostgreSQL database called `code_by_heart`, and then add to the .env file the environment variable `SQLALCHEMY_DATABASE_URI` to hold the path to this database. For example: `SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://postgres:postgres@localhost:5432/code_by_heart`
6. To start up the backend in development mode, run: `flask_env=development && flask run`

### Front-end 
1. Clone this other repository: https://github.com/rachael-codes/code-by-heart-frontend-v2.
2. Install dependencies by running `npm install` or `yarn install`.
3. Create a .env file and add this line: `REACT_APP_BACKEND_URL=whatever_your_backend_url_will_be`. For example: `REACT_APP_BACKEND_URL=http://127.0.0.1:5000`.
4. For user authentication: create a Google Firebase project for Code By Heart. Within it, enable Google as a sign-in method, and add your local host as an authorized domain. 
5. To start up the frontend, run `yarn start` (or npm is you're using that).  
