""" Jobs.py

SUMMARY: Use Selenium to watch for new online jobs on Wyzant.com.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.1.0

DATE: Jul 3, 2020
"""
from MyConstants import *


class Jobs(object):
    """ Class containing job listing information.

    Attributes:
    """
    def __init__(self, job_location) -> None:
        """ Constructor method for this class.

        Parameters:
        Returns:
        """
        # Jobs
        self.jobs = dict()
        for job_location in JOB_LOCATIONS:
            self.jobs[job_location] = dict()

        # Job IDs
        self.job_ids = dict()
        for job_location in JOB_LOCATIONS:
            self.job_ids[job_location] = set()

        # Diff
        self.diff = dict()


