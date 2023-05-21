""" wyzant_tutor_survey.py

SUMMARY: Use Selenium to take a survey tutors (the competition).

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.5.4

DATE: May 20, 2023
"""
# Web Browser independent Selenium imports.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# Web Browser dependent Selenium code
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Username and password.
from student_login import USERNAME, PASSWORD

# Other packages.
import csv
from sys import stdout
from time import sleep

# CONSTANTS.

TIMEOUT = 30  # Seconds.
SLEEP_TIME = 0.5  # Seconds.


def main():
    """ Function main.

    Parameters:
    Returns:
    """
    # Read list of topics
    topics = []
    with open('topics.txt', 'r') as file:
        for topic in file:
            topics.append(topic.strip())

    # Selenium options.
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--window-size=1920,2200")

    # Connect to the Selenium web driver.
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Maximize the browser window.
    driver.maximize_window()

    stdout.write("Done initializing Selenium.\n")
    stdout.write("Logging into Wyzant.\n")
    driver.get("https://www.wyzant.com/login")

    WebDriverWait(driver, TIMEOUT).until(EC.title_is("Sign In | Wyzant Tutoring"))
    driver.find_element(By.XPATH, '//*[@id="sso_login-landing"]//input[@id="Username"]').send_keys(USERNAME)
    driver.find_element(By.XPATH, '//*[@id="sso_login-landing"]//input[@id="Password"]').send_keys(PASSWORD)
    driver.find_element(By.XPATH, '//*[@id="sso_login-landing"]/form/button').click()
    WebDriverWait(driver, TIMEOUT).until(EC.title_is("Student Dashboard | Wyzant Tutoring"))

    stdout.write("Done logging into Wyzant.\n")
    stdout.write("Going to the Wyzant find tutors page.\n")

    driver.get("https://www.wyzant.com/match/search")
    sleep(5)
    # this_id = "ctl00_ctl00_PageCPH_CenterColumnCPH_LessonDisplay1_ListViewSession_Pager_NextPageBTN"
    # WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_element_located((By.ID, this_id)))

    stdout.write("At Wyzant find tutors page.\n")

    with open('tutor_survey.csv', 'w', newline='') as output:
        csvwriter = csv.writer(output)

        # Heading row.
        row = ['Topic', 'Tutors']
        print(row)
        csvwriter.writerow(row)

        for topic_orig in topics:
            if " # subject" in topic_orig:
                topic = topic_orig.split(" # subject")[0].strip()
            else:
                topic = topic_orig
            # Enter subject into subject input control.
            subject = driver.find_element(By.XPATH, '//div[2]/section/main/aside[2]/form/div[1]/input')
            sleep(SLEEP_TIME)
            subject.send_keys(Keys.CONTROL, 'a')
            sleep(SLEEP_TIME)
            subject.send_keys(Keys.BACKSPACE)
            sleep(SLEEP_TIME)
            subject.send_keys(topic)
            sleep(SLEEP_TIME)

            # Click Search "button" (an anchor).
            submit = driver.find_element(By.XPATH, '//div[2]/section/main/aside[2]/form/div[3]/button')
            sleep(SLEEP_TIME)
            submit.click()
            sleep(SLEEP_TIME)

            results = driver.find_element(By.XPATH, '//div[2]/div[2]/div[1]/section/div[1]/div/h3/strong').text
            hits = results.split()[0].replace(",", "")
            row = [topic_orig, hits]
            print(row)
            csvwriter.writerow(row)


# End of function main.


if __name__ == '__main__':
    main()
