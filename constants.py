""" constants.py

SUMMARY: Use Selenium to watch for new online jobs on Wyzant.com.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.2.1

DATE: Jul 14, 2020
"""
TIMEOUT = 15  # Seconds.
SLEEP_TIME = 15  # Seconds.

# Fields in jobs and jobs_prev.
JOB_ONLINE = "ONLINE"
JOB_IN_PERSON = "IN PERSON"
JOB_LOCATIONS = {JOB_ONLINE, JOB_IN_PERSON}

# For (re)initializing jobs and jobs_prev.
JOB_ID = "Job ID"
JOB_AGE = "Job Age"
STUDENT_NAME = "Student Name"
JOB_TOPIC = "Job Topic"
PAY_RATE = "Job Rate"
JOB_DESCRIPTION = "Job Description"
CARD_NUMBER = "Card Number"

SMTP_SERVER = "smtp-mail.outlook.com"
SMTP_PORT = 587
SMTP_PASSWORD = "!V15%5lzBiGv^34N"
EMAIL_SENDER = "David_J_lambert@outlook.com"
EMAIL_RECIPIENT = "David_J_lambert@outlook.com"

SELENIUM_OPTIONS = ["--window-size=1920,1080"]

# Wyzant.com login information.
USERNAME = "david.lambert.3"
PASSWORD = "40tN7@hu^q4^8R1cw8l#"
LOGIN_PAGE_URL = "https://www.wyzant.com/login"
PRE_LOGIN_PAGE_TITLE = "Sign In | Wyzant Tutoring"
POST_LOGIN_PAGE_TITLE = "My Profile | Wyzant Tutoring"
USERNAME_FIELD_XPATH = '//*[@id="sso_login-landing"]//input[@id="Username"]'
PASSWORD_FIELD_XPATH = '//*[@id="sso_login-landing"]//input[@id="Password"]'
LOGIN_BUTTON_XPATH = '//*[@id="sso_login-landing"]/form/button'

# Other Wyzant information.
JOBS_PAGE_URL = "https://www.wyzant.com/tutor/jobs"
JOBS_PAGE_TITLE = "Jobs | Wyzant Tutoring"

# How to wait for refresh
BY_ID = "BY ID"
BY_PAGE_TITLE = "BY PAGE TITLE"
JOBS_LIST = "jobs-list"
