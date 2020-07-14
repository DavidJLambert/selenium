=======================================
Using Selenium to Web Scrape wyzant.com  
=======================================

:SUMMARY: Use Selenium to watch for new online jobs on wyzant.com.

:REPOSITORY: https://github.com/DavidJLambert/Selenium

:AUTHOR: David J. Lambert

:VERSION: 0.2.1

:DATE: DATE: Jul 14, 2020

PROBLEM DESCRIPTION
-------------------
I am a tutor on wyzant.com.  People who want a tutor can do one of two things:

- Post a request for a tutor, which shows up on https://www.wyzant.com/tutor/jobs.
- Go through tutor profiles and contact a specific tutor.

Most of the time, people choose the first option, so I find most of my students
by looking at the tutor requests on https://www.wyzant.com/tutor/jobs.  In
order to find students on that web page, I have to regularly refresh that web
page, and I have to quickly respond to tutor requests, before that person
chooses another tutor and the request vanishes from that web page.

PROGRAM DESCRIPTION
-------------------
To make it easier for me to find tutoring students, I have created this program.
Wyzant uses the Python Selenium library to:

- Log into wyzant.com.
- Go to https://www.wyzant.com/tutor/jobs.
- Scrape a list of tutor requests from that web page every 30 seconds.
- Compare the current list of tutor requests to the previously scraped list.
- Print the list of new tutor requests in standard output.
- And alert me to the presence of new tutor requests.

I am alerted to the presence of the new tutor requests in up to two ways which
I choose:

- Make a "beep" sound on the computer running wyzant.com.
- Email the tutor requests to David_J_lambert@outlook.com, which my smart phone receives.

PROGRAM REQUIREMENTS
--------------------

- The Python Selenium library.
- The Selenium Chromium driver, chromedriver.exe.
- The Python library Check_Chromedriver, to update chromedriver.exe to match Chrome's version. 
- To make the beeping sound, the Beep function in the Python Standard Library module winsound.
- To send the email, the Python Standard Library modules smtplib, ssl, and email.mime.text.
