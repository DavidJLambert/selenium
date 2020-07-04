""" wyzant.py

SUMMARY: Use Selenium to watch for new online jobs on Wyzant.com.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.1.0

DATE: Jul 3, 2020
"""
from copy import deepcopy
from Check_Chromedriver import Check_Chromedriver
from winsound import Beep
from datetime import datetime
import re
from MyConstants import *
from MyFunctions import *
from MySelenium import *

# ##### GLOBAL VARIABLES #####

# Ignore in-person jobs?
do_in_person = False
if not do_in_person:
    SLEEP_TIME = 2*SLEEP_TIME
    JOB_LOCATIONS = {JOB_ONLINE}

# Print jobs nested dictionary, used in test_MyFunctions.
get_test_data = False
if get_test_data:
    from varname import nameof

# Jobs dicts, stores info about job listings.
jobs = dict()
jobs_prev = dict()

# Initialize jobs and jobs_prev.
for job_location in JOB_LOCATIONS:
    jobs[job_location] = dict()
    jobs_prev[job_location] = dict()

# Jobs urls dicts, stores jobs urls.
job_ids = dict()
job_ids_prev = dict()

# Initialize job_ids and job_ids_prev.
for job_location in JOB_LOCATIONS:
    job_ids[job_location] = set()
    job_ids_prev[job_location] = set()

# ##### FUNCTION DEFINITIONS #####


def process_academy_cards(my_job_loc: str) -> None:
    """ Process HTML elements with class "academy-card".  Each instance of
        "academy-card" contains one Wyzant job listing.

    Parameters:
        my_job_loc (str): Type of job listing (online or in-person).
    Returns:
    """
    # Clear jobs, job_ids.
    jobs[my_job_loc] = dict()
    job_ids[my_job_loc] = set()

    xpath = job_loc2xpath(my_job_loc)
    # TODO 1 "https://www.wyzant.com/tutor/jobs"
    my_selenium.click_sleep_wait(xpath, SLEEP_TIME, BY_ID, JOBS_LIST)
    print("Fetched Wyzant %s jobs list." % job_location)

    # Each instance of class "academy-card" contains 1 job, up to 10 visible.
    academy_cards = my_selenium.get_related_by_class("academy-card")

    for card_num, card_obj in enumerate(academy_cards):
        # Get Job listing URL.
        job_url = card_obj.find_element_by_xpath('./h3/a').get_attribute('href').strip()

        # Extract Job ID, it is after the last "/".
        job_id = job_url.split("/")[-1]

        # Save Job ID to list of current Job IDs.
        job_ids[my_job_loc].add(job_id)

        # Initialize storage of job information.
        jobs[my_job_loc][job_id] = dict()

        # Card Number.
        jobs[my_job_loc][job_id][CARD_NUM] = card_num

        # Age of job listing.
        job_age = card_obj.find_element_by_xpath('./div[1]/span').text.strip()
        jobs[my_job_loc][job_id][JOB_AGE] = process_job_age(job_age)

        # Student name.
        jobs[my_job_loc][job_id][JOB_STUDENT_NAME] = card_obj.find_element_by_xpath('./p[1]').text.strip()

        # Job topic.
        jobs[my_job_loc][job_id][JOB_TOPIC] = card_obj.find_element_by_xpath('./h3/a').text.strip()

        # Job's suggested pay rate.
        pay_rate = card_obj.find_element_by_xpath('./div[3]/span/div/div[1]/span').text
        jobs[my_job_loc][job_id][JOB_PAY_RATE] = process_pay_rate(pay_rate)

        # Job description.
        job_description = card_obj.find_element_by_xpath('./p[2]').text
        re.sub("(\\r\\n){2,}", "\\r\\n", job_description)
        re.sub("\\r{2,}", "\\r", job_description)
        re.sub("\\n{2,}", "\\n", job_description).strip()
        jobs[my_job_loc][job_id][JOB_DESCRIPTION] = job_description

        # Click "Show Details" control to see more job listing info.
        card_obj.find_element_by_xpath('./div[4]/div/div/p').click()

        # Clear jobs[my_job_loc][job_id][JOB_OTHER]
        jobs[my_job_loc][job_id][JOB_OTHER] = dict()

        # Each instance of class "spc_zero" contains one job attribute.
        spc_zeros = card_obj.find_elements_by_class_name("spc-zero")

        # Iterate over all job attributes in class "spc_zero".
        for spc_zero in spc_zeros:
            # There are 1-2 children of class "spc_zero".
            children = spc_zero.find_elements_by_xpath('./child::*')
            if len(children) == 2:
                # Job attribute in 2nd child of class "spc_zero".
                value = spc_zero.find_element_by_xpath('./span[2]').text
            else:
                # Sometimes the job availability attribute isn't the 2nd child of class "spc_zero".
                xpath = './../p[@class="text-semibold spc-tiny"]'
                items = spc_zero.find_elements_by_xpath(xpath)
                value = "; ".join([item.text for item in items])

            # Job attribute in 1st child of class "spc_zero".
            my_key = spc_zero.find_element_by_xpath('./span[1]').text.strip()
            my_key = my_key.strip().replace(":", "")
            jobs[my_job_loc][job_id][JOB_OTHER][my_key] = value.strip()

        # Done iterating over all job attributes in class "spc_zero".

        # Print progress, on just one line.
        if card_num == 0:
            stdout.write("Done fetching %s job %d" % (my_job_loc, card_num))
        else:
            stdout.write(", %d" % card_num)

    # Done iterating over academy_cards.

    # After stdout.write, need to add newline.
    print()
# End of function process_academy_cards.

# ##### EXECUTE CODE #####


if __name__ == '__main__':

    print("About to check the version of chromedriver.exe.")

    # Check the version of chromedriver.exe, and update when needed.
    Check_Chromedriver.driver_mother_path = "./"
    Check_Chromedriver.main()

    print("Done checking the version of chromedriver.exe.")
    print("")

    do_beep = get_boolean("Beep when new job found? ")
    do_email = get_boolean("Email when new job found? ")
    do_log = get_boolean("Save activity to log? ")

    # Open output file for appending.
    if do_log:
        outfile = open('log.txt', 'a')

    print("Initializing Selenium.")
    my_selenium = MySelenium()
    print("Done initializing Selenium.")
    print("Logging into Wyzant.com.")
    # TODO 2 "https://www.wyzant.com/login"
    my_selenium.website_login(USERNAME, PASSWORD, LOGIN_PAGE_URL, PRE_LOGIN_PAGE_TITLE,
                              POST_LOGIN_PAGE_TITLE, USERNAME_FIELD_XPATH,
                              PASSWORD_FIELD_XPATH, LOGIN_BUTTON_XPATH)
    print("Logged into Wyzant.")
    print("Going to Wyzant job listings page.")
    # TODO 3 "https://www.wyzant.com/tutor/jobs"
    my_selenium.go_to_web_page(JOBS_PAGE_URL, BY_ID, JOBS_LIST)
    print("At Wyzant job listings page.")

    # Loop forever.
    while True:

        try:
            if get_test_data:
                print("BEGIN PRINTING JOBS.")
                nested_print(nameof(jobs), jobs)
                print("DONE PRINTING JOBS.")

            # Save (jobs, job_ids) into (jobs_prev, job_ids_prev).
            # Skip if job_ids empty due to faulty page load.
            for job_loc in JOB_LOCATIONS:
                if len(job_ids[job_loc]) > 0:
                    jobs_prev[job_loc] = deepcopy(jobs[job_loc])
                    job_ids_prev[job_loc] = deepcopy(job_ids[job_loc])

            # Fetch jobs.
            for job_loc in JOB_LOCATIONS:
                process_academy_cards(job_loc)

            # Print and write to log file the current datetime.
            date_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "\n"
            stdout.write(date_time)
            if do_log:
                outfile.write(date_time)
                outfile.flush()

            # Look for new jobs.
            for job_loc in JOB_LOCATIONS:
                # Look for job IDs in job_ids and not in job_ids_prev.
                # Skip if job_ids or job_ids_prev empty (1st loop or faulty page load).
                current, previous = job_ids[job_loc], job_ids_prev[job_loc]
                if len(current) * len(previous) > 0:
                    # Could also restrict myself to jobs with age < 1h.
                    new_job_ids = get_new_job_ids(current, previous, jobs[job_loc])

                    # Iterate over all new job listings.
                    for job_id in new_job_ids:
                        # Start collecting data about new job listings.
                        email_subject = "New %s job at www.wyzant.com/tutor/jobs/%s" % (job_loc, job_id)
                        job_data = email_subject + "\n"

                        # Continue collecting job data.
                        job_data = get_job_data(job_data, job_id, job_loc, jobs[job_loc])

                        # Make audible tone.
                        if do_beep:
                            Beep(6000, 1000)

                        # Send email.
                        if do_email:
                            send_email(SMTP_SERVER, SMTP_PORT, SMTP_PASSWORD, EMAIL_SENDER,
                                       EMAIL_RECIPIENT, subject=email_subject, body=job_data)

                        # Print and write to log file the job data.
                        stdout.write(job_data)
                        if do_log:
                            outfile.write(job_data)
                            outfile.flush()
        except (KeyboardInterrupt, SystemExit):
            # Allow for graceful program exit.
            print("LEAVING")
            if do_log:
                outfile.flush()
                outfile.close()
            # Make audible tone.
            if do_beep:
                Beep(4000, 1000)
            raise
        except Exception:
            # Try to keep running on exceptions, but show stack trace.
            print_stacktrace()
