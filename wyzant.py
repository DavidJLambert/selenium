""" wyzant.py

SUMMARY: Use Selenium to watch for new online jobs on Wyzant.com.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.3.1

DATE: July 17, 2021
"""
import constants as c
import functions as f
from MySelenium import MySelenium
from Jobs import Jobs

from sys import stdout
from copy import deepcopy
from winsound import Beep
from datetime import datetime
from time import sleep

# from Check_Chromedriver import Check_Chromedriver


def main():
    """ Function main.  Watch for new online jobs on Wyzant.com.

    Parameters:
    Returns:
    """
    do_beep = f.get_boolean("Beep when new job found? ")
    do_email = f.get_boolean("Email when new job found? ")
    do_log = f.get_boolean("Save activity to log? ")

    # Print jobs.
    print_jobs = False

    # On Exception, come back to here and re-initialize everything.
    while True:
        try:
            # Jobs dicts, stores info about job listings.
            jobs = Jobs()
            jobs_prev = Jobs()

            # Check the version of chromedriver.exe, and update when needed.
            # Check_Chromedriver.driver_mother_path = r"C:\Program Files\WebDrivers"
            # Check_Chromedriver.main()

            # stdout.write("Done checking the version of chromedriver.exe.\n\n")

            # Open output file for appending.
            if do_log:
                outfile = open('log.txt', 'a')
            else:
                outfile = None

            stdout.write("Initializing Selenium.\n")
            my_selenium = MySelenium()
            stdout.write("Done initializing Selenium.\n")
            stdout.write("Logging into Wyzant.\n")
            my_selenium.website_login(c.USERNAME, c.PASSWORD, c.LOGIN_PAGE_URL, c.PRE_LOGIN_PAGE_TITLE,
                                      c.POST_LOGIN_PAGE_TITLE, c.USERNAME_FIELD_XPATH,
                                      c.PASSWORD_FIELD_XPATH, c.LOGIN_BUTTON_XPATH)
            stdout.write("Done logging into Wyzant.\n")
            stdout.write("Going to the Wyzant job listings page.\n")
            my_selenium.go_to_web_page(c.JOBS_PAGE_URL, c.BY_CLASS, c.UI_PAGE_LINK)
            stdout.write("At Wyzant job listings page.\n")

            xpath = "//label[@for='lesson_type_online']"
            my_selenium.click_sleep_wait(xpath, c.SLEEP_TIME, c.BY_CLASS, c.UI_PAGE_LINK)
            stdout.write("Fetched Wyzant jobs list.  ")

            # Loop forever.
            while True:
                my_selenium.force_refresh(c.BY_CLASS, c.UI_PAGE_LINK)

                # Save jobs into jobs_prev.  Skip if job_ids empty due to faulty page load.
                if jobs.count_jobs() > 0:
                    jobs_prev = deepcopy(jobs)
                    jobs.reset()

                # Print and write to log file the current datetime.
                date_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                stdout.write(date_time + "  ")
                if do_log:
                    outfile.write(date_time + "\n")
                    outfile.flush()

                # Each instance of class "academy-card" contains 1 job, 10 visible per page.
                academy_cards = my_selenium.get_related_by_class("academy-card")

                for card_num, card_obj in enumerate(academy_cards):
                    # Get Job listing URL.
                    job_url = card_obj.find_element_by_xpath('./h3/a').get_attribute('href')

                    # Save job properties.
                    params = dict()
                    params[c.JOB_ID] = int(job_url.split("/")[-1].strip())
                    params[c.CARD_NUMBER] = card_num
                    job_age_info = card_obj.find_element_by_xpath('./div[1]/span[1]').text.strip()
                    if job_age_info == "No applications yet":
                        params[c.APPLICATIONS] = "N"
                        job_age_info = card_obj.find_element_by_xpath('./div[1]/span[2]').text.strip()
                    else:
                        params[c.APPLICATIONS] = "Y"
                    params[c.JOB_AGE] = f.age_to_minutes(job_age_info)
                    params[c.STUDENT_NAME] = card_obj.find_element_by_xpath('./p[1]').text.strip()
                    params[c.JOB_TOPIC] = card_obj.find_element_by_xpath('./h3/a').text.strip()
                    pay_rate = card_obj.find_element_by_xpath('./div[3]/span/div/div[1]/span').text.strip()
                    params[c.PAY_RATE] = pay_rate.replace("Recommended rate: ", "")
                    params[c.JOB_DESCRIPTION] = card_obj.find_element_by_xpath('./p[2]').text.strip()

                    # Does "Show Details" control exist?
                    show_details = card_obj.find_elements_by_xpath('./div[4]/div/div/p')
                    if len(show_details) == 1:
                        # If "Show Details" exists, click it.
                        show_details[0].click()

                        # Each instance of class "spc_zero" contains one job attribute.
                        spc_zeros = card_obj.find_elements_by_class_name("spc-zero")

                        # Iterate over all job attributes in class "spc_zero".
                        for spc_zero in spc_zeros:
                            # There are 1-2 children of class "spc_zero".
                            children = spc_zero.find_elements_by_xpath('./child::*')
                            if len(children) == 2:
                                # Job attribute in 2nd child of class "spc_zero".
                                value = spc_zero.find_element_by_xpath('./span[2]').text.strip()
                            else:
                                # Sometimes the job availability attribute isn't the 2nd child of class "spc_zero".
                                xpath = './../p[@class="text-semibold spc-tiny"]'
                                items = spc_zero.find_elements_by_xpath(xpath)
                                value = "; ".join([item.text for item in items]).strip()

                            # Job attribute in 1st child of class "spc_zero".
                            my_key = spc_zero.find_element_by_xpath('./span[1]').text
                            my_key = my_key.replace(":", "").strip()
                            params[my_key] = value
                        # Done iterating over all job attributes in class "spc_zero".

                    # Save job properties in new instance of class Jobs.
                    jobs.add_job(**params)

                    # Print progress, on just one line.
                    if card_num == 0:
                        stdout.write(f"Done fetching job {card_num}")
                    else:
                        stdout.write(f", {card_num}")
                # Done iterating over academy_cards.

                # After stdout.write, need to add newline.
                stdout.write("\n")

                # Look for new jobs.
                # Get job IDs in job_ids and not in job_ids_prev.
                current_num = jobs.count_jobs()
                previous_num = jobs_prev.count_jobs()
                # Skip if job_ids or job_ids_prev has <= 10 entries (1st loop or faulty page load).
                if current_num <= 0:
                    stdout.write(f"Current  # Job IDs: {current_num}.\n")
                elif previous_num <= 0:
                    stdout.write(f"Previous # Job IDs: {previous_num}.\n")
                else:
                    job_ids_previous = jobs_prev.get_job_ids()
                    new_job_ids = jobs.get_new_job_ids(job_ids_previous)

                    # Iterate over all new job listings.
                    for job_id in new_job_ids:
                        # Collect job data.
                        email_subject = f"New job at www.wyzant.com/tutor/jobs/{job_id}"
                        job_summary, job_data, age = jobs.get_job_data(email_subject + "\n", job_id)

                        if age <= 120:
                            # Make audible tone.
                            if do_beep:
                                Beep(6000, 1000)

                            # Send email.
                            if do_email:
                                f.send_email(c.SMTP_SERVER, c.SMTP_PORT, c.SMTP_PASSWORD, c.EMAIL_SENDER,
                                             c.EMAIL_RECIPIENT, subject=email_subject, body=job_data)

                            # Print the job data, write job summary to log file.
                            stdout.write(job_data)
                            if do_log:
                                outfile.write(job_summary + "\n")
                                outfile.flush()
                    # Done iterating over new_job_ids.

                if print_jobs and jobs is not None:
                    stdout.write("BEGIN PRINTING JOBS.\n")
                    stdout.write(str(jobs)+'\n')
                    stdout.write("DONE PRINTING JOBS.\n")

                # Wait some more, so that jobs page polled about every 30 seconds.
                sleep(20)
            # End of inner while loop.
        except Exception:
            # Print exception.
            f.print_stacktrace()
            # Close log file.
            if do_log:
                outfile.flush()
                outfile.close()
            # Make audible tone.
            if do_beep:
                Beep(1000, 1000)
            # Wait, in case of a web glitch.
            sleep(c.SLEEP_TIME)
            # Start over.
    # End of outer while loop.
# End of function main.


if __name__ == '__main__':
    main()
