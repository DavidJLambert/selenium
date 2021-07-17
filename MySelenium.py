""" MySelenium.py

SUMMARY: Use Selenium to watch for new online jobs on Wyzant.com.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.3.0

DATE: May 16, 2021
"""
from constants import BY_ID, BY_PAGE_TITLE, BY_CLASS, TIMEOUT, SELENIUM_OPTIONS
from functions import print_stacktrace

from time import sleep
from sys import stdout

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class MySelenium(object):
    """ Class encapsulating driver object

    Attributes:
        self.options.headless
        self.driver
    """
    def __init__(self) -> None:
        """ Constructor method for this class.

        Parameters:
        Returns:
        """
        self.options = Options()
        self.options.headless = True
        self.options.add_argument(SELENIUM_OPTIONS)

        self.driver = webdriver.Chrome(options=self.options,
                                       executable_path=r"C:\Program Files\WebDrivers\chromedriver.exe")
    # End of method __init__.

    def force_refresh(self, method: str, identifier: str) -> None:
        """ Force Selenium to refresh web page.
        Parameters:
            method (str): method to wait for refresh, BY_ID, BY_PAGE_TITLE, or BY_CLASS.
            identifier (str):
                method = BY_PAGE_TITLE, title of web page shown after logging in.
                method = BY_ID, HTML element ID.
                method = BY_CLASS, HTML element class.
        Returns:
        """
        self.driver.refresh()
        self.wait_for_refresh(method, identifier)
    # End of method force_refresh.

    def wait_for_refresh(self, method: str, identifier: str) -> None:
        """ Make Selenium wait for web page to post.

        Parameters:
            method (str): method to wait for refresh, BY_ID, BY_PAGE_TITLE, or BY_CLASS.
            identifier (str):
                method = BY_PAGE_TITLE, title of web page shown after logging in.
                method = BY_ID, HTML element ID.
                method = BY_CLASS, HTML element class.
        Returns:
        """
        try:
            if method == BY_PAGE_TITLE:
                WebDriverWait(self.driver, TIMEOUT).until(EC.title_is(identifier))
            elif method == BY_ID:
                WebDriverWait(self.driver, TIMEOUT).until(EC.visibility_of_element_located((By.ID, identifier)))
            elif method == BY_CLASS:
                WebDriverWait(self.driver, TIMEOUT).until(EC.visibility_of_element_located((By.CLASS_NAME, identifier)))
            else:
                raise ValueError("Unknown Method.")
        except TimeoutException:
            print_stacktrace()
    # End of method wait_for_refresh.

    def wait_for_refresh2(self, my_driver: webdriver.chrome.webdriver.WebDriver, EC_type: type,
                      BY_type: str, location: str, sleep_time: int) -> None:
        """ Not implemented.

        Parameters:
            my_driver (webdriver.chrome.webdriver.WebDriver): Selenium object.
            EC_type (type): EC attribute to use.
            BY_type (str): BY attribute to use.
            location (str): string value for EC_type.
            sleep_time (int): extra time to wait, in seconds.
        Returns:
        """

        # Wait for Lesson History Page to post.
        if EC_type is EC.title_is:
            WebDriverWait(my_driver, TIMEOUT).until(EC_type(location))
        elif EC_type is EC.presence_of_element_located:
            WebDriverWait(my_driver, TIMEOUT).until(EC_type((BY_type, location)))
        else:
            raise NotImplementedError(f"{str(EC_type)} is unexpected.")
        sleep(sleep_time)

    def click_sleep_wait(self, xpath: str, sleep_time: int, method: str, identifier: str) -> None:
        """ Click control and wait for expected web page title to appear.

        Parameters:
            xpath (str):  xpath of control.
            sleep_time (int): length of time to sleep, in seconds.
            method (str): method to wait for refresh, BY_ID, BY_PAGE_TITLE, or BY_CLASS.
            identifier (str):
                method = BY_PAGE_TITLE, title of web page shown after logging in.
                method = BY_ID, HTML element ID.
                method = BY_CLASS, HTML element class.
        Returns:
        """
        if method not in {BY_ID, BY_PAGE_TITLE, BY_CLASS}:
            raise ValueError("Unknown Method.")

        # Click control.
        self.driver.find_element_by_xpath(xpath).click()

        if sleep_time > 0:
            stdout.write(f"Sleeping for {sleep_time} seconds.  ")
            sleep(sleep_time)  # Seconds.

        # Wait for expected page title.
        self.wait_for_refresh(method, identifier)
    # End of method click_sleep_wait.

    def website_login(self, username: str, password: str, login_page_url: str,
                      pre_login_page_title: str, post_login_page_title: str,
                      username_field_xpath: str, password_field_xpath: str,
                      login_button_xpath: str) -> None:
        """ Login into web site.

        Parameters:
            username (str): web site username
            password (str): web site password
            login_page_url (str): web page to go to for login prompt.
            pre_login_page_title (str): title for login_page_url.
            post_login_page_title (str): title of web page shown after logging in.
            username_field_xpath (str): xpath of field that takes username.
            password_field_xpath (str): xpath of field that takes password.
            login_button_xpath (str): xpath of button that starts login.
        Returns:
        """
        # Go to the login page.
        self.driver.get(login_page_url)

        # Wait for login page to appear.
        self.wait_for_refresh(BY_PAGE_TITLE, pre_login_page_title)

        # Enter login into login field.
        self.driver.find_element_by_xpath(username_field_xpath).send_keys(username)

        # Enter password into password field.
        self.driver.find_element_by_xpath(password_field_xpath).send_keys(password)

        # Click login button, wait for My Profile page to appear.
        self.click_sleep_wait(login_button_xpath, 0, BY_PAGE_TITLE, post_login_page_title)
    # End of method website_login.

    def go_to_web_page(self, web_page_url: str, method: str, identifier: str) -> None:
        """ Go to a web page.

        Parameters:
            web_page_url (str): URL of web page to go to.
            method (str): method to wait for refresh, BY_ID, BY_PAGE_TITLE, or BY_CLASS.
            identifier (str):
                method = BY_PAGE_TITLE, title of web page shown after logging in.
                method = BY_ID, HTML element ID.
                method = BY_CLASS, HTML element class.
        Returns:
        """
        if method not in {BY_ID, BY_CLASS, BY_PAGE_TITLE}:
            raise ValueError("Unknown Method.")

        # Go to web_page_url.
        self.driver.get(web_page_url)

        # Wait for page title to appear.
        self.wait_for_refresh(method, identifier)
    # End of method go_to_web_page.

    def get_related_by_class(self, class_name: str):
        """ Return HTML elements with a class name.

        Parameters:
            class_name (str): return all HTML elements with this class name.
        Returns:
            The HTML elements with this class name.
        """
        return self.driver.find_elements_by_class_name(class_name)

    def find_elements_by_xpath(self, xpath: str):
        """ Return HTML elements by xpath.

        Parameters:
            xpath (str): return all HTML elements with this class name.
        Returns:
            The HTML elements with this class name.
        """
        return self.driver.find_elements_by_xpath(xpath)
    # End of method find_related_by_class.
