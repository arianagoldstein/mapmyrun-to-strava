import os
import re
from dotenv import load_dotenv
from stravalib.client import Client

# Load credentials from .env file
load_dotenv()

# Directory with TCX files
TCX_DIRECTORY = "src/workout_files"
client = Client()


def upload_activity(file_path, activity_type, activity_name):
    """
    Upload an activity file to Strava
    """
    with open(file_path, "rb") as file:
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
    # Ensure the filename matches the format "5.0mi Run" in order to parse the distance and activity type
    # Note: filenames may be identical, so there may be a sequence number at the end that we ignore during the upload
    match = re.match(r'([\d.]+mi)\s+(.+?)(?:\s+\(\d+\))?$', name)
    if match:
        distance, activity_type = match.groups()
        return f"{distance} {activity_type}", activity_type
    else:
        # If the filename doesn't match the expected format, return the whole name as is
        return name, "Other"
    

def upload_strava_data(access_token):
    """
    Upload all TCX files in the TCX_DIRECTORY
    """
    client.access_token = access_token
    for filename in os.listdir(TCX_DIRECTORY):
        if filename.endswith(".tcx"):
            file_path = os.path.join(TCX_DIRECTORY, filename)
            activity_name, activity_type = parse_filename(filename)
            try:
                activity = upload_activity(file_path, activity_type, activity_name)
                print(f"Uploaded {filename}: Activity ID {activity.id}")
            except Exception as e:
                print(f"Failed to upload {filename}: {str(e)}")
    return "Strava workouts uploaded successfully!"