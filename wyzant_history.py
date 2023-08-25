""" wyzant_history.py

SUMMARY: Use Selenium to get my entire tutoring history.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.5.7

DATE: Aug 25, 2023
"""
# Web Browser independent Selenium imports.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as ec

# Web Browser dependent Selenium code
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from wyzant_login import log_into_wyzant

# Other packages.
import csv
from time import sleep
from os import remove
import zipfile

# CONSTANTS.

TIMEOUT = 30  # Seconds.
SLEEP_TIME = 2  # Seconds.
FILE_NAME = './output/history'


def time_fmt(convert_me):
    hh_mm, am_pm = convert_me.split(" ")
    hh, mm = hh_mm.split(":")
    if am_pm == "AM":
        if hh == "12":
            hh = "00"
        elif len(hh) == 1:
            hh = "0" + hh
    else:
        if hh != "12":
            hh = str(int(hh) + 12)
    return hh + ":" + mm


def main():
    """ Function main.  Get all recommendations.

    Parameters:
    Returns:
    """
    # Get output format.
    while True:
        fmt = input("Enter 'c' for csv output, or 't' or press 'Enter' for tab-separated value output: ")
        extension = fmt.lower()
        if extension == 'c':
            extension = 'csv'
            delimiter = ','
        elif extension in ['t', '']:
            extension = 'tsv'
            delimiter = '\t'

        if extension in ['csv', 'tsv']:
            print(f"You chose {extension} format.")
            break
        else:
            print(f"'{fmt}' was not an option, doofus.")

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

    print("Going to the Wyzant lesson history page.")

    driver.get("https://www.wyzant.com/tutor/lessons")
    this_id = "ctl00_ctl00_PageCPH_CenterColumnCPH_LessonDisplay1_ListViewSession_Pager_NextPageBTN"
    WebDriverWait(driver, TIMEOUT).until(ec.visibility_of_element_located((By.ID, this_id)))

    print("At Wyzant tutoring history page.")

    # Click the "Show All" link.
    show_all = driver.find_element(By.ID, value='ctl00_ctl00_PageCPH_CenterColumnCPH_LessonDisplay1_btnShowAll')
    sleep(SLEEP_TIME)
    show_all.click()
    sleep(SLEEP_TIME)

    # Select 200 entries per page.
    this_id = 'ctl00_ctl00_PageCPH_CenterColumnCPH_LessonDisplay1_ListViewSession_Pager_DDPageSize'
    per_page = Select(driver.find_element(By.ID, value=this_id))
    per_page.select_by_value("200")
    sleep(5)

    print("In first Wyzant history page.")

    with open(FILE_NAME + extension, 'w', newline='') as output:
        csvwriter = csv.writer(output, delimiter=delimiter)

        # Heading row.
        row = ['Date', 'Time', 'Min', 'Hrs', 'Entered', 'Online', 'Student', 'Subject', 'Rating',
               'Rate', 'Pay', 'Earned', 'Miles', 'Payment', 'Status']
        if extension == 'csv':
            print(row)
        else:
            print(delimiter.join(row))
        csvwriter.writerow(row)

        # Go to every page in the history
        while True:

            # Get table tbody.
            t_body = driver.find_element(By.XPATH, '//tbody')

            # Find all rows in tbody and iterate over them.
            t_rows = t_body.find_elements(By.XPATH, './tr')
            for t_row in t_rows:
                row = []

                # Find cells in the current row.
                t_cells = t_row.find_elements(By.XPATH, './td')

                # Cell  0 "Date", date and time
                # date
                value = t_cells[0].find_element(By.XPATH, './span[1]/span[1]').text.strip()
                row.append(value)
                # time
                value = t_cells[0].find_element(By.XPATH, './span[2]').text.strip()
                row.append(time_fmt(value))
                # Cell  1 "Minutes"
                value = t_cells[1].text.strip()[:-4]
                row.append(value)
                # Cell  2 "Hours"
                value = str(int(value)/60)
                row.append(value)
                # Cell  3 "Entered" date
                value = t_cells[2].find_element(By.XPATH, './span/span[1]').text.strip()
                row.append(value)
                # Cell  4 "Online" yes/no
                value = t_cells[3].text.strip()
                row.append(value)
                # Cell  5 "Student" name and location
                name = t_cells[4].find_element(By.XPATH, './span/a').text.strip()
                location = t_cells[4].find_element(By.XPATH, './span/span').text.strip()
                row.append(name + ", " + location)
                # Cell  6 "Subject"
                value = t_cells[5].text.strip()
                row.append(value)
                # Cell  7 "Rating", "No Rating" or 1-5 stars
                value = t_cells[6].text.strip()
                if value == "":
                    xpath = './div/span[contains(@class, "wc-yellow")]'
                    value = t_cells[6].find_elements(By.XPATH, xpath)
                    value = str(len(value))
                else:
                    value = "None"
                row.append(value)
                # Cell  8 "Rate", $/hr
                value = t_cells[7].text.strip()[1:-3]
                row.append(value)
                # Cell  9 "Pay", always 75%?
                value = t_cells[8].text.strip()[:-1]
                row.append(value)
                # Cell 10 "Earned" $
                value = t_cells[9].text.strip()[1:]
                row.append(value)
                # Cell 11 "Mileage" blank or "<N> miles"
                value = t_cells[10].text.strip()
                if value != "":
                    value = value[:-6]
                row.append(value)
                # Cell 12 "Payment" date
                value = t_cells[11].find_element(By.XPATH, './a/span/span[1]').text.strip()
                row.append(value)
                # Cell 13 "Status", "complete" or "void"
                value = t_cells[12].find_element(By.XPATH, './a').text.strip()
                row.append(value)

                # Save row.
                if extension == 'csv':
                    print(row)
                else:
                    print(delimiter.join(row))
                csvwriter.writerow(row)

            # xpath of ">" link to move to next page.
            # xpath = '//a[@id="ctl00_ctl00_PageCPH_CenterColumnCPH_LessonDisplay1_ListViewSession_Pager_NextPageBTN"]'
            # next_page = driver.find_element(By.XPATH, xpath)
            # class_ = next_page.get_attribute("class").strip()

            # if class_ == "":
            #    next_page.click()
            #    sleep(5)
            # else:
            #     break

            break

    # Compress the output file.
    with zipfile.ZipFile(FILE_NAME + '.zip', compression=zipfile.ZIP_DEFLATED, mode='w') as x:
        x.write(FILE_NAME + extension, compresslevel=9)

    # Delete csv file.
    remove(FILE_NAME + extension)
# End of function main.


if __name__ == '__main__':
    main()
