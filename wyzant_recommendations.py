""" wyzant.py

SUMMARY: Use Selenium to watch for new online jobs on Wyzant.com.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.3.0

DATE: May 16, 2021
"""
from selenium.webdriver.common.by import By
import constants as c
from MySelenium import MySelenium

import csv
from sys import stdout
from time import sleep

SLEEP_TIME = 2  # Seconds.

topics = {'python': 'Python', 'sql': 'SQL', 'calculus': 'Calculus', 'web scraping':'Web Scraping', 'vba': 'VBA',
          'precalc': 'Pre-Calculus',
          'linux': 'Linux', 'ubuntu': 'Linux', 'unix': 'Linux', 'bash':'Linux',
          'code':'Coding', 'coding':'Coding', 'programming':'Coding', 'loop':'Coding'}
exact_topics = {'GRE'}


def main():
    """ Function main.  Get all recommendations.

    Parameters:
    Returns:
    """
    print(f"Sleep time {SLEEP_TIME} seconds.")

    # Log into Wyzant, go to starting web page.
    stdout.write("Initializing Selenium.\n")
    my_selenium = MySelenium()
    stdout.write("Done initializing Selenium.\n")
    stdout.write("Logging into Wyzant.\n")
    my_selenium.website_login(c.USERNAME, c.PASSWORD, c.LOGIN_PAGE_URL, c.PRE_LOGIN_PAGE_TITLE,
                              c.POST_LOGIN_PAGE_TITLE, c.USERNAME_FIELD_XPATH,
                              c.PASSWORD_FIELD_XPATH, c.LOGIN_BUTTON_XPATH)
    stdout.write("Done logging into Wyzant.\n")
    stdout.write("Going to the Wyzant job listings page.\n")
    my_selenium.go_to_web_page(c.JOBS_PAGE_URL, By.CLASS_NAME, c.UI_PAGE_LINK)
    stdout.write("At Wyzant job listings page.\n")

    # Go inside first job listing page.
    xpath = '//a[@class="job-details-link"]'
    page = my_selenium.find_elements_by_xpath(xpath)[0]
    page.click()
    sleep(SLEEP_TIME)

    stdout.write("At Wyzant job listing page.\n")

    with open('recommendations.csv', 'w', newline='') as output:
        csvwriter = csv.writer(output)

        # Heading row.
        row = ['Title', 'Body', 'Name', 'Sessions', 'Topics']
        print(row)
        csvwriter.writerow(row)

        # Loop over recommendations.
        keep_going = True
        while keep_going:
            previous_row = row
            row = []

            xpath = '//h5[@id="testimonial_title"]'
            testimonial_title = my_selenium.find_element_by_xpath(xpath).text
            row.append(testimonial_title)

            xpath = '//p[@id="testimonial_body"]'
            testimonial_body = my_selenium.find_element_by_xpath(xpath).text
            row.append(testimonial_body)

            xpath = '//span[@id="testimonial_student_name"]'
            testimonial_student = my_selenium.find_element_by_xpath(xpath).text
            row.append(testimonial_student)

            xpath = '//span[@id="testimonial_sessions"]'
            testimonial_sessions = my_selenium.find_element_by_xpath(xpath).text.split()[0]
            row.append(testimonial_sessions)

            # xpath of button to move to next recommendation.
            xpath = '//div[@id="testimonial_nav"]/a[text()="›"]'
            xpath2 = '//span[@id="testimonial_sessions"]'
            my_selenium.click_sleep_wait(xpath, SLEEP_TIME, c.BY_XPATH, xpath2)

            used_topics = set()
            # Search for topics, part 1.
            search_me = testimonial_title + ' ' + testimonial_body
            for topic in exact_topics:
                if topic in search_me:
                    used_topics.add(topic)
            # Search for topics, part 2.
            search_me = search_me.lower()
            for topic, TOPIC in topics.items():
                if topic in search_me:
                    used_topics.add(TOPIC)
            # Append topics to end of row.
            used_topics = ', '.join(used_topics)
            row.append(used_topics)

            if previous_row == row and row[2] != 'Hunter':
                # Repetitions means end of recommendations.
                keep_going = False
            else:
                # Write row to file and print.
                print(row)
                csvwriter.writerow(row)

# End of function main.


if __name__ == '__main__':
    main()
