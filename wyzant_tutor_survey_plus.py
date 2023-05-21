""" wyzant_tutor_survey.py

SUMMARY: Use Selenium to take a survey of tutors (the competition),
plus a summary of the statistics of their business (how much they charge,
number of students they've tutored, their ratings, et cetera).

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.5.5

DATE: May 21, 2023
"""
# Web Browser independent Selenium imports.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException

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
import statistics

# CONSTANTS.

TIMEOUT = 30  # Seconds.
SLEEP_TIME = 0.2  # Seconds.


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

    with open('tutor_survey_plus.csv', 'w', newline='') as output:
        csvwriter = csv.writer(output)

        # Heading row.
        row = ['Topic', 'Tutors', 'Rate_Mean', 'Rating_Mean', 'Students_Mean', 'Num_Hours_Mean', 'Correl', 'Slope',
               'Intercept', 'Entries']

        print(row)
        csvwriter.writerow(row)

        for topic_orig in topics:
            if " # subject" in topic_orig:
                topic = topic_orig.split(" # subject")[0].strip()
            else:
                topic = topic_orig
            # Enter subject into subject input control.
            subject = driver.find_element(By.XPATH, '/html/body/div[2]/section/main/aside[2]/form/div[1]/input')
            sleep(SLEEP_TIME)
            subject.send_keys(Keys.CONTROL, 'a')
            sleep(SLEEP_TIME)
            subject.send_keys(Keys.BACKSPACE)
            sleep(SLEEP_TIME)
            subject.send_keys(topic)
            sleep(SLEEP_TIME)

            # Click Search "button" (an anchor).
            submit = driver.find_element(By.XPATH, '/html/body/div[2]/section/main/aside[2]/form/div[3]/button')
            sleep(SLEEP_TIME)
            submit.click()
            sleep(SLEEP_TIME)

            # Get number of tutors.
            number_tutors = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[1]/section/div[1]/div/h3/strong').text
            number_tutors = number_tutors.split()[0].replace(",", "")

            # Keep clicking "Show More Tutors" link until it disappears.
            while True:
                try:
                    sleep(0.35)
                    show_more = driver.find_elements(By.XPATH, '//a[contains(@class, "load-more-btn")]')
                except Exception:
                    pass

                try:
                    show_more[0].click()
                except Exception:
                    pass

                if not show_more:
                    break

            # Get tutor statistics.
            rate_list = []
            rating_list = []
            num_students_list = []
            num_hours_list = []
            entries = 0

            tutor_cards = driver.find_elements(By.XPATH, '//a[contains(@class, "tutor-card")]')
            print("TUTOR CARDS", len(tutor_cards))
            for tutor in tutor_cards:
                rate = tutor.find_elements(By.XPATH, './div/section[3]/section/h5/div')
                if not rate:
                    rate_list.append(0)
                else:
                    rate = float(rate[0].text.strip()[1:-5].replace(",", ""))
                    rate_list.append(rate)

                rating = tutor.find_elements(By.XPATH, './div/section[3]/div[1]/strong')
                if not rating:
                    pass
                    # rating_list.append(0), no sensible rating possible, just omit.
                else:
                    rating = float(rating[0].text.strip())
                    rating_list.append(rating)

                num_students = tutor.find_elements(By.XPATH, './div/section[3]/div[1]/span[2]')
                if not num_students:
                    num_students_list.append(0)
                else:
                    num_students = float(num_students[0].text.strip().replace(",", "")[1:-1])
                    num_students_list.append(num_students)

                num_hours = tutor.find_elements(By.XPATH, './div/section[3]/div[2]/h3')
                if not num_hours:
                    num_hours_list.append(0)
                else:
                    num_hours = float(num_hours[0].text.split()[0].replace(",", ""))
                    num_hours_list.append(num_hours)

                entries += 1

            # print(rate_list)
            # print(rating_list)
            # print(num_students_list)
            # print(num_hours_list)

            rate_mean = statistics.mean(rate_list)
            rating_mean = statistics.mean(rating_list)
            num_students_mean = statistics.mean(num_students_list)
            num_hours_mean = statistics.mean(num_hours_list)

            # rate_median = statistics.median(rate_list)
            # rating_median = statistics.median(rating_list)
            # num_students_median = statistics.median(num_students_list)
            # num_hours_median = statistics.median(num_hours_list)

            correl = statistics.correlation(num_hours_list, rate_list)
            slope, intercept = statistics.linear_regression(num_hours_list, rate_list)

            row = [topic_orig, number_tutors, rate_mean, rating_mean, num_students_mean, num_hours_mean, correl, slope,
                   intercept, entries]

            print(row)
            csvwriter.writerow(row)


# End of function main.


if __name__ == '__main__':
    main()
