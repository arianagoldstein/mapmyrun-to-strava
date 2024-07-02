import os
import re
from dotenv import load_dotenv
from stravalib.client import Client
from flask import Flask, request, redirect

# Load credentials from .env file
load_dotenv()
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

# Strava API URLs
TOKEN_URL = "https://www.strava.com/oauth/token"
UPLOAD_URL = "https://www.strava.com/api/v3/uploads"
REDIRECT_URI = 'http://localhost:8000/authorized'

# Directory with TCX files
TCX_DIRECTORY = "src/workout_files"

app = Flask(__name__)
client = Client()


@app.route("/")
def login():
    auth_uri = client.authorization_url(
        client_id = STRAVA_CLIENT_ID,
        redirect_uri = REDIRECT_URI,
        scope = ["activity:write", "activity:read_all"]
    )
    return redirect(auth_uri)


@app.route("/authorized")
def authorized():
    code = request.args.get('code')
    token_response = client.exchange_code_for_token(
        client_id = STRAVA_CLIENT_ID,
        client_secret = STRAVA_CLIENT_SECRET,
        code = code
    )
    client.access_token = token_response["access_token"]
    client.refresh_token = token_response["refresh_token"]
    
    upload_activities()
    return "Activities uploaded successfully!"


def get_access_token(client):
    """
    Get a new access token using the refresh token
    """
    response = client.refresh_access_token(
        client_id = STRAVA_CLIENT_ID,
        client_secret = STRAVA_CLIENT_SECRET,
        refresh_token = STRAVA_REFRESH_TOKEN
    )
    return response["access_token"]


def upload_activity(file_path, activity_type, activity_name):
    """
    Upload an activity file to Strava
    """
    with open(file_path, "rb") as file:
        files = {'file': file}
        upload = client.upload_activity(
            activity_file = file,
            data_type = "tcx",
            name = activity_name,
            description = "Uploaded from MapMyRun",
            activity_type = activity_type
        )
        return upload.wait()

def parse_filename(filename):
    """
    Parse the workout type and name from the filename
    """
    name = filename[:-4]
    match = re.match(r'([\d.]+mi)\s+(.+)', name)
    if match:
        distance, activity_type = match.groups()
        return f"{distance} {activity_type}", activity_type
    else:
        # If the filename doesn't match the expected format, return the whole name as is
        return name, "Other"
    

def upload_activities():
    """
    Upload all TCX files in the TCX_DIRECTORY
    """
    for filename in os.listdir(TCX_DIRECTORY):
        if filename.endswith(".tcx"):
            file_path = os.path.join(TCX_DIRECTORY, filename)
            activity_name, activity_type = parse_filename(filename)
            try:
                activity = upload_activity(file_path, activity_type, activity_name)
                print(f"Uploaded {filename}: Activity ID {activity.id}")
            except Exception as e:
                print(f"Failed to upload {filename}: {str(e)}")


def main():
    app.run(port=8000)


if __name__ == "__main__":
    main()