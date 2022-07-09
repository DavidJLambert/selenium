""" wyzant_testimonials.py

SUMMARY: Use Selenium to get all the testimonials.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.5.0

DATE: July 8, 2022
"""
# Web Browser independent Selenium imports.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Web Browser dependent Selenium code
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import csv
from sys import stdout
from time import sleep

# CONSTANTS.

TIMEOUT = 30  # Seconds.
SLEEP_TIME = 2  # Seconds.

# Wyzant.com login information.
USERNAME = "david.lambert.3"
PASSWORD = "40tN7@hu^q4^8R1cw8l#"

# How to wait for refresh
UI_PAGE_LINK = "ui-page-link"


topics = {'python': 'Python',
          'sql': 'SQL',
          'calculus': 'Calculus',
          'web scraping': 'Web Scraping',
          'vba': 'VBA',
          'precalc': 'Pre-Calculus',
          'linux': 'Linux', 'ubuntu': 'Linux', 'unix': 'Linux', 'bash': 'Linux',
          'code': 'Coding', 'coding': 'Coding', 'programming': 'Coding', 'loop': 'Coding'}
exact_topics = {'GRE'}


def main():
    """ Function main.  Get all recommendations.

    Parameters:
    Returns:
    """
    # Selenium options.
    options = Options()
    options.headless = True
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
    WebDriverWait(driver, TIMEOUT).until(EC.title_is("My Profile | Wyzant Tutoring"))

    stdout.write("Done logging into Wyzant.\n")
    stdout.write("Going to the Wyzant job listings page.\n")

    driver.get("https://www.wyzant.com/tutor/jobs")
    WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_element_located((By.CLASS_NAME, UI_PAGE_LINK)))

    stdout.write("At Wyzant job listings page.\n")

    # Go inside first job listing page.
    control = driver.find_elements(By.XPATH, '//a[@class="job-details-link"]')[0]
    control.click()
    sleep(SLEEP_TIME)

    stdout.write("In first Wyzant job listing page.\n")

    with open('recommendations.csv', 'w', newline='') as output:
        csvwriter = csv.writer(output)

        # Heading row.
        row = ['Name', 'Sessions', 'Topics', 'Title', 'Body']
        print(row)
        csvwriter.writerow(row)

        # Loop over recommendations.
        keep_going = True
        while keep_going:
            previous_row = row
            row = []

            # Student name.
            testimonial_student = driver.find_element(By.XPATH, '//span[@id="testimonial_student_name"]').text
            row.append(testimonial_student)

            # Number of sessions with student.
            testimonial_sessions = driver.find_element(By.XPATH, '//span[@id="testimonial_sessions"]').text
            row.append(testimonial_sessions.split()[0])

            testimonial_title = driver.find_element(By.XPATH, '//h5[@id="testimonial_title"]').text

            testimonial_body = driver.find_element(By.XPATH, '//p[@id="testimonial_body"]').text

            # xpath of button to move to next recommendation.
            xpath2 = '//span[@id="testimonial_sessions"]'
            driver.find_element(By.XPATH, '//div[@id="testimonial_nav"]/a[text()="›"]').click()
            sleep(SLEEP_TIME)

            used_topics = set()
            # Search for topics, part 1.
            search_me = testimonial_title + ' ' + testimonial_body
            for topic in exact_topics:
                if topic in search_me:
                    used_topics.add(topic)
            # Search for topics, part 2.
            search_me = search_me.lower()
            for topic, TOPIC in topics.items():
                if topic in search_me:
                    used_topics.add(TOPIC)
            # Append topics to end of row.
            used_topics = ', '.join(used_topics)

            # Topics covered in the session.
            row.append(used_topics)

            # Testimonial title.
            row.append(testimonial_title)

            # Body of testimonial.
            row.append(testimonial_body)

            if previous_row == row and testimonial_student not in {'Hunter', 'Nathan'}:
                # Repetitions means end of recommendations.
                keep_going = False
            else:
                # Write row to file and print.
                print(row)
                csvwriter.writerow(row)

# End of function main.


if __name__ == '__main__':
    main()