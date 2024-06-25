import os
import requests
import pandas as pd
import io
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# load credentials from .env file
load_dotenv()
USERNAME = os.getenv("MAPMYRUN_USERNAME")
PASSWORD = os.getenv("MAPMYRUN_PASSWORD")

CSV_URL = 'https://www.mapmyfitness.com/workout/export/csv'
LOGIN_URL = "https://www.mapmyrun.com/auth/login/"

def login_to_mapmyrun(session, username, password):
    login_payload = {
        "username": username,
        "password": password
    }
    session.post(LOGIN_URL, data=login_payload)

# downloads the csv file containing the links to the workouts
def download_csv(session, url): 
    response = session.get(url) # https://www.mapmyfitness.com/workout/export/csv
    return response.content

# parses the csv file and returns a list of workout urls
def parse_csv(csv_content):
    df = pd.read_csv(io.StringIO(csv_content.decode('utf-8')))
    return df['Link'].tolist()

# downloads the individual workout file as a tcx file
def download_workout(session, url, save_path):
    response = session.get(url)
    with open(save_path, "wb") as f:
        f.write(response.content)


def main():
    with requests.Session() as session:
        login_to_mapmyrun(session, USERNAME, PASSWORD)
        
        csv_content = download_csv(session, CSV_URL)

        workout_urls = parse_csv(csv_content)

        for i, url in enumerate(workout_urls):
            print(i, url)

            download_ur = f'https://www.mapmyrun.com{url}'
            download_workout(session, url, f"data/workout_{i}.gpx")

            print(f"Downloading workout {i+1}/{len(workout_urls)}")


if __name__ == "__main__":
    main()