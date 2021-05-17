""" functions.py

SUMMARY: Use Selenium to watch for new online jobs on Wyzant.com.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.3.0

DATE: May 16, 2021
"""
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
# End of function send_email.


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


def nested_print(this_name: str, root_dict: dict) -> str:
    """ Get printable report of the elements of a nested dictionary.

    Parameters:
        this_name (str): nameof(root_dict), where "from varname import nameof".
        root_dict (dict): the dictionary whose elements must be printed.
    Returns:
        output (str): printable report of the elements of a nested dictionary.
    """
    output = ""
    for my_key, my_value in root_dict.items():
        if isinstance(my_key, int):
            my_key_value = "[%d]" % my_key
        elif isinstance(my_key, str):
            my_key_value = '["%s"]' % my_key
        else:
            raise NotImplementedError

        if isinstance(my_value, int):
            my_value_value = "%d" % my_value
        elif isinstance(my_value, str):
            my_value_value = '"%s"' % my_value.replace('\n', '<LF>').replace('\r', '<CR>')
        else:
            my_value_value = "WTF?"

        if not isinstance(my_value, dict):
            output += "%s%s = %s\n" % (this_name, my_key_value, my_value_value)
        else:
            output += "%s%s = %s\n" % (this_name, my_key_value, "dict()")
            output += nested_print(this_name+my_key_value, my_value)
    return output
# End of function nested_print.


def age_to_minutes(age: str) -> int:
    """ Convert job age to minutes.

    Parameters:
        age (str): age of job, in units of minutes, hours, or days.
    Returns:
        length (int): age of job in minutes.
    """
    units = age[-1]
    length = int(age[:-1])
    if units == 'm':
        pass
    elif units == 'h':
        length = 60 * length
    elif units == 'd':
        length = 60 * 24 * length
    else:
        # Ages greater than 7 days formatted as "mmm d"
        length = 60 * 24 * 7
    return length
# End of function print_stacktrace.
