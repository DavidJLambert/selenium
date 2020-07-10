""" MyFunctions.py

SUMMARY: Use Selenium to watch for new online jobs on Wyzant.com.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.1.0

DATE: Jul 3, 2020
"""
import re
from smtplib import SMTP
from ssl import create_default_context
from email.mime.text import MIMEText

from MyConstants import *
from sys import stdout, exc_info
from traceback import print_exception


def send_email(smtp_server: str, port: int, password: str, sender: str,
               recipient: str, subject: str, body: str) -> None:
    """ Send SMTP email message.

    Parameters:
        smtp_server (str): SMTP server to use.
        port (int): port number SMTP server is listening on.
        password (str):
        sender (str):
        recipient (str):
        subject (str):
        body (str): Body of the email.
    Returns:
    """
    message = MIMEText(body)
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = recipient

    context = create_default_context()
    with SMTP(host=smtp_server, port=port) as server:
        server.starttls(context=context)
        server.login(user=recipient, password=password)
        server.sendmail(from_addr=sender, to_addrs=recipient, msg=message.as_string())


def get_boolean(prompt: str) -> bool:
    """ Process result of prompt to get boolean.

    Parameters:
        prompt (str): prompt to get True/False response.
    Returns:
        result (bool): True or FaLse.
    """
    while True:
        result = input(prompt)[0].upper()
        if result in {"T", "Y", "1"}:
            print("Entered 'Yes'.")
            return True
        elif result in {"F", "N", "0"}:
            print("Entered 'No'.")
            return False
        else:
            print("Invalid choice, try again.")
# End of function print_stacktrace.


def print_stacktrace() -> None:
    """ Print a stack trace, then resume.

    Parameters:
    Returns:
    """
    print_exception(*exc_info(), limit=None, file=stdout)
# End of function print_stacktrace.


def process_job_age(job_age: str) -> int:
    """ Process the age of a job listing.

    Parameters:
        job_age (str): the age of a job listing.
    Returns:
        job_age (int): the age of a job listing, in minutes.
    """
    last_char = job_age.strip()[-1]
    if last_char == "m":
        job_age = int(job_age[:-1])
    elif last_char == "h":
        job_age = 60 * int(job_age[:-1])
    elif last_char == "d":
        job_age = 24 * 60 * int(job_age[:-1])
    else:
        job_age = 8 * 24 * 60
    return job_age
# End of function process_job_age.


def process_pay_rate(pay_rate: str) -> int:
    """ Process the pay rate of a job listing.

    Parameters:
        pay_rate (str): the pay rate of a job listing.
    Returns:
        pay_rate (int): the pay rate of a job listing.
    """
    pay_rate = pay_rate.replace("Recommended rate: ", "")
    pay_rate = pay_rate.replace("/hr", "")
    pay_rate = pay_rate.replace("$", "").strip()
    if pay_rate == "None":
        pay_rate = None
    else:
        pay_rate = int(pay_rate)
    return pay_rate
# End of function process_job_age.


def process_job_description(job_description: str) -> str:
    """ Process the job description of a job listing.

    Parameters:
        job_description (str): the job_description of a job listing.
    Returns:
        job_description (str): the job_description of a job listing.
    """
    re.sub("(\\r\\n){2,}", "\\r\\n", job_description.strip())
    re.sub("\\r{2,}", "\\r", job_description)
    re.sub("\\n{2,}", "\\n", job_description).strip()
    return job_description
# End of function process_job_description.


def job_loc2xpath(job_location: str) -> str:
    """ Get the xpath for online and in-person job listings.

    Parameters:
        job_location (str): JOB_ONLINE or JOB_IN_PERSON.
    Returns:
        xpath (str): the job listings xpath for given job_location.
    """
    if job_location == JOB_ONLINE:
        # Look for online jobs.
        xpath = "//label[@for='lesson_type_online']"
    elif job_location == JOB_IN_PERSON:
        # Look for in-person jobs.
        xpath = "//label[@for='lesson_type_in_person']"
    else:
        raise ValueError("Unknown job location: '%s'." % job_location)
    return xpath
# End of function job_loc2xpath.


def nested_print(this_name: str, root_dict: dict) -> None:
    """ Print the elements of a nested dictionary.

    Parameters:
        this_name (str): nameof(root_dict), where "from varname import nameof".
        root_dict (dict): the dictionary whose elements must be printed.
    Returns:
    """
    for my_key, my_value in root_dict.items():
        if isinstance(my_key, int):
            my_key_value = "[%d]" % my_key
        elif isinstance(my_key, str):
            my_key_value = "['%s']" % my_key
        else:
            raise NotImplementedError

        if isinstance(my_value, int):
            my_value_value = "%d" % my_value
        elif isinstance(my_value, str):
            my_value_value = '"%s"' % my_value.replace('\n', '<LF>').replace('\r', '<CR>')
        else:
            raise NotImplementedError

        if not isinstance(my_value, dict):
            print("%s%s = %s" % (this_name, my_key_value, my_value_value))
        else:
            print("%s%s = %s" % (this_name, my_key_value, "dict()"))
            nested_print(this_name+my_key_value, my_value)
    return


def get_new_job_ids(current: set, previous: set, jobs: dict) -> set:
    """  Find job_id's in both job_ids[job_loc] and job_ids_prev[job_loc].

    Parameters:
        current (set): job_ids[job_loc].
        previous (set): job_ids_prev[job_loc].
        jobs (dict): nested dictionary.
    Returns:
        new_job_ids (set): the job IDs in current, but not in previous.
    """
    job_ids_in_both = current.intersection(previous)
    # Find smallest card_num ("cn") for job_id's in job_id_in_both.
    min_cn = [jobs[job_id][CARD_NUM] for job_id in job_ids_in_both]
    min_cn = min(min_cn)
    # Find job_id's with card_num's < min_cn.
    new_job_ids = [job_id for job_id in current if jobs[job_id][CARD_NUM] < min_cn]
    return set(new_job_ids)
# End of function get_new_job_ids.


def get_job_data(job_data: str, job_id: str, job_loc: str, jobs: dict) -> str:
    """  Extract job data from jobs[job_id], add to job_data.

    Parameters:
        job_data (str): job_ids[job_loc].
        job_id (str): job_ids_prev[job_loc].
        job_loc (str): include in job_data.
        jobs (dict): nested dictionary.
    Returns:
        job_data (str): the job IDs in current, but not in previous.
    """
    for key in jobs[job_id].keys():
        value = jobs[job_id][key]
        job_data += "('%s', '%s', '%s'): '%s'\n" % (job_loc, job_id, key, value)
    return job_data
# End of function get_job_data.
