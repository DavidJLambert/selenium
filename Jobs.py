""" Jobs.py

SUMMARY: Use Selenium to watch for new online jobs on Wyzant.com.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.2.2

DATE: Jul 15, 2020
"""
import constants as c
import re


class Jobs(object):
    """ Class containing job listing information.

    Attributes:
        jobs, a collection of job info fetched from www.wyzant.com/tutor/jobs.
        job_ids, a set of job IDs.
    """
    def __init__(self) -> None:
        """ Constructor method for this class.

        Parameters:
        Returns:
        """
        self.jobs = dict()
        self.job_ids = set()
    # End of method __init__.

    def reset(self) -> None:
        """ Reset jobs and job_ids.

        Parameters:
        Returns:
        """
        self.jobs = dict()
        self.job_ids = set()
    # End of method reset.

    def add_job(self, **params: dict) -> None:
        """ Add new job to jobs.

        Parameters:
            params (dict): dictionary of parameters to add to job_id.
        Required elements of params:
            JOB_ID, CARD_NUMBER, JOB_AGE, STUDENT_NAME, JOB_TOPIC, PAY_RATE, JOB_DESCRIPTION
        Optional elements of params:
            "Availability", "Lesson frequency", "Location", "Preferred lesson location",
            "Student grade level", "Subject", "Timezone", "Tutoring goals", "Would like lessons to begin".
        Returns:
        """
        job_id = params[c.JOB_ID]
        self.jobs[job_id] = dict()
        self.job_ids.add(job_id)

        for key, value in params.items():
            self.jobs[job_id][key] = value
    # End of method add_properties.

    def get_job_ids(self) -> set:
        """  Find job_id's in both job_ids and job_ids_prev.

        Parameters:
        Returns:
            job_ids (set): the job_ids.
        """
        return self.job_ids
    # End of method get_job_ids.

    def get_new_job_ids(self, job_ids_prev: set) -> set:
        """  Find job_id's in both jobs and jobs_prev.

        Parameters:
            job_ids_prev (set): jobs_prev.get_job_ids().
        Returns:
            new_job_ids (set): the job_ids in self, but not in job_ids_prev.
        """
        job_ids_current = self.job_ids
        job_ids_in_both = job_ids_current.intersection(job_ids_prev)
        # Find smallest card_num ("min_cn") for job_id's in job_id_in_both.
        min_cn = [self.jobs[job_id][c.CARD_NUMBER] for job_id in job_ids_in_both]
        min_cn = min(min_cn)
        # Find job_id's with card_num's < min_cn.
        new_job_ids = [job_id for job_id in job_ids_current
                       if self.jobs[job_id][c.CARD_NUMBER] < min_cn]
        return set(new_job_ids)
    # End of method get_new_job_ids.

    def get_job_data(self, job_data: str, job_id: str) -> str:
        """  Extract job data from jobs[job_id], add to job_data.

        Parameters:
            job_data (str): job_ids.
            job_id (str): job_ids_prev.
        Returns:
            job_data (str): the job IDs in current, but not in previous.
        """
        for key in self.jobs[job_id].keys():
            value = self.jobs[job_id][key]
            job_data += "('%s', '%s'): '%s'\n" % (job_id, key, value)
        return job_data
    # End of method get_job_data.

    def count_job_ids(self) -> int:
        """  Count the number of job_id's.

        Parameters:
        Returns:
            count (int): the number of job_ids.
        """
        return len(self.job_ids)
    # End of method count_job_ids.

    @staticmethod
    def process_job_age(job_age: str) -> int:
        """ Process the age of a job listing.

        Parameters:
            job_age (str): the age of a job listing.
        Returns:
            job_age (int): the age of a job listing, in minutes.
        """
        last_char = job_age.strip()[-1]
        if last_char == "m":
            job_age = int(job_age[:-1])
        elif last_char == "h":
            job_age = 60 * int(job_age[:-1])
        elif last_char == "d":
            job_age = 24 * 60 * int(job_age[:-1])
        else:
            job_age = 8 * 24 * 60
        return job_age
    # End of method process_job_age.

    @staticmethod
    def process_pay_rate(pay_rate: str) -> int:
        """ Process the pay rate of a job listing.

        Parameters:
            pay_rate (str): the pay rate of a job listing.
        Returns:
            pay_rate (int): the pay rate of a job listing.
        """
        pay_rate = pay_rate.replace("Recommended rate: ", "")
        pay_rate = pay_rate.replace("/hr", "")
        pay_rate = pay_rate.replace("$", "").strip()
        if pay_rate == "None":
            pay_rate = None
        else:
            pay_rate = int(pay_rate)
        return pay_rate
    # End of method process_job_age.

    @staticmethod
    def process_job_description(job_description: str) -> str:
        """ Process the job description of a job listing.

        Parameters:
            job_description (str): the job_description of a job listing.
        Returns:
            job_description (str): the job_description of a job listing.
        """
        return re.sub("\n{2,}", "\n", job_description.strip())
    # End of method process_job_description.
# End of class Jobs.
