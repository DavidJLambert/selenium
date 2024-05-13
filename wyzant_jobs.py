""" wyzant_jobs.py

SUMMARY: Use Selenium to watch for new online jobs on Wyzant.com.

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

# Web Browser dependent Selenium code.
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from wyzant_login import log_into_wyzant

# Other packages.
from traceback import print_exception
from sys import exc_info
from copy import deepcopy
from winsound import Beep
from datetime import datetime, date
from time import sleep

# CONSTANTS.

TIMEOUT = 30  # Seconds.
SLEEP_TIME = 30  # Seconds.
MY_CLASS_NAME = "ui-page-link"

# Keys for the jobs_curr and jobs_prev dictionaries.
JOB_ID = "Job ID"
APPLICATIONS = "Applications"
JOB_AGE = "Age"
STUDENT_NAME = "Name"
JOB_TOPIC = "Topic"
PAY_RATE = "Rate"
JOB_DESCRIPTION = "Description"
CARD_NUMBER = "Card #"


def age_to_minutes(arg: str) -> int:
    """ Convert job age to minutes.

    Parameters:
        arg (str): either age of job, in units of minutes, hours, or days,
                   or date (format "mmm d") job was submitted.
    Returns:
        length (int): age of job in minutes.
    """
    if arg[-1].isdigit():
        # age contains date
        now = date.today()
        submitted = datetime.strptime(arg, "%b %d").date()
        delta = now - submitted
        length = 60 * 24 * delta.days
    else:
        units = arg[-1]
        length = int(arg[:-1])
        if units == 'm':
            pass
        elif units == 'h':
            length = 60 * length
        elif units == 'd':
            length = 60 * 24 * length
        else:
            print("UNKNOWN ELAPSED TIME UNITS")
            length = 0
    return length
# End of function age_to_minutes.


def main():
    """ Function main.  Watch for new online jobs on Wyzant.com.

    Parameters:
    Returns:
    """

    # On Exception, come back to here and re-initialize everything.
    while True:
        try:
            # Job dicts, store info about job listings.
            jobs_curr = dict()
            jobs_prev = dict()
            # Job_ids sets, store the job_ids for job dict.
            job_ids_curr = set()
            job_ids_prev = set()

            # Selenium options.
            print("Initializing Selenium.")
            options = Options()
            options.add_argument('--headless')
            options.add_argument("--window-size=1920,2200")

            # Connect to the Selenium web driver.
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            # Maximize the browser window.
            driver.maximize_window()

            print("Done initializing Selenium.")

            # Log into wyzant.
            driver = log_into_wyzant(driver)

            print("Going to the Wyzant job listings page.")

            driver.get("https://www.wyzant.com/tutor/jobs")
            WebDriverWait(driver, TIMEOUT).until(ec.visibility_of_element_located((By.CLASS_NAME, MY_CLASS_NAME)))

            print("At Wyzant job listings page.")
            print(f"Sleeping for {SLEEP_TIME} seconds.")

            driver.find_element(By.XPATH, "//label[@for='lesson_type_online']").click()
            # sleep(SLEEP_TIME)  # Seconds.
            WebDriverWait(driver, TIMEOUT).until(ec.visibility_of_element_located((By.CLASS_NAME, MY_CLASS_NAME)))

            print("Fetched Wyzant jobs list.")

            # Loop forever.
            while True:
                driver.refresh()
                WebDriverWait(driver, TIMEOUT).until(ec.visibility_of_element_located((By.CLASS_NAME, MY_CLASS_NAME)))

                # Save jobs_curr and job_ids_curr into jobs_prev and job_ids_prev, respectively.
                # Skip if jobs_curr empty due to faulty page load.
                if len(jobs_curr) > 0:
                    jobs_prev = deepcopy(jobs_curr)
                    job_ids_prev = deepcopy(job_ids_curr)
                    jobs_curr.clear()
                    job_ids_curr.clear()

                # Print the current datetime.
                date_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                print(date_time + "    ", end="")

                # Each instance of class "academy-card" contains 1 job, 10 cards per page.
                academy_cards = driver.find_elements(By.CLASS_NAME, "academy-card")

                for card_num, card_obj in enumerate(academy_cards):
                    # Get Job listing URL.
                    job_url = card_obj.find_element(By.XPATH, './h3/a').get_attribute('href')

                    # Save job properties.
                    params = dict()
                    params[JOB_ID] = int(job_url.split("/")[-1].strip())
                    params[CARD_NUMBER] = card_num
                    job_age_info = card_obj.find_element(By.XPATH, './div[1]/span[1]').text.strip()
                    if job_age_info == "No applications yet":
                        params[APPLICATIONS] = "N"
                        job_age_info = card_obj.find_element(By.XPATH, './div[1]/span[2]').text.strip()
                    else:
                        params[APPLICATIONS] = "Y"
                    params[JOB_AGE] = age_to_minutes(job_age_info)
                    params[STUDENT_NAME] = card_obj.find_element(By.XPATH, './p[1]').text.strip()
                    params[JOB_TOPIC] = card_obj.find_element(By.XPATH, './h3/a').text.strip()
                    pay_rate = card_obj.find_element(By.XPATH, './div[3]/span/div/div[1]/span').text.strip()
                    params[PAY_RATE] = pay_rate.replace("Recommended rate: ", "")
                    params[JOB_DESCRIPTION] = card_obj.find_element(By.XPATH, './p[2]').text.strip()

                    # Does "Show Details" control exist?
                    show_details = card_obj.find_elements(By.XPATH, './div[4]/div/div/p')
                    if len(show_details) == 1:
                        # If "Show Details" exists, click it.
                        show_details[0].click()

                        # Each instance of class "spc_zero" contains one job attribute.
                        spc_zeros = card_obj.find_elements(By.CLASS_NAME, "spc-zero")

                        # Iterate over all job attributes in class "spc_zero".
                        for spc_zero in spc_zeros:
                            # There are 1-2 children of class "spc_zero".
                            children = spc_zero.find_elements(By.XPATH, './child::*')
                            if len(children) == 2:
                                # Job attribute in 2nd child of class "spc_zero".
                                value = spc_zero.find_element(By.XPATH, './span[2]').text.strip()
                            else:
                                # Sometimes the job availability attribute isn't the 2nd child of class "spc_zero".
                                xpath = './../p[@class="text-semibold spc-tiny"]'
                                items = spc_zero.find_elements(By.XPATH, xpath)
                                value = "; ".join([item.text for item in items]).strip()

                            # Job attribute in 1st child of class "spc_zero".
                            my_key = spc_zero.find_element(By.XPATH, './span[1]').text
                            my_key = my_key.replace(":", "").strip()
                            params[my_key] = value
                        # Done iterating over all job attributes in class "spc_zero".

                    # Save job properties in new entry in dict jobs_curr, and save job_id in set job_ids_curr.
                    # for key, value in params.items():
                    #     print("params", key, value)
                    # Description?
                    # Availability?
                    job_id = params[JOB_ID]
                    jobs_curr[job_id] = params
                    job_ids_curr.add(job_id)

                    # Print progress, on just one line.
                    if card_num == 0:
                        print(f"Done fetching job {card_num}", end="")
                    else:
                        print(f", {card_num}", end="")
                # Done iterating over academy_cards.

                # After print, need to add newline.
                print()

                # Look for new jobs: the job IDs in job_ids and not in job_ids_prev.
                current_num = len(jobs_curr)
                previous_num = len(jobs_prev)
                # Skip if job_ids or job_ids_prev has too few entries (1st loop or faulty page load).
                if current_num == 0:
                    print(f"Current  # Job IDs: {current_num}.")
                elif previous_num == 0:
                    print(f"Previous # Job IDs: {previous_num}.")
                else:
                    new_job_ids = job_ids_curr.difference(job_ids_prev)

                    # Iterate over all new job listings.
                    for job_id in new_job_ids:
                        age = jobs_curr[job_id][JOB_AGE]
                        if age <= 10:
                            keys = jobs_curr[job_id].keys()

                            job_summary = f"New job at www.wyzant.com/tutor/jobs/{job_id}"

                            key = 'Rate'
                            if key in keys:
                                value = jobs_curr[job_id][key]
                                job_summary += f'\n{key.upper()}: "{value}"'
                            key = 'Topic'
                            if key in keys:
                                value = jobs_curr[job_id][key]
                                job_summary += f'\n{key.upper()}: "{value}"'
                            key = 'Subject'
                            if key in keys:
                                value = jobs_curr[job_id][key]
                                job_summary += f'\n{key.upper()}: "{value}"'
                            key = 'Student grade level'
                            if key in keys:
                                value = jobs_curr[job_id][key]
                                job_summary += f'\n{key.upper()}: "{value}"'
                            key = 'Description'
                            if key in keys:
                                value = jobs_curr[job_id][key]
                                job_summary += f'\n{key.upper()}: "{value}"'

                            # Make audible tone.
                            Beep(6000, 1000)

                            # Print the job summary.
                            print(job_summary)
                    # Done iterating over new_job_ids.

                # Wait some more, so that jobs page polled about every 30 seconds.
                sleep(20)
            # End of inner while loop.
        except Exception:
            # Print exception.
            print_exception(*exc_info(), limit=None)
            # Make audible tone.
            Beep(1000, 1000)
            # Wait, in case of a web glitch.
            sleep(SLEEP_TIME)
            # Start over.
    # End of outer while loop.
# End of function main.


if __name__ == '__main__':
    main()
