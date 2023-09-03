""" wyzant_login.py

SUMMARY: Function log_into_wyzant handles logging into wyzant website.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.6.0

DATE: Sep 02, 2023
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

# Username and password.
from login_tutor import USERNAME, PASSWORD

TIMEOUT = 30  # Seconds.


def log_into_wyzant(driver):
    """ Function log_into_wyzant.

    Parameters: Selenium driver object, before logging into Wyzant.
    Returns: Selenium driver object, after logging into Wyzant.
    """

    print("Logging into Wyzant.")
    driver.get("https://www.wyzant.com/login")

    WebDriverWait(driver, TIMEOUT).until(ec.title_is("Sign In | Wyzant Tutoring"))
    driver.find_element(By.XPATH, '//form[@class="sso-login-form"]//input[@id="Username"]').send_keys(USERNAME)
    driver.find_element(By.XPATH, '//form[@class="sso-login-form"]//input[@id="Password"]').send_keys(PASSWORD)
    driver.find_element(By.XPATH, '//form[@class="sso-login-form"]/button').click()
    WebDriverWait(driver, TIMEOUT).until(ec.title_is("My Profile | Wyzant Tutoring"))

    print("Done logging into Wyzant.")

    return driver
