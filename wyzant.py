""" wyzant.py

SUMMARY: Use Selenium to watch for new online jobs on Wyzant.com.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.2.0

DATE: Jul 11, 2020
"""


def main():
    """ Function main.  Watch for new online jobs on Wyzant.com.

    Parameters:
    Returns:
    """
    import constants as c
    import functions as f
    from varname import nameof
    from sys import stdout
    from MySelenium import MySelenium
    from Jobs import Jobs
    from copy import deepcopy
    from Check_Chromedriver import Check_Chromedriver
    from winsound import Beep
    from datetime import datetime

    # Ignore in-person jobs?
    do_in_person = False
    if not do_in_person:
        SLEEP_TIME = 2 * c.SLEEP_TIME
        JOB_LOCATIONS = {c.JOB_ONLINE}
    else:
        SLEEP_TIME = c.SLEEP_TIME
        JOB_LOCATIONS = c.JOB_LOCATIONS

    # Print jobs nested dictionary, used in test_MyFunctions.
    get_test_data = False

    # Jobs dicts, stores info about job listings.
    jobs, jobs_prev = dict(), dict()

    for job_loc in JOB_LOCATIONS:
        jobs[job_loc], jobs_prev[job_loc] = Jobs(), Jobs()

    # Check the version of chromedriver.exe, and update when needed.
    Check_Chromedriver.driver_mother_path = "./"
    Check_Chromedriver.main()

    stdout.write("Done checking the version of chromedriver.exe.\n")
    stdout.write("\n")

    do_beep = f.get_boolean("Beep when new job found? ")
    do_email = f.get_boolean("Email when new job found? ")
    do_log = f.get_boolean("Save activity to log? ")

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
    my_selenium.go_to_web_page(c.JOBS_PAGE_URL, c.BY_ID, c.JOBS_LIST)
    stdout.write("At Wyzant job listings page.\n")

    # Loop forever.
    while True:

        try:
            if get_test_data:
                stdout.write("BEGIN PRINTING JOBS.\n")
                f.nested_print(nameof(jobs), jobs)
                stdout.write("DONE PRINTING JOBS.\n")

            # Fetch jobs.
            for job_loc in JOB_LOCATIONS:
                # Save jobs into jobs_prev.  Skip if job_ids empty due to faulty page load.
                if jobs[job_loc].count_job_ids() > 0:
                    jobs_prev[job_loc] = deepcopy(jobs[job_loc])

                # Clear jobs.
                jobs[job_loc].reset()

                # Print and write to log file the current datetime.
                date_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                stdout.write(date_time + "  ")
                if do_log:
                    outfile.write(date_time + "\n")
                    outfile.flush()

                xpath = f.job_loc2xpath(job_loc)
                my_selenium.click_sleep_wait(xpath, SLEEP_TIME, c.BY_ID, c.JOBS_LIST)
                stdout.write("Fetched Wyzant %s jobs list.  " % job_loc)

                # Each instance of class "academy-card" contains 1 job, 10 visible.
                academy_cards = my_selenium.get_related_by_class("academy-card")

                for card_num, card_obj in enumerate(academy_cards):
                    # Get Job listing URL.
                    job_url = card_obj.find_element_by_xpath('./h3/a').get_attribute('href').strip()

                    # Extract Job ID, it is after the last "/".
                    job_id = job_url.split("/")[-1]

                    # Initialize storage of job information.
                    jobs[job_loc].add_job_id(job_id)

                    # Age of job listing.
                    job_age = card_obj.find_element_by_xpath('./div[1]/span').text
                    # Student name.
                    student_name = card_obj.find_element_by_xpath('./p[1]').text
                    # Job topic.
                    job_topic = card_obj.find_element_by_xpath('./h3/a').text
                    # Job's suggested pay rate.
                    pay_rate = card_obj.find_element_by_xpath('./div[3]/span/div/div[1]/span').text
                    # Job description.
                    job_description = card_obj.find_element_by_xpath('./p[2]').text

                    # Click "Show Details" control to see more job listing info.
                    card_obj.find_element_by_xpath('./div[4]/div/div/p').click()

                    # Each instance of class "spc_zero" contains one job attribute.
                    spc_zeros = card_obj.find_elements_by_class_name("spc-zero")

                    # Iterate over all job attributes in class "spc_zero".
                    other_params = dict()
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
                        my_key = spc_zero.find_element_by_xpath('./span[1]').text
                        my_key = my_key.strip().replace(":", "")
                        other_params[my_key] = value.strip()

                    # Add properties of this job_id.
                    jobs[job_loc].add_properties(job_id, card_num, job_age, student_name,
                                                 job_topic, pay_rate, job_description, **other_params)
                    # Done iterating over all job attributes in class "spc_zero".

                    # Print progress, on just one line.
                    if card_num == 0:
                        stdout.write("Done fetching %s job %d" % (job_loc, card_num))
                    else:
                        stdout.write(", %d" % card_num)
                # Done iterating over academy_cards.

                # After stdout.write, need to add newline.
                stdout.write("\n")

            # Look for new jobs.
            for job_loc in JOB_LOCATIONS:
                # Look for job IDs in job_ids and not in job_ids_prev.
                # Skip if job_ids or job_ids_prev empty (1st loop or faulty page load).
                current_num = jobs[job_loc].count_job_ids()
                previous_num = jobs_prev[job_loc].count_job_ids()
                if current_num <= 0:
                    stdout.write("Current  # Job IDs: %d.\n" % current_num)
                elif previous_num <= 0:
                    stdout.write("Previous # Job IDs: %d.\n" % previous_num)
                else:
                    # Could also restrict myself to jobs with age < 1h.
                    job_ids_previous = jobs_prev[job_loc].get_job_ids()
                    new_job_ids = jobs[job_loc].get_new_job_ids(job_ids_previous)

                    # Iterate over all new job listings.
                    for job_id in new_job_ids:
                        # Start collecting job data.
                        email_subject = "New %s job at www.wyzant.com/tutor/jobs/%s" % (job_loc, job_id)
                        job_data = email_subject + "\n"

                        # Continue collecting job data.
                        job_data = jobs[job_loc].get_job_data(job_data, job_id, job_loc)

                        # Make audible tone.
                        if do_beep:
                            Beep(6000, 1000)

                        # Send email.
                        if do_email:
                            f.send_email(c.SMTP_SERVER, c.SMTP_PORT, c.SMTP_PASSWORD, c.EMAIL_SENDER,
                                         c.EMAIL_RECIPIENT, subject=email_subject, body=job_data)

                        # Print and write to log file the job data.
                        stdout.write(job_data)
                        if do_log:
                            outfile.write(job_data)
                            outfile.flush()
        except (KeyboardInterrupt, SystemExit):
            # Allow for graceful program exit.
            stdout.write("LEAVING\n")
            if do_log:
                outfile.flush()
                outfile.close()
            # Make audible tone.
            if do_beep:
                Beep(4000, 1000)
            raise
        except Exception:
            # Try to keep running on exceptions, but show stack trace.
            f.print_stacktrace()
# End of function main.


if __name__ == '__main__':
    main()
