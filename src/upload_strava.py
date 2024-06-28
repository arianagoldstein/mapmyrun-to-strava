import os
import requests
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

# Strava API URLs
TOKEN_URL = "https://www.strava.com/oauth/token"
UPLOAD_URL = "https://www.strava.com/api/v3/uploads"


def get_access_token(client_id, client_secret, refresh_token):
    """
    Get a new access token using the refresh token
    """
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "f": "json"
    }
    response = requests.post(TOKEN_URL, data=payload)
    return response.json()["access_token"]

def upload_workout(file_path, access_token, workout_type, workout_name):
    """
    Upload a workout file to Strava
    """
    with open(file_path, "rb") as file:
        files = {'file': file}
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        payload = {
            "data_type": "tcx",
            "name": workout_name,
            "description": "Uploaded from MapMyRun",
            "activity_type": workout_type
        }
        response = requests.post(UPLOAD_URL, headers=headers, data=payload, files=files)
        return response.json()

def main():
    # Get a new access token
    access_token = get_access_token(STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN)

    # Directory with TCX files
    tcx_directory = "src/workout_files"

    workout_type_mapping = {
        'run': 'run',
        'ride': 'ride',
        'swim': 'swim',
        'hike': 'hike',
        'walk': 'walk',
        'other': 'other'
    }

    # Upload each tcx file
    for filename in os.listdir(tcx_directory):
        if filename.endswith(".tcx"):
            file_path = os.path.join(tcx_directory, filename)
            workout_type = 'other'
            for key in workout_type_mapping:
                if key in filename:
                    workout_type = workout_type_mapping[key]
                    break
            workout_name = os.path.splitext(filename)[1]
            response = upload_workout(file_path, access_token, workout_type, workout_name)
            print(f"Uploaded {filename}: {response}")


if __name__ == "__main__":
    main()