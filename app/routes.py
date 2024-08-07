import time
from flask import Blueprint, render_template, request, redirect, session, url_for, jsonify
import os
import requests
import threading
from dotenv import load_dotenv
from src.download_mapmyrun import download_mapmyrun_data, check_login_status
from src.upload_strava import upload_strava_data
from src.utils import get_progress

# Create a blueprint
main = Blueprint('main', __name__)


# Load credentials from .env file
load_dotenv()
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = 'http://localhost:8000/callback'


@main.route("/")
def home():
    strava_authenticated = 'strava_access_token' in session
    return render_template("index.html", strava_authenticated=strava_authenticated)


@main.route("/login")
def login():
    strava_auth_url = "https://www.strava.com/oauth/authorize"
    params = {
        'client_id': STRAVA_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': 'activity:write,read'
    }
    auth_url = f"{strava_auth_url}?{'&'.join(f'{key}={val}' for key, val in params.items())}"
    return redirect(auth_url)


@main.route("/callback")
def callback():
    code = request.args.get("code")
    token_response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': STRAVA_CLIENT_ID,
            'client_secret': STRAVA_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code'
        }
    )
    token_response_data = token_response.json()
    session["strava_access_token"] = token_response_data["access_token"]
    session["refresh_token"] = token_response_data["refresh_token"]
    session["expires_at"] = token_response_data["expires_at"]

    return redirect(url_for("main.home"))


def get_access_token():
    if "expires_at" in session and session["expires_at"] < time.time():
        refresh_response = requests.post(
            'https://www.strava.com/oauth/token',
            data={
                'client_id': STRAVA_CLIENT_ID,
                'client_secret': STRAVA_CLIENT_SECRET,
                'refresh_token': session["refresh_token"],
                'grant_type': 'refresh_token'
            }
        )
        refresh_response_data = refresh_response.json()
        session["strava_access_token"] = refresh_response_data["access_token"]
        session["refresh_token"] = refresh_response_data["refresh_token"]
        session["expires_at"] = refresh_response_data["expires_at"]
    
    return session["strava_access_token"]


def download_workouts(username, password):
    try:
        download_mapmyrun_data(username, password)
    except Exception as e:
        print(f"Error downloading workouts: {str(e)}")


@main.route("/download", methods=["POST"])
def download():
    mapmyrun_username = request.form["mapmyrun_username"]
    mapmyrun_password = request.form["mapmyrun_password"]

    session["mapmyrun_username"] = mapmyrun_username
    session["mapmyrun_password"] = mapmyrun_password

    try:
        if check_login_status(mapmyrun_username, mapmyrun_password):
            # Start workout download in the background
            threading.Thread(target=download_workouts, args=(mapmyrun_username, mapmyrun_password)).start()
            return jsonify({"status": "success", "message": "Download started successfully."})
        else:
            return jsonify({"status": "error", "message": "Invalid MapMyRun credentials."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@main.route("/upload", methods=["POST"])
def upload():
    if "strava_access_token" in session:
        strava_access_token = get_access_token()

        # Upload workouts to Strava
        print("About to upload workouts to Strava")
        try:
            upload_strava_data(strava_access_token)
            return jsonify({"status": "success", "message": "Workouts uploaded successfully."})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    else:
        return jsonify({"status": "error", "message": "Please authenticate with Strava first!"})


@main.route("/download_progress")
def download_progress():
    progress = get_progress('download_progress.json')
    return jsonify({"progress": progress})


@main.route("/upload_progress")
def upload_progress():
    progress = get_progress('upload_progress.json')
    return jsonify({"progress": progress})