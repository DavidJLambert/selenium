""" wyzant_pricing.py

SUMMARY: Part 1 of a survey and analysis of tutors (the competition).
Uses Selenium to find all the tutors, the topics they tutor in, and related info.
Simply goes through tapics in a text file, searches for students who tutor in each topic,
scrapes the search results page, and saves that information into a database.

Part 1 wyzant_pricing.py.
Part 2: wyzant_pricing_detail.py
Part 3: wyzant_pricing_gender.py

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
import datetime
import sqlite3
from traceback import print_exception
from sys import stdout, exc_info
from time import sleep
import gender_guesser.detector as gender_guesser

# CONSTANTS.

TIMEOUT = 30  # Seconds.
FAILURE_WAIT = 10 # Seconds.
BIG_WAIT = 2  # Seconds.
SMALL_WAIT = 0.2  # Seconds.
DB_PATH = r'C:\Users\david\Desktop\Wyzant\Pricing\Pricing.sqlite3'
MAX_TRIES = 6

# Instantiate gender guesser
""" Output:
unknown (name not found), saved as Unk
andy (androgynous), saved as And
male, saved as M
female, saved as F
mostly_male, saved as M?
mostly_female, saved as F?
"""
guess = gender_guesser.Detector()
guess_dict = {'unknown': 'Unk',
              'andy': 'And',
              'male': 'M',
              'female': 'F',
              'mostly_male': 'M?',
              'mostly_female': 'F?'}


# Get the current time, in 'YYYY-MM-DD HH:MM:SS' format.
def get_date_time():
    return str(datetime.datetime.now())[:19]


def main():
    """ Function main.

    Parameters:
    Returns:
    """
    # Read list of topics.
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

    # Log into Wyzant website.
    print("Done initializing Selenium, logging into Wyzant.")
    driver.get("https://www.wyzant.com/login")
    WebDriverWait(driver, TIMEOUT).until(ec.title_is("Sign In | Wyzant Tutoring"))
    driver.find_element(By.XPATH, '//*[@id="sso_login-landing"]//input[@id="Username"]').send_keys(USERNAME)
    driver.find_element(By.XPATH, '//*[@id="sso_login-landing"]//input[@id="Password"]').send_keys(PASSWORD)
    driver.find_element(By.XPATH, '//*[@id="sso_login-landing"]/form/button').click()
    WebDriverWait(driver, TIMEOUT).until(ec.title_is("Student Dashboard | Wyzant Tutoring"))
    print("Done logging into Wyzant.")

    # Connect to database.
    connection = sqlite3.connect(database=DB_PATH, timeout=10)
    cursor = connection.cursor()
    print("Connected to SQLite.")

    for topic_orig in topics:
        # Get next topic.
        subject = 0
        if " # subject" in topic_orig:
            topic, subject = topic_orig.split(" # ")
            if subject == "subject":
                subject = 1
        else:
            topic = topic_orig
        print(f"{topic} STARTED.")

        for num_tries in range(1, MAX_TRIES):
            try:
                # Start search.
                driver.get("https://www.wyzant.com/match/search")
                sleep(BIG_WAIT)

                # Make sure that the background check checkbox is unchecked.
                background_check = driver.find_element(By.XPATH,
                                                       '/html/body/div[2]/section/main/aside[1]/form/input[6]')
                if background_check.is_selected():
                    background_check.click()
                    sleep(BIG_WAIT)

                # Enter topic into subject input control.
                search_term = driver.find_element(By.XPATH,
                                                  '/html/body/div[2]/section/main/aside[2]/form/div[1]/input')
                # First, select all text in input...
                search_term.send_keys(Keys.CONTROL, 'a')
                sleep(SMALL_WAIT)
                # ...backspace to delete text in input...
                search_term.send_keys(Keys.BACKSPACE)
                sleep(SMALL_WAIT)
                # ...paste topic into subject input control...
                search_term.send_keys(topic)
                sleep(SMALL_WAIT)
                # ...click Search "button" (an anchor).
                submit = driver.find_element(By.XPATH,
                                             '/html/body/div[2]/section/main/aside[2]/form/div[3]/button')
                submit.click()
                sleep(BIG_WAIT)

                # Get number of tutors.
                num_tutors = driver.find_elements(By.XPATH,
                                                  '/html/body/div[2]/div[2]/div[1]/section/div[1]/div/h3/strong')
                num_tutors = num_tutors[0].text.split()[0].replace(",", "")
                num_tutors = int(num_tutors)
                print(f"{topic} HAS {num_tutors} TUTORS.")

                # Successful topic search, exit for loop
                break
            except Exception:
                print(f"{topic} TOPIC SEARCH RAISED THIS EXCEPTION, TRY #{num_tries}:")
                print_exception(*exc_info(), limit=None, file=stdout)
                sleep(FAILURE_WAIT)

        else:  # for num_tries in range(1, MAX_TRIES):
            print(f"{topic} TOPIC SEARCH FAILED {MAX_TRIES} TIMES, SKIPPING TO NEXT TOPIC.")
            continue

        # Scrape tutors only if there are tutors.
        if num_tutors == 0:
            print(f"{topic} TOPIC SEARCH FOUND ZERO TUTORS.")
            continue

        # Keep clicking "Show More Tutors" link until it disappears.
        print(f"{topic} CLICKING 'Show More Tutors'")
        while True:
            try:
                sleep(0.35)
                show_more = driver.find_elements(By.XPATH,
                                                 '//div[@class="load-more"]/a[contains(@class, "load-more-btn")]')
                if len(show_more) == 0:
                    break
                else:
                    show_more[0].click()
            except Exception:
                pass

        print(f"{topic} FINISHED CLICKING 'Show More Tutors'")

        for num_tries in range(1, MAX_TRIES):
            try:
                # Get list of tutor-card anchors (each contains 1 tutor).  They fall under 2 different xpaths.
                xpath1 = '/html/body/div[2]/div[2]/div[1]/section/a[contains(@class, "tutor-card")]'
                xpath2 = '/html/body/div[2]/div[2]/div[1]/a[contains(@class, "tutor-card")]'
                tutor_cards = (driver.find_elements(By.XPATH, xpath1) +
                               driver.find_elements(By.XPATH, xpath2))
                # Number of tutor-cards should match num_tutors.  Not checking.
                num_tutor_cards = len(tutor_cards)

                # Successful tutor-card search, exit for loop
                break
            except Exception:
                print(f"{topic} TUTOR-CARD SEARCH RAISED THIS EXCEPTION, TRY #{num_tries}:")
                print_exception(*exc_info(), limit=None, file=stdout)
                sleep(FAILURE_WAIT)
        else:  # for num_tries in range(1, MAX_TRIES):
            print(f"{topic} GETTING LIST OF TUTOR-CARDS FAILED {MAX_TRIES} TIMES, SKIPPING TO NEXT TOPIC.")
            continue

        print(f"{topic} STARTED SCRAPING TUTOR CARDS")
        for tutor in tutor_cards:
            # Get tutor profile URL
            tutor_url = tutor.get_attribute('href').split('?')[0]

            # Get tutor ID number
            id_number = tutor_url.split("?")[0].split("/")[-1]
            id_number = int(id_number)

            for num_tries in range(1, MAX_TRIES):
                try:
                    # Get Tutor Name and Gender
                    tutor_name = tutor.find_elements(By.XPATH, './div/section[2]/div/h5')
                    if tutor_name:
                        tutor_name = tutor_name[0].text.strip()
                        gender = tutor_name.split()[:-1]
                        gender = " ".join(gender)
                        gender = guess_dict[guess.get_gender(gender)]
                    else:
                        tutor_name = None
                        gender = "Unk"

                    # Billing rate, $ per hour.
                    bill_rate = tutor.find_elements(By.XPATH, './div/section[3]/section/h5/div')
                    if bill_rate:
                        bill_rate = int(bill_rate[0].text.strip()[1:-5].replace(",", ""))
                    else:
                        bill_rate = None

                    # Average Rating, 0-5.
                    avg_rating = tutor.find_elements(By.XPATH, './div/section[3]/div[1]/strong')
                    if avg_rating:
                        avg_rating = float(avg_rating[0].text.strip())
                    else:
                        avg_rating = None

                    # Number of Ratings.
                    num_ratings = tutor.find_elements(By.XPATH, './div/section[3]/div[1]/span[2]')
                    if num_ratings:
                        num_ratings = int(num_ratings[0].text.strip().replace(",", "")[1:-1])
                    else:
                        num_ratings = 0

                    # Topic hours and Total hours
                    '''
                    FORMAT 1:
                    TOPIC HOURS: "40 hours tutoring Fortran" at
                        /html/body/div[2]/div[2]/div[1]/section/a[3]/div/section[3]/div[2]/div/p/span[1]
                    TOTAL HOURS: "out of 1,369 hours" at
                        /html/body/div[2]/div[2]/div[1]/section/a[3]/div/section[3]/div[2]/div/p/span[2]

                    FORMAT 2:
                    TOPIC HOURS: 'None'
                    TOTAL HOURS: "78 hours tutoring" at
                        /html/body/div[2]/div[2]/div[1]/section/a[2]/div/section[3]/div[2]/h3
                    '''
                    topic_hours = tutor.find_elements(By.XPATH, './div/section[3]/div[2]/div/p/span[1]')
                    if topic_hours:
                        # FORMAT 1
                        topic_hours = int(topic_hours[0].text.split()[0].replace(",", ""))

                        total_hours = tutor.find_element(By.XPATH, './div/section[3]/div[2]/div/p/span[2]')
                        total_hours = int(total_hours.text.split()[2].replace(",", ""))
                    else:
                        # FORMAT 2
                        # No topic hours reported, so don't record topic hours.  Do get total hours.
                        topic_hours = 0
                        total_hours = tutor.find_elements(By.XPATH, './div/section[3]/div[2]/h3')
                        if total_hours:
                            total_hours = int(total_hours[0].text.split()[0].replace(",", ""))
                        else:
                            total_hours = 0

                    photo = tutor.find_elements(By.XPATH, './div/section[1]/div/img')
                    if photo:
                        photo = photo[0].get_attribute('src')
                        has_photo = int(photo != 'https://www.wyzant.com/images/tutor/silhouette.png')
                    else:
                        has_photo = int(False)

                    # Successful scrape of tutor, exit for loop
                    break
                except Exception:
                    print(f"{topic} GET INTO FOR TUTOR {id_number} RAISED THIS EXCEPTION, TRY #{num_tries}:")
                    print_exception(*exc_info(), limit=None, file=stdout)
                    sleep(FAILURE_WAIT)

            else:  # for num_tries in range(1, MAX_TRIES):
                print(f"{topic} GET INTO FOR TUTOR {id_number} FAILED #{num_tries} TIMES, SKIPPING.")
                continue

            # Insert into or update Tutors table.
            sql = "SELECT COUNT(*) FROM Tutors WHERE ID = ?"
            cursor.execute(sql, [id_number])
            count = cursor.fetchone()[0]

            if count == 0:
                sql = ("INSERT INTO Tutors (URL, Name, Bill_Rate, Avg_Rating, Number_Ratings, Total_Hours, "
                       "Has_Photo, Gender, Last_Update, ID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
            else:
                sql = ("UPDATE Tutors SET URL = ?, Name = ?, Bill_Rate = ?, Avg_Rating = ?,"
                       "Number_Ratings = ?, Total_Hours = ?, Has_Photo = ?, Gender = ?, Last_Update = ? "
                       "WHERE ID = ?")
            cursor.execute(sql, [tutor_url, tutor_name, bill_rate, avg_rating, num_ratings, total_hours,
                                 has_photo, gender, get_date_time(), id_number])

            # Insert into or update Topics table.
            sql = "SELECT COUNT(*) FROM Topics WHERE ID = ? AND Topic = ?"
            cursor.execute(sql, [id_number, topic])
            count = cursor.fetchone()[0]

            if count == 0:
                sql = "INSERT INTO Topics (Subject, Topic_Hours, Last_Update, ID, Topic) VALUES (?, ?, ?, ?, ?)"
            else:
                sql = ("UPDATE Topics SET Subject = ?, Topic_Hours = ?, Last_Update = ? WHERE ID = ? AND "
                       "Topic = ?")
            cursor.execute(sql, [subject, topic_hours, get_date_time(), id_number, topic])
            connection.commit()

        else:  # for tutor in tutor_cards:
            pass

        print(f"{topic} FINISHED SCRAPING TUTOR CARDS")
        print(f"{topic} TOPIC FINISHED")

    else:  # for topic_orig in topics:
        pass

    # Final commit, disconnect from database.
    connection.commit()
    cursor.close()
    connection.close()
    print("ALL DONE.")
# End of function main.


if __name__ == '__main__':
    main()
