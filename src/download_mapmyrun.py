import os
import time
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# load credentials from .env file
load_dotenv()
USERNAME = os.getenv("MAPMYRUN_USERNAME")
PASSWORD = os.getenv("MAPMYRUN_PASSWORD")

LOGIN_URL = "https://www.mapmyrun.com/auth/login/"
CSV_URL = 'https://www.mapmyfitness.com/workout/export/csv'

def wait_for_download(directory, timeout):
    """
    Wait for a new file to appear in the specified directory.
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

def login(driver):
    """
    log in to MapMyRun with credentials from env file
    """
    username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email-input")))
    password_field = driver.find_element(By.ID, "Password-input")
    username_field.send_keys(USERNAME)
    password_field.send_keys(PASSWORD)

    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()

def main():
    # set up Chrome options to enable automatic file download
    chrome_options = Options()
    downloads_folder = os.path.expanduser("~/Downloads")
    prefs = {'download.default_directory': downloads_folder,
             'download.prompt_for_download': False,
             'download.directory_upgrade': True,
             'safebrowsing.enabled': True}
    chrome_options.add_experimental_option('prefs', prefs)

    driver = webdriver.Chrome(options=chrome_options)

    # log in
    driver.get(LOGIN_URL)
    login(driver)
    WebDriverWait(driver, 10).until(EC.url_contains("dashboard"))

    print("Files in downloads folder before download:")
    print(os.listdir(downloads_folder))

    # navigate to the CSV download page to save workout data csv file
    driver.get(CSV_URL)

    # check if we need to authenticate the user again
    if "login" in driver.current_url:
        print("Logging in again...")
        login(driver)

    # wait for the download to complete
    new_files = wait_for_download(downloads_folder, 120)
    if new_files:
        print(f"New files detected: {new_files}")
    else:
        print("No new files detected.")

    # check for any new files
    all_files = os.listdir(downloads_folder)
    all_files.sort(key=lambda x: os.path.getmtime(os.path.join(downloads_folder, x)), reverse=True)

    if all_files:
        latest_file = all_files[0]
        print(f"Most recent file in downloads folder: {latest_file}")
        print(f"File type: {os.path.splitext(latest_file)[1]}")
    else:
        print("No files found in the downloads folder.")

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()