""" wyzant_search_topics.py

SUMMARY: Use Selenium to find my ranking among the tutors for each topic listed in a text file.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.5.7

DATE: Aug 25, 2023
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

from wyzant_login import log_into_wyzant

# Other packages.
import csv
from sys import stdout
from time import sleep

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

    with open('search_topics.txt', 'r') as file:
        for topic in file:
            if topic not in topics:
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

    # Log into wyzant.
    driver = log_into_wyzant(driver)

    stdout.write("Going to the Wyzant find tutors page.\n")

    driver.get("https://www.wyzant.com/match/search")
    sleep(5)
    # this_id = "ctl00_ctl00_PageCPH_CenterColumnCPH_LessonDisplay1_ListViewSession_Pager_NextPageBTN"
    # WebDriverWait(driver, TIMEOUT).until(ec.visibility_of_element_located((By.ID, this_id)))

    stdout.write("At Wyzant find tutors page.\n")

    with open('./output/search_topics.csv', 'w', newline='') as output:
        csvwriter = csv.writer(output)

        # Heading row.
        row = ['Topic', 'Subject', 'Num_Tutors', 'Num_Tutor_Cards', 'Rank']

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
                num_tutors = 0
                num_tutor_cards = 0
                rank = -1
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

                tutor_cards = driver.find_elements(By.XPATH, '//a[contains(@class, "tutor-card")]')
                num_tutor_cards = len(tutor_cards)

                # In case no hits for search term.
                rank = -2

                for index, tutor in enumerate(tutor_cards):
                    url = tutor.get_attribute('href')
                    if "https://www.wyzant.com/match/tutor/88195255" == url[:43]:
                        rank = index
                        break
                rank += 1

            row = [topic, subject, num_tutors, num_tutor_cards, rank]
            print(row)
            csvwriter.writerow(row)


# End of function main.


if __name__ == '__main__':
    main()
