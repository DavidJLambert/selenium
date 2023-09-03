""" wyzant_pricing_detail.py

SUMMARY: Part 2 of a survey and analysis of tutors (the competition).
Fetches information about each tutor, goes to the tutor's profile page on wyzant.com,
scrapes the information in that page, and saves that information into a database.

Part 1: wyzant_pricing.py.
Part 2: wyzant_pricing_detail.py
Part 3: pricing_gender.py

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.6.0

DATE: Sep 02, 2023
"""
# Web Browser independent Selenium imports.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

# Web Browser dependent Selenium code
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from wyzant_login import log_into_wyzant

# Other packages.
import datetime
import sqlite3
from traceback import print_exception
from sys import exc_info

# CONSTANTS.

TIMEOUT = 30  # Seconds.
FAILURE_WAIT = 10 # Seconds.
BIG_WAIT = 2  # Seconds.
SMALL_WAIT = 0.2  # Seconds.
DB_PATH = r'C:\Users\david\Desktop\Wyzant\Pricing\Pricing.sqlite3'
MAX_TRIES = 6


# Get the current time, in 'YYYY-MM-DD HH:MM:SS' format.
def get_date_time() -> str:
    return str(datetime.datetime.now())[:19]


def main():
    """ Function main.

    Parameters:
    Returns:
    """
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
    print("Done initializing Selenium")

    # Log into wyzant.
    driver = log_into_wyzant(driver)

    # Connect to database.
    connection = sqlite3.connect(database=DB_PATH, timeout=10)
    cursor = connection.cursor()
    print("Connected to SQLite.")

    # Find tutors who need details from their profile added.
    sql = ("SELECT ID, URL "
           "FROM Tutors "
           "WHERE City IS NULL "
           "OR State IS NULL "
           "OR Response_Time_Min IS NULL "
           "OR Highest_Degree IS NULL "
           "OR Background_Check IS NULL")
    cursor.execute(sql)
    rows = cursor.fetchall()

    print(f"Found {len(rows)} records to update.")

    for row_number, row in enumerate(rows):
        if row_number % 50 == 0:
            print(f"Updated {row_number} records.")

        try:
            id_number, tutor_url = row

            # Go to URL.
            driver.get(tutor_url)
            xpath = '/html/body/footer/div[1]/div[2]/div/div[1]/ul/li[1]/a'
            WebDriverWait(driver, TIMEOUT, poll_frequency=0.2).until(ec.element_to_be_clickable((By.XPATH, xpath)))

            # City and state.  Format: "Other Palm Beach Gardens, FL Tutors"
            location = driver.find_elements(By.XPATH, '/html/body/div[2]/section/div[1]/div[3]/aside/h2')
            if location:
                location = location[0].text[6:-7]
                city, state = location.split(", ")
            else:
                city, state = None, None

            # Response time.  Format: "Response time: 2 hours"
            xpath = '/html/body/div[2]/section/div[1]/div[1]/section/div[6]/div'
            response_time = driver.find_elements(By.XPATH, xpath)
            if response_time:
                response_time = response_time[0].text.strip().split()
                if len(response_time) > 2:
                    response_time, units = response_time[2:]
                    response_time = int(response_time)
                    if units[:4] == "hour":
                        response_time *= 60
                    elif units[:6] == "minute":
                        pass
                    else:
                        response_time = None
                else:
                    response_time = None
            else:
                response_time = None

            # Highest degree.  Format: "University of Rochester\nMathematics\n\nUniversity of Rochester\nMasters".
            highest_degree = 'None'
            xpath = '/html/body/div/section/div/div/div/h3[contains(text(), "Education")]/../div/section'
            degrees = driver.find_elements(By.XPATH, xpath)
            if len(degrees) > 0:
                for degree in degrees:
                    degree = degree.text.split("\n")
                    if len(degree) >= 2:
                        degree = degree[1]
                        if highest_degree in ['MS', 'BS', 'None'] and degree == 'PhD':
                            highest_degree = 'PhD'
                        elif highest_degree in ['BS', 'None'] and degree in ['Masters', 'MBA']:
                            highest_degree = 'MS'
                        elif highest_degree == 'None':
                            highest_degree = 'BS'

            # Background check date.  Format: "Background check passed on 1/26/2016"
            xpath = '/html/body/div/section/div/div/div/div/ul/li/p/a[contains(text(), "Background check passed")]/..'
            check_date = driver.find_elements(By.XPATH, xpath)
            if check_date:
                check_date = check_date[0].text.strip().split()[-1]
                month, day, year = check_date.split('/')
                check_date = datetime.date(int(year), int(month), int(day))
            else:
                check_date = None

            # Update the Tutors table.
            sql = ("UPDATE Tutors SET City = ?, State = ?, Response_Time_Min = ?, Highest_Degree = ?, "
                   "Background_Check = ?, Last_Update = ? WHERE ID = ?")
            cursor.execute(sql, [city, state, response_time, highest_degree, check_date, get_date_time(), id_number])

            if row_number % 10 == 0:
                connection.commit()

        except KeyboardInterrupt:
            connection.commit()
            cursor.close()
            connection.close()
            print("Execution halted.")
            exit(0)

        except Exception:
            # print stack trace, but continue on to next record.
            print(f"Exception caught scraping {tutor_url}:")
            print_exception(*exc_info(), limit=None)

    else:
        pass

    # Final commit, disconnect from database.
    connection.commit()
    cursor.close()
    connection.close()
    print("ALL DONE.")
# End of function main.


if __name__ == '__main__':
    main()


'''
# Go to each tutor's web page.
for tutor_detail in tutor_detail_list:
    tutor_url, topic, subject = tutor_detail

    # Tutor ID number
    id_number = tutor_url.split("?")[0].split("/")[-1]
    id_number = int(id_number)

    # Go to URL.
    driver.get(tutor_url)
    xpath = '/html/body/footer/div[1]/div[2]/div/div[1]/ul/li[1]/a'
    WebDriverWait(driver, TIMEOUT, poll_frequency=0.2).until(ec.element_to_be_clickable((By.XPATH,
                                                                                         xpath)))

    # Response time.
    xpath = '/html/body/div[2]/section/div[1]/div[1]/section/div[6]/div'
    response_time = driver.find_elements(By.XPATH, xpath)
    if response_time:
        response_time, units = response_time[0].text.strip().split()[2:]
        response_time = int(response_time)
        if units[:4] == "hour":
            response_time *= 60
        elif units[:6] == "minute":
            pass
        else:
            response_time = None
    else:
        response_time = None

    # Background check date.
    xpath = ('/html/body/div/section/div/div/div/div/ul/li/p/a[contains(text(), '
             '"Background check passed")]/..')
    check_date = driver.find_elements(By.XPATH, xpath)
    if check_date:
        check_date = check_date[0].text.strip().split()[-1]
        month, day, year = check_date.split('/')
        check_date = datetime.date(int(year), int(month), int(day))
    else:
        check_date = None

    # Highest degree.
    highest_degree = 'None'
    xpath = '/html/body/div/section/div/div/div/h3[contains(text(), "Education")]/../div/section'
    degrees = driver.find_elements(By.XPATH, xpath)
    if len(degrees) > 0:
        for degree in degrees:
            degree = degree.text.split("\n")
            if len(degree) >= 2:
                degree = degree[1]
                if highest_degree in ['MS', 'BS', 'None'] and degree == 'PhD':
                    highest_degree = 'PhD'
                elif highest_degree in ['BS', 'None'] and degree in ['Masters', 'MBA']:
                    highest_degree = 'MS'
                elif highest_degree == 'None':
                    highest_degree = 'BS'

    # Examples of Expertise.
    examples = driver.find_elements(By.XPATH,
                                    '/html/body/div[2]/section/div[1]/div[3]/div[6]/div[3]/div[1]/a')
    examples = len(examples)

    # City and state.
    location = driver.find_elements(By.XPATH, '/html/body/div[2]/section/div[1]/div[3]/aside/h2')
    if location:
        location = location[0].text[6:-7]
        city, state = location.split(", ")
    else:
        city, state = None, None

    # Insert into or Update Tutors.
    sql = f"SELECT COUNT(*) FROM Tutors WHERE ID = ?"
    cursor.execute(sql, [id_number])
    count = cursor.fetchone()[0]

    if count == 0:
        print("WTF 1")
    else:
        sql = ("UPDATE Tutors SET City = ?, State = ?, Response_Time_Min = ?, Highest_Degree = ?, "
               "Last_Update = ? WHERE ID = ?")
    cursor.execute(sql, [city, state, response_time, highest_degree, get_date_time(), id_number])

    # Insert into or Update Topics.
    sql = f"SELECT COUNT(*) FROM Topics WHERE ID = ? AND Topic = ?"
    cursor.execute(sql, [id_number, topic])
    count = cursor.fetchone()[0]

    if count == 0:
        print("WTF 2")
    else:
        sql = "UPDATE Topics SET Examples_Expertise = ?, Last_Update = ? WHERE ID = ? AND Topic = ?"
    cursor.execute(sql, [examples, get_date_time(), id_number, topic])

    connection.commit()
# END OF "for tutor_detail in tutor_detail_list"
print(f"{topic} FINISHED TUTOR WEB PAGES")
'''
