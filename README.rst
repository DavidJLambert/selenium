=======================================
Using Selenium to Web Scrape wyzant.com
=======================================

:SUMMARY: Use Selenium to scrape wyzant.com for various types of information.

:REPOSITORY: https://github.com/DavidJLambert/Selenium

:AUTHOR: David J. Lambert

:VERSION: 0.5.7

:DATE: Aug 25, 2023

Problem Description
-------------------
I am a tutor on wyzant.com.  People who want a tutor can do one of two things:

- Post a request for a tutor, which shows up on https://www.wyzant.com/tutor/jobs.
- Go through tutor profiles and contact a specific tutor.

A lot of the time, people choose the first option, so I find most of my students
by looking at the tutor requests on https://www.wyzant.com/tutor/jobs.  In
order to find students on that web page, I have to regularly refresh that web
page, and I have to quickly respond to tutor requests, before that person
chooses another tutor and the request vanishes from that web page.

Program Description for wyzant_jobs.py
--------------------------------------
To make it easier for me to find tutoring students, I have created
wyzant_jobs.py, which uses the Python Selenium library to:

- Log into wyzant.com.
- Go to https://www.wyzant.com/tutor/jobs.
- Scrape a list of tutor requests (in topics I tutor) from that web page every 30 seconds.
- Compare the current list of tutor requests to the previously scraped list.
- Print the list of new tutor requests in standard output.
- And alert me to the presence of new tutor requests.

This program alerts me to the presence of each new tutor request by
- Making a "beep" sound.
- Printing the details of the new request.

Program Description for wyzant_testimonials.py
----------------------------------------------
Once wyzant_jobs.py alerts me to new tutoring opportunities, I can fill out a
form on wyzant.com telling each prospective student why I think I'm the best
tutor for them.

One part of this form allows me to select a recommendation made by a previous
student of mine.  Students can write recommendations for tutors.

Unfortunately, recommendations can only be found in the order they were created.
Each recommendation has a number associated with it, with the numbers being 1, 2,
3, et cetera, and the most recent recommendation being number 1.  As new
recommendations are created, the number for previous recommendations are
incremented to make room for the new recommendations.  Furthermore, some
recommendations appear more than once, and occasionally past recommendations 
vanish without explanation.

Thus, I wrote wyzant_testimonials.py to keep an inventory of all recommendations.
I keep this inventory in an Excel workbook, which includes which recommendation
to use for each topic I teach.

This workbook allows me to select a recommendation for each tutoring opportunity
in less than 30 seconds.

Program Description for wyzant_history.py
-----------------------------------------
I keep track of all the tutoring sessions I have ever delivered, along with
the:

- session date
- start time
- session length, in minutes
- date entered into wyzant.com
- the student name, city, and state
- the subject
- the student's rating of the session, if any
- the pay rate
- the dollar amount I earned
- the payment date

I wrote wyzant_history.py to copy this information from wyzant.com, and paste it
into an Excel workbook.

Program Description for wyzant_pricing.py, wyzant_pricing_detail.py, wyzant_search_topics.py, and pricing_gender.py
-------------------------------------------------------------------------------------------------------------------
I wrote these programs to log into wyzant.com as a student and to scrape information about each tutor in wyzant.com for
the subjects I tutor, so I could use the data to decide much I charge as a tutor.  These programs save the data in a
SQLite database.  pricing_gender.py does not scrape any web data, I use it to analyze some of the scraped data. 

PROGRAM REQUIREMENTS
--------------------

- The Python Selenium library.
- To make the beeping sound, the Beep function in the Python Standard Library module winsound.
