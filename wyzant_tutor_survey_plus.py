""" wyzant_tutor_survey.py

SUMMARY: Use Selenium to take a survey of tutors (the competition),
plus a summary of the statistics of their business (how much they charge,
number of students they've tutored, their ratings, et cetera).  Does this for tapics in a text file.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.5.6

DATE: May 25, 2023
"""
# Web Browser independent Selenium imports.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

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
    with open('tutor_topics.txt', 'r') as file:
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

    WebDriverWait(driver, TIMEOUT).until(ec.title_is("Sign In | Wyzant Tutoring"))
    driver.find_element(By.XPATH, '//*[@id="sso_login-landing"]//input[@id="Username"]').send_keys(USERNAME)
    driver.find_element(By.XPATH, '//*[@id="sso_login-landing"]//input[@id="Password"]').send_keys(PASSWORD)
    driver.find_element(By.XPATH, '//*[@id="sso_login-landing"]/form/button').click()
    WebDriverWait(driver, TIMEOUT).until(ec.title_is("Student Dashboard | Wyzant Tutoring"))

    stdout.write("Done logging into Wyzant.\n")
    stdout.write("Going to the Wyzant find tutors page.\n")

    driver.get("https://www.wyzant.com/match/search")
    sleep(5)
    # this_id = "ctl00_ctl00_PageCPH_CenterColumnCPH_LessonDisplay1_ListViewSession_Pager_NextPageBTN"
    # WebDriverWait(driver, TIMEOUT).until(ec.visibility_of_element_located((By.ID, this_id)))

    stdout.write("At Wyzant find tutors page.\n")

    with open('tutor_survey_plus.csv', 'w', newline='') as output:
        csvwriter = csv.writer(output)

        # Heading row.
        row = ['Topic', 'Subject', 'Tutors', 'Num_Tutor_Cards', 'Rate_Mean', 'Rating_Mean', 'Num_Ratings_Mean', 'Topic_Hours_Mean',
               'Total_Hours_Mean', 'Correl_Topic', 'Slope_Topic', 'Intercept_Topic', 'Correl_Total', 'Slope_Total',
               'Intercept_Total']

        print(row)
        csvwriter.writerow(row)

        for topic_orig in topics:
            if " # subject" in topic_orig:
                topic, subject = topic_orig.split(" # ")
            else:
                topic, subject = topic_orig, ""
            # Enter search into subject input control.
            search = driver.find_element(By.XPATH, '/html/body/div[2]/section/main/aside[2]/form/div[1]/input')
            sleep(SLEEP_TIME)
            search.send_keys(Keys.CONTROL, 'a')
            sleep(SLEEP_TIME)
            search.send_keys(Keys.BACKSPACE)
            sleep(SLEEP_TIME)
            search.send_keys(topic)
            sleep(SLEEP_TIME)

            # Click Search "button" (an anchor).
            submit = driver.find_element(By.XPATH, '/html/body/div[2]/section/main/aside[2]/form/div[3]/button')
            sleep(SLEEP_TIME)
            submit.click()
            sleep(SLEEP_TIME)

            # Get number of tutors.
            num_tutors = driver.find_elements(By.XPATH, '/html/body/div[2]/div[2]/div[1]/section/div[1]/div/h3/strong')
            if len(num_tutors) == 0:
                row = [topic, subject, 0, 0, "None", "None", "None",
                       "None", "None", "None", "None", "None", "None", "None", "None"]
            else:
                num_tutors = num_tutors[0].text.split()[0].replace(",", "")

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
                topic_rate_list = []
                total_rate_list = []
                rating_list = []
                num_ratings_list = []
                topic_hours_list = []
                total_hours_list = []

                tutor_cards = driver.find_elements(By.XPATH, '//a[contains(@class, "tutor-card")]')
                num_tutor_cards = len(tutor_cards)
                print("TUTOR CARDS", num_tutor_cards)
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

                    num_ratings = tutor.find_elements(By.XPATH, './div/section[3]/div[1]/span[2]')
                    if not num_ratings:
                        num_ratings_list.append(0)
                    else:
                        num_ratings = float(num_ratings[0].text.strip().replace(",", "")[1:-1])
                        num_ratings_list.append(num_ratings)

                    '''
                    FORMAT 1:
                    TOPIC HOURS: "40 hours tutoring Fortran" at
                        /html/body/div[2]/div[2]/div[1]/section/a[3]/div/section[3]/div[2]/div/p/span[1]
                    TOTAL HOURS: "out of 1,369 hours" at
                        /html/body/div[2]/div[2]/div[1]/section/a[3]/div/section[3]/div[2]/div/p/span[2]

                    FORMAT 2:
                    TOPIC HOURS: None
                    TOTAL HOURS: "78 hours tutoring" at
                        /html/body/div[2]/div[2]/div[1]/section/a[2]/div/section[3]/div[2]/h3
                    '''
                    topic_hours = tutor.find_elements(By.XPATH, './div/section[3]/div[2]/div/p/span[1]')
                    if topic_hours:
                        # FORMAT 1
                        topic_hours = float(topic_hours[0].text.split()[0].replace(",", ""))
                        topic_hours_list.append(topic_hours)
                        topic_rate_list.append(rate)

                        total_hours = tutor.find_element(By.XPATH, './div/section[3]/div[2]/div/p/span[2]')
                        total_hours = float(total_hours.text.split()[2].replace(",", ""))
                        total_hours_list.append(total_hours)
                        total_rate_list.append(rate)
                    else:
                        # FORMAT 2
                        # No topic hours reported, so don't record topic hours.  Do get total hours.
                        total_hours = tutor.find_elements(By.XPATH, './div/section[3]/div[2]/h3')
                        if total_hours:
                            total_hours = float(total_hours[0].text.split()[0].replace(",", ""))
                            total_hours_list.append(total_hours)
                            total_rate_list.append(rate)
                        else:
                            # No total hours reported, so don't record anything.
                            pass

                if rate_list:
                    rate_mean = statistics.mean(rate_list)
                else:
                    rate_mean = "None"
                if rating_list:
                    rating_mean = statistics.mean(rating_list)
                else:
                    rating_mean = "None"
                if num_ratings_list:
                    num_ratings_mean = statistics.mean(num_ratings_list)
                else:
                    num_ratings_mean = "None"
                if total_hours_list:
                    total_hours_mean = statistics.mean(total_hours_list)
                else:
                    total_hours_mean = "None"

                if total_hours_list and total_rate_list:
                    correl_total = statistics.correlation(total_hours_list, total_rate_list)
                    slope_total, intercept_total = statistics.linear_regression(total_hours_list, total_rate_list)

                if topic_hours_list:
                    topic_hours_mean = statistics.mean(topic_hours_list)

                    correl_topic = statistics.correlation(topic_hours_list, topic_rate_list)
                    slope_topic, intercept_topic = statistics.linear_regression(topic_hours_list, topic_rate_list)
                else:
                    topic_hours_mean = "None"
                    correl_topic = "None"
                    slope_topic = "None"
                    intercept_topic = "None"

                row = [topic, subject, num_tutors, num_tutor_cards, rate_mean, rating_mean, num_ratings_mean,
                       topic_hours_mean, total_hours_mean, correl_topic, slope_topic, intercept_topic, correl_total,
                       slope_total, intercept_total]

            print(row)
            csvwriter.writerow(row)


# End of function main.


if __name__ == '__main__':
    main()
