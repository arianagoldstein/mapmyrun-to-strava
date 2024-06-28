import csv
import os
import time
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains

# Load credentials from .env file
load_dotenv()
USERNAME = os.getenv("MAPMYRUN_USERNAME")
PASSWORD = os.getenv("MAPMYRUN_PASSWORD")

LOGIN_URL = "https://www.mapmyrun.com/auth/login/"
CSV_URL = 'https://www.mapmyfitness.com/workout/export/csv'


def set_up_driver(workout_files_dir):
    """
    Set up a Chrome driver with options for automatic file download
    """
    chrome_options = Options()
    prefs = {'download.default_directory': workout_files_dir,
             'download.prompt_for_download': False,
             'download.directory_upgrade': True,
             'safebrowsing.enabled': True}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def login(driver):
    """
    Log in to MapMyRun with credentials from env file
    """
    username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email-input")))
    password_field = driver.find_element(By.ID, "Password-input")
    username_field.send_keys(USERNAME)
    password_field.send_keys(PASSWORD)

    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()


def wait_for_download(directory, timeout):
    """
    Wait for a new file to appear in the specified directory
    """
    files_before = set(os.listdir(directory))
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(1)
        files_now = set(os.listdir(directory))
        new_files = files_now - files_before
        if new_files:
            return list(new_files)
    return []


def click_element(driver, element):
    """
    Click an element, scrolling it into view if necessary
    """
    try:
        # Scroll the element into view
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)  # Small pause after scrolling
        element.click()
    except ElementClickInterceptedException:
        # If normal click fails, try JavaScript click
        driver.execute_script("arguments[0].click();", element)


def download_workout_files(driver, csv_file_path, directory):
    """
    Download TCX file for each workout in the CSV file
    """
    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader) # Skip header row

        for row in csv_reader:
            workout_link = row[-1] # Link is in last column of each row

            driver.get(workout_link) # Open workout page

            try:
                time.sleep(2)

                # Wait for and click the 3-dot menu
                three_dot_menu = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'MuiIconButton-root')]"))
                )
                # three_dot_menu.click()
                click_element(driver, three_dot_menu)

                # Wait for and click the TCX download option
                tcx_download = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Download as TCX')]"))
                )
                # tcx_download.click()
                click_element(driver, tcx_download)

                # Wait for the download to complete
                new_files = wait_for_download(directory, 30)
                if new_files:
                    print(f"Downloaded TCX for workout: {workout_link}")
                else:
                    print(f"Failed to download TCX for workout: {workout_link}")

            except (TimeoutException, NoSuchElementException) as e:
                print(f"Error processing workout {workout_link}: {str(e)}")


def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the script
    workout_files_dir = os.path.join(project_dir, "workout_files")
    os.makedirs(workout_files_dir, exist_ok=True)  # Create workout_files directory if it doesn't exist

    driver = set_up_driver(workout_files_dir)

    # Log in
    driver.get(LOGIN_URL)
    login(driver)
    WebDriverWait(driver, 10).until(EC.url_contains("dashboard"))

    # Visit URL to download CSV file
    driver.get(CSV_URL)

    # Re-authenticate if necessary
    if "login" in driver.current_url:
        login(driver)

    # Wait for the CSV download to complete
    wait_for_download(workout_files_dir, 120)

    # Find the most recently downloaded CSV file
    csv_file_path = max((os.path.join(workout_files_dir, f) for f in os.listdir(workout_files_dir)),
            key=os.path.getmtime,
            default=None
        )
    
    if csv_file_path is None:
        print("No files found in the downloads folder.")
        return

    # Download TCX file for each workout in the CSV file
    download_workout_files(driver, csv_file_path, workout_files_dir)

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()