""" wyzant_tutor_survey_plus.py

SUMMARY: Use Selenium to take a survey of tutors (the competition),
plus a summary of the statistics of their business (how much they charge,
number of students they've tutored, their ratings, et cetera).  Does this for tapics in a text file.
Abandoned in favor of writing to database in wyzant_pricing*.py.


REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.5.7

DATE: May 26, 2023
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
from time import sleep
import statistics
import datetime

# CONSTANTS.

TIMEOUT = 30  # Seconds.
BIG_WAIT = 2  # Seconds.
SMALL_WAIT = 0.2  # Seconds.

# Get today's date.
current_date = datetime.date.today()


def get_mean_sigma(input_list):
    if len(input_list) >= 2:
        return statistics.mean(input_list), statistics.stdev(input_list)
    elif len(input_list) == 1:
        return input_list[0], "None"
    else:
        return "None", "None"


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

    print("Done initializing Selenium, logging into Wyzant.")
    driver.get("https://www.wyzant.com/login")

    WebDriverWait(driver, TIMEOUT).until(ec.title_is("Sign In | Wyzant Tutoring"))
    driver.find_element(By.XPATH, '//*[@id="sso_login-landing"]//input[@id="Username"]').send_keys(USERNAME)
    driver.find_element(By.XPATH, '//*[@id="sso_login-landing"]//input[@id="Password"]').send_keys(PASSWORD)
    driver.find_element(By.XPATH, '//*[@id="sso_login-landing"]/form/button').click()
    WebDriverWait(driver, TIMEOUT).until(ec.title_is("Student Dashboard | Wyzant Tutoring"))

    print("Done logging into Wyzant.")

    with open('./output/tutor_survey_plus.csv', 'w', newline='') as output:
        csvwriter = csv.writer(output)

        # Heading row.
        row = ['Topic', 'Subject', 'Num_Tutors', 'Num_Tutor_Cards', 'Rate_Mean', 'Rate_Sigma',
               'Rating_Mean', 'Rating_Sigma', 'Num_Ratings_Mean', 'Num_Ratings_Sigma', 'Years_Mean', 'Years_Sigma',
               'Topic_Hours_Mean', 'Topic_Hours_Sigma', 'Topic_Hrs_Per_Yr_Mean', 'Topic_Hrs_Per_Yr_Sigma',
               'Correl_Topic', 'Slope_Topic', 'Intercept_Topic',
               'Total_Hours_Mean', 'Total_Hours_Sigma', 'Total_Hrs_Per_Yr_Mean', 'Total_Hrs_Per_Yr_Sigma',
               'Correl_Total', 'Slope_Total', 'Intercept_Total']

        print(row)
        csvwriter.writerow(row)

        for topic_orig in topics:

            # Get next topic
            if " # subject" in topic_orig:
                topic, subject = topic_orig.split(" # ")
            else:
                topic, subject = topic_orig, ""

            driver.get("https://www.wyzant.com/match/search")
            sleep(BIG_WAIT)
            # this_id = "ctl00_ctl00_PageCPH_CenterColumnCPH_LessonDisplay1_ListViewSession_Pager_NextPageBTN"
            # WebDriverWait(driver, TIMEOUT).until(ec.visibility_of_element_located((By.ID, this_id)))

            # Check the background check checkbox.
            background_check = driver.find_element(By.XPATH, '/html/body/div[2]/section/main/aside[1]/form/input[6]')
            # sleep(SMALL_WAIT)
            if not background_check.is_selected():
                background_check.click()
                sleep(BIG_WAIT)

            # Enter topic into subject input control.
            search_term = driver.find_element(By.XPATH, '/html/body/div[2]/section/main/aside[2]/form/div[1]/input')
            # sleep(SMALL_WAIT)
            search_term.send_keys(Keys.CONTROL, 'a')
            sleep(SMALL_WAIT)
            search_term.send_keys(Keys.BACKSPACE)
            sleep(SMALL_WAIT)
            search_term.send_keys(topic)
            sleep(SMALL_WAIT)

            # Click Search "button" (an anchor).
            submit = driver.find_element(By.XPATH, '/html/body/div[2]/section/main/aside[2]/form/div[3]/button')
            # sleep(SMALL_WAIT)
            submit.click()
            sleep(BIG_WAIT)

            # Get number of tutors.
            num_tutors = driver.find_elements(By.XPATH, '/html/body/div[2]/div[2]/div[1]/section/div[1]/div/h3/strong')
            if len(num_tutors) == 0:
                row = [topic, subject, 0, 0, "None", "None", "None", "None",
                       "None", "None", "None", "None", "None",
                       "None", "None", "None", "None", "None"]

            else:
                num_tutors = num_tutors[0].text.split()[0].replace(",", "")
                num_tutors = int(num_tutors)

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
                tutor_url_list = []

                tutor_cards = driver.find_elements(By.XPATH, '//a[contains(@class, "tutor-card")]')
                num_tutor_cards = len(tutor_cards)

                for tutor_number, tutor in enumerate(tutor_cards):
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
                    tutor_url = tutor.get_attribute('href')
                    tutor_url_list.append(tutor_url)

                # END OF "for tutor in tutor_cards"
                # Go to each tutor's web page.
                years_list = []
                for tutor_number, tutor_url in enumerate(tutor_url_list):
                    print(tutor_url)
                    driver.get(tutor_url)
                    sleep(BIG_WAIT)
                    check_date = driver.find_element(By.XPATH, '//a[contains(text(), "Background check passed")]')
                    check_date = check_date.find_element(By.XPATH, '..').text
                    check_date = check_date.strip().split()[-1]
                    month, day, year = check_date.split('/')
                    check_date = datetime.date(int(year), int(month), int(day))
                    age = current_date - check_date
                    years = age.days/365.2425
                    years_list.append(years)

                rate_mean, rate_sigma = get_mean_sigma(rate_list)

                rating_mean, rating_sigma = get_mean_sigma(rating_list)

                num_ratings_mean, num_ratings_sigma = get_mean_sigma(num_ratings_list)

                total_hours_mean, total_hours_sigma = get_mean_sigma(total_hours_list)

                topic_hours_mean, topic_hours_sigma = get_mean_sigma(topic_hours_list)

                years_mean, years_sigma = get_mean_sigma(years_list)

                if total_hours_list and years_list:
                    total_hrs_per_yr_list = [h/y for h, y in zip(total_hours_list, years_list)]
                else:
                    total_hrs_per_yr_list = []

                total_hrs_per_yr_mean, total_hrs_per_yr_sigma = get_mean_sigma(total_hrs_per_yr_list)

                if topic_hours_list and years_list:
                    topic_hrs_per_yr_list = [h/y for h, y in zip(topic_hours_list, years_list)]
                else:
                    topic_hrs_per_yr_list = []

                topic_hrs_per_yr_mean, topic_hrs_per_yr_sigma = get_mean_sigma(topic_hrs_per_yr_list)

                if len(total_hrs_per_yr_list) >= 2 and len(total_rate_list) >= 2:
                    correl_total = statistics.correlation(total_hrs_per_yr_list, total_rate_list)
                    slope_total, intercept_total = statistics.linear_regression(total_hrs_per_yr_list, total_rate_list)
                else:
                    correl_total = "None"
                    slope_total = "None"
                    intercept_total = "None"

                if len(topic_hrs_per_yr_list) >= 2 and len(topic_rate_list) >= 2:
                    correl_topic = statistics.correlation(topic_hrs_per_yr_list, topic_rate_list)
                    slope_topic, intercept_topic = statistics.linear_regression(topic_hrs_per_yr_list, topic_rate_list)
                else:
                    correl_topic = "None"
                    slope_topic = "None"
                    intercept_topic = "None"

                row = [topic, subject, num_tutors, num_tutor_cards, rate_mean, rate_sigma,
                       rating_mean, rating_sigma, num_ratings_mean, num_ratings_sigma, years_mean, years_sigma,
                       topic_hours_mean, topic_hours_sigma, topic_hrs_per_yr_mean, topic_hrs_per_yr_sigma,
                       correl_topic, slope_topic, intercept_topic,
                       total_hours_mean, total_hours_sigma, total_hrs_per_yr_mean, total_hrs_per_yr_sigma,
                       correl_total, slope_total, intercept_total]
            print(row)
            csvwriter.writerow(row)


# End of function main.


if __name__ == '__main__':
    main()
