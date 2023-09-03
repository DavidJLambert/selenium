""" wyzant_testimonials.py

SUMMARY: Use Selenium to get all the testimonials.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.6.0

DATE: Sep 02, 2023
"""
# Web Browser independent Selenium imports.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

# Web Browser dependent Selenium code
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from wyzant_login import log_into_wyzant

# Other packages.
import csv

# CONSTANTS.

TIMEOUT = 30  # Seconds.

topics = {'python': 'Python',
          'sql': 'SQL',
          'calculus': 'Calculus',
          'web scraping': 'Web Scraping',
          'vba': 'VBA',
          'precalc': 'Pre-Calculus',
          'linux': 'Linux', 'ubuntu': 'Linux', 'unix': 'Linux', 'bash': 'Linux',
          'code': 'Coding', 'coding': 'Coding', 'programming': 'Coding', 'loop': 'Coding'}
exact_topics = {'GRE'}


def main():
    """ Function main.  Get all recommendations.

    Parameters:
    Returns:
    """
    # Selenium options.
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--window-size=1920,2200")

    # Connect to the Selenium web driver.
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Maximize the browser window.
    driver.maximize_window()

    print("Done initializing Selenium.")

    # Log into wyzant.
    driver = log_into_wyzant(driver)

    print("Going to the Wyzant job listings page.")

    driver.get("https://www.wyzant.com/tutor/jobs")
    WebDriverWait(driver, TIMEOUT).until(ec.visibility_of_element_located((By.CLASS_NAME, "ui-page-link")))

    print("At Wyzant job listings page.")

    # Go inside first job listing page.
    control = driver.find_elements(By.XPATH, '//a[@class="job-details-link"]')[0]
    control.click()
    WebDriverWait(driver, TIMEOUT).until(ec.visibility_of_element_located((By.ID, "testimonial_student_name")))

    print("In first Wyzant job listing page.")

    with open('./output/recommendations.csv', 'w', newline='') as output:
        csvwriter = csv.writer(output)

        # Heading row.
        row = ['Name', 'Sessions', 'Topics', 'Title', 'Body']
        csvwriter.writerow(row)
        row = '\t'.join(row)
        print(row)

        # Loop over recommendations.
        keep_going = True
        while keep_going:
            row = []

            # Student name.
            testimonial_student = driver.find_element(By.XPATH, '//span[@id="testimonial_student_name"]').text
            row.append(testimonial_student)

            # Number of sessions with student.
            testimonial_sessions = driver.find_elements(By.XPATH, '//span[@id="testimonial_sessions"]')
            if len(testimonial_sessions) > 0:
                testimonial_sessions = testimonial_sessions[0].text
                if len(testimonial_sessions) > 0:
                    row.append(testimonial_sessions.split()[0])
                else:
                    row.append('')
            else:
                row.append('')

            testimonial_titles = driver.find_elements(By.XPATH, '//h5[@id="testimonial_title"]')
            if len(testimonial_titles) > 0:
                testimonial_title = testimonial_titles[0].text
            else:
                testimonial_title = ''

            testimonial_body = driver.find_element(By.XPATH, '//p[@id="testimonial_body"]').text

            # xpath of button to move to next recommendation.
            # driver.find_element(By.XPATH, '//div[@id="testimonial_nav"]/a[text()="›"]').click()
            arrows = driver.find_elements(By.XPATH, '//a[text()="›"][not(contains(@class, "disabled"))]')
            if len(arrows) == 1:
                arrows[0].click()
            else:
                keep_going = False

            WebDriverWait(driver, TIMEOUT).until(ec.visibility_of_element_located((By.ID, "testimonial_student_name")))

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

            # Topics covered in the session.
            row.append(used_topics)

            # Testimonial title.
            row.append(testimonial_title)

            # Body of testimonial.
            row.append(testimonial_body)

            row_len = 0
            for item in row:
                row_len += len(item)

            if row_len > 0:
                # Write row to file and print.
                csvwriter.writerow(row)
                row = '\t'.join(row)
                print(row)

# End of function main.


if __name__ == '__main__':
    main()
