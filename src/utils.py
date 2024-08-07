import json
import os

def update_progress(percent_complete, progress_file):
    """
    Update the progress file with the current percentage complete
    """
    with open(progress_file, 'w') as f:
        json.dump({'progress': percent_complete}, f)

def get_progress(progress_file):
    """
    Get the current progress from the progress file
    """
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            return json.load(f).get('progress', 0)
    return 0