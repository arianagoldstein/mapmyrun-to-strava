import os
import re
import time
from dotenv import load_dotenv
from stravalib.client import Client
from stravalib.exc import RateLimitExceeded, ActivityUploadFailed
from src.utils import update_progress

# Load credentials from .env file
load_dotenv()

# Directory with TCX files
TCX_DIRECTORY = "src/workout_files"
PROGRESS_FILE = 'upload_progress.json'
client = Client()

def upload_activity(file_path, activity_type, activity_name):
    """
    Upload an activity file to Strava
    """
    with open(file_path, "rb") as file:
        try:
            upload = client.upload_activity(
                activity_file=file,
                data_type="tcx",
                name=activity_name,
                description="Uploaded from MapMyRun",
                activity_type=activity_type
            )
            return upload.wait()
        except Exception as e:
            print(f"Exception during upload: {e}")
            print(upload)
            raise


def parse_filename(filename):
    """
    Parse the workout type and name from the filename
    """
    name = filename[:-4]  # Remove .tcx extension
    
    # Dictionary to map verbs to nouns for activity types
    activity_map = {
        'Ran': 'Run',
        'Hiked': 'Hike',
        'Rode': 'Ride',
        'Walked': 'Walk'
    }
    
    # Pattern for "3.87mi Hike" format
    pattern1 = r'([\d.]+mi)\s+(.+?)(?:\s+\(\d+\))?$'
    
    # Pattern for "Ran 4.02 mi on 11_10_18" format
    pattern2 = r'(\w+)\s+([\d.]+)\s*mi\s+on\s+\d+_\d+_\d+'
    
    match1 = re.match(pattern1, name)
    match2 = re.match(pattern2, name)
    
    if match1:
        distance, activity_type = match1.groups()
        return f"{distance} {activity_type}", activity_type
    elif match2:
        verb, distance = match2.groups()
        activity_type = activity_map.get(verb, 'Other')
        return f"{distance}mi {activity_type}", activity_type
    else:
        # If the filename doesn't match either expected format, return the whole name as is
        return name, "Other"
    

def upload_strava_data(access_token):
    """
    Upload all TCX files in the TCX_DIRECTORY
    """
    client.access_token = access_token
    tcx_files = [f for f in os.listdir(TCX_DIRECTORY) if f.endswith(".tcx")]
    total_files = len(tcx_files)

    for i, filename in enumerate(tcx_files):
        file_path = os.path.join(TCX_DIRECTORY, filename)
        activity_name, activity_type = parse_filename(filename)
        print(f"Uploading {filename} as {activity_name} ({activity_type})")

        try:
            upload = upload_activity(file_path, activity_type, activity_name)
            
            # Wait for the upload to complete
            while not upload.is_complete:
                print(f"Waiting for upload to complete: {upload.status}")
                time.sleep(1)
                upload.refresh()

            if upload.is_error:
                print(f"Error uploading {filename}: {upload.error}")
            else:
                print(f"Successfully uploaded {filename}: Activity ID {upload.activity_id}")

        except RateLimitExceeded as e:
            print(f"Rate limit exceeded. Waiting for {e.timeout} seconds before retrying.")
            time.sleep(e.timeout)
            i -= 1  # Retry this file
            continue
        except ActivityUploadFailed as e:
            print(f"Failed to upload {filename}: {str(e)} - {e.response.json()}")
        except Exception as e:
            print(f"Failed to upload {filename}: {str(e)}")
            
        percent_complete = ((i+1) / total_files) * 100
        update_progress(percent_complete, PROGRESS_FILE)

    return "Strava workouts uploaded successfully!"