""" functions.py

SUMMARY: Use Selenium to watch for new online jobs on Wyzant.com.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.2.0

DATE: Jul 11, 2020
"""
from constants import JOB_ONLINE, JOB_IN_PERSON

from sys import stdout, exc_info
from traceback import print_exception
from smtplib import SMTP
from ssl import create_default_context
from email.mime.text import MIMEText


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
            stdout.write("Entered 'Yes'.\n")
            return True
        elif result in {"F", "N", "0"}:
            stdout.write("Entered 'No'.\n")
            return False
        else:
            stdout.write("Invalid choice, try again.\n")
# End of function print_stacktrace.


def print_stacktrace() -> None:
    """ Print a stack trace, then resume.

    Parameters:
    Returns:
    """
    print_exception(*exc_info(), limit=None, file=stdout)
# End of function print_stacktrace.


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
            stdout.write("%s%s = %s\n" % (this_name, my_key_value, my_value_value))
        else:
            stdout.write("%s%s = %s\n" % (this_name, my_key_value, "dict()"))
            nested_print(this_name+my_key_value, my_value)
    return


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
