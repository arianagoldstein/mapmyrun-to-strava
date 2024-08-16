# Baton
### transfer your workouts from MapMyRun to Strava
This website automates the transfer of workouts from MapMyRun to Strava. After the user authenticates with MapMyRun and Strava, Baton downloads their workouts from MapMyRun and uploads them to Strava, saving hours of manual effort and ensuring your workout data is seamlessly synchronized between platforms.

## Features
- **Effortless Data Transfer:** Automatically download and upload your workout data with just a few clicks
- **Seamless Authentication:** Securely authenticate with both MapMyRun and Strava to authorize data transfer
- **Error Handling:** Built-in error detection and retries ensure your data transfer process is smooth
- **Custom Workout Parsing:** Supports different workout file formats and intelligently parses workout details


## Getting started
1. Clone the repository.
2. Install the required dependencies with
```
$ pip install -r requirements.txt
```
3. Set up your .env file with your API credentials for Strava as follows:
```
STRAVA_CLIENT_ID=_____
STRAVA_CLIENT_SECRET=_____
STRAVA_REFRESH_TOKEN=_____
```
4. Use the following commands to run locally:
```
$ export FLASK_APP=app.py
$ flask run --port=8000
```