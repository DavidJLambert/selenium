""" MySelenium.py

SUMMARY: Use Selenium to watch for new online jobs on Wyzant.com.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.2.0

DATE: Jul 11, 2020
"""
from constants import BY_ID, BY_PAGE_TITLE, TIMEOUT
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
    """
    def __init__(self) -> None:
        """ Constructor method for this class.

        Parameters:
        Returns:
        """
        self.options = Options()
        self.options.headless = True
        self.options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(options=self.options)
    # End of method __init__.

    def wait_for_refresh(self, method: str, identifier: str) -> None:
        """ Make Selenium wait for web page to post.

        Parameters:
            method (str): method to wait for refresh, BY_ID or BY_PAGE_TITLE
            identifier (str): if method = BY_PAGE_TITLE, title of web page shown
                after logging in.  if method = BY_ID, HTML element ID.
        Returns:
        """
        try:
            if method == BY_PAGE_TITLE:
                WebDriverWait(self.driver, TIMEOUT).until(EC.title_is(identifier))
            elif method == BY_ID:
                WebDriverWait(self.driver, TIMEOUT).until(EC.visibility_of_element_located((By.ID, identifier)))
            else:
                raise ValueError("Method not BY_ID or BY_PAGE_TITLE.")
        except TimeoutException:
            print_stacktrace()
    # End of method wait_for_refresh.

    def click_sleep_wait(self, xpath: str, sleep_time: int, method: str, identifier: str) -> None:
        """ Click control and wait for expected web page title to appear.

        Parameters:
            xpath (str):  xpath of control.
            sleep_time (int): length of time to sleep, in seconds.
            method (str): method to wait for refresh, BY_ID or BY_PAGE_TITLE
            identifier (str): if method = BY_PAGE_TITLE, title of web page shown
                after logging in.  if method = BY_ID, HTML element ID.
        Returns:
        """
        if method not in {BY_ID, BY_PAGE_TITLE}:
            raise ValueError("Method not BY_ID or BY_PAGE_TITLE.")

        # Click control.
        self.driver.find_element_by_xpath(xpath).click()

        if sleep_time > 0:
            stdout.write("Sleeping for %d seconds.  " % sleep_time)
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
            method (str): method to wait for refresh, BY_ID or BY_PAGE_TITLE
            identifier (str): if method = BY_PAGE_TITLE, title of web page shown
                after logging in.  if method = BY_ID, HTML element ID.
        Returns:
        """
        if method not in {BY_ID, BY_PAGE_TITLE}:
            raise ValueError("Method not BY_ID or BY_PAGE_TITLE.")

        # Go to web_page_url.
        self.driver.get(web_page_url)

        # Wait for page title to appear.
        self.wait_for_refresh(method, identifier)
    # End of method go_to_web_page.

    def get_related_by_class(self, class_name: str):
        """ Return HTML elements with a class name.
            It is not worth the effort to encapsulate other HTML elements,
            so they are directly accessed in wyzant.old.py.

        Parameters:
            class_name (str): return all HTML elements with this class name.
        Returns:
            The HTML elements with this class name.
        """
        return self.driver.find_elements_by_class_name(class_name)
    # End of method find_related_by_class.
