""" Jobs.py

SUMMARY: Use Selenium to watch for new online jobs on Wyzant.com.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.1.0

DATE: Jul 3, 2020
"""
import re
from MyConstants import *
# from MyFunctions import *


class Jobs(object):
    """ Class containing job listing information.

    Attributes:
        jobs, a collection of job info fetched from www.wyzant.com/tutor/jobs.
        job_ids, an instance of Class Job_IDs.
    """
    def __init__(self) -> None:
        """ Constructor method for this class.

        Parameters:
        Returns:
        """
        self.jobs = dict()
        self.job_ids = JobIDs()
    # End of method __init__.

    def reset(self) -> None:
        """ Reset jobs and job_ids.

        Parameters:
        Returns:
        """
        self.jobs = dict()
        self.job_ids.reset()
    # End of method reset.

    def add_job_id(self, new_job_id: str) -> None:
        """ Add new job_id to jobs.

        Parameters:
            new_job_id (str): new job_id to add to the collection of job_ids.
        Returns:
        """
        self.jobs[new_job_id] = dict()
    # End of method add_job_id.

    def add_properties(self, job_id: str, card_num: int, job_age: str,
                       student_name: str, job_topic: str, pay_rate: str,
                       job_description: str, **other_params: dict) -> None:
        """ Add properties to jobs for job_id.

        Parameters:
            job_id (str): job_id to add properties to.
            card_num (int): card_num to add to job_id.
            job_age (str): unprocessed job_age to add to job_id.
            student_name (str): student_name to add to job_id.
            job_topic (str): job_topic to add to job_id.
            pay_rate (str): unprocessed pay_rate to add to job_id.
            job_description (str): unprocessed job_description to add to job_id.
            other_params (dict): dictionary of parameters to add to job_id.
        Returns:
        """
        self.jobs[job_id][CARD_NUM] = card_num
        job_age = self.process_job_age(job_age)
        self.jobs[job_id][JOB_AGE] = job_age
        self.jobs[job_id][JOB_STUDENT_NAME] = student_name.strip()
        self.jobs[job_id][JOB_TOPIC] = job_topic.strip()
        pay_rate = self.process_pay_rate(pay_rate)
        self.jobs[job_id][JOB_PAY_RATE] = pay_rate
        job_description = self.process_job_description(job_description)
        self.jobs[job_id][JOB_DESCRIPTION] = job_description
        for key, value in other_params.items():
            self.jobs[job_id][key] = value
    # End of method add_properties.

    def get_new_job_ids(self, current: set, previous: set) -> set:
        """  Find job_id's in both job_ids[job_loc] and job_ids_prev[job_loc].

        Parameters:
            current (set): job_ids[job_loc].
            previous (set): job_ids_prev[job_loc].
        Returns:
            new_job_ids (set): the job IDs in current, but not in previous.
        """
        job_ids_in_both = current.intersection(previous)
        # Find smallest card_num ("cn") for job_id's in job_id_in_both.
        min_cn = [self.jobs[job_id][CARD_NUM] for job_id in job_ids_in_both]
        min_cn = min(min_cn)
        # Find job_id's with card_num's < min_cn.
        new_job_ids = [job_id for job_id in current if self.jobs[job_id][CARD_NUM] < min_cn]
        return set(new_job_ids)
    # End of method get_new_job_ids.

    def get_job_data(self, job_data: str, job_id: str, job_loc: str) -> str:
        """  Extract job data from jobs[job_id], add to job_data.

        Parameters:
            job_data (str): job_ids[job_loc].
            job_id (str): job_ids_prev[job_loc].
            job_loc (str): include in job_data.
        Returns:
            job_data (str): the job IDs in current, but not in previous.
        """
        for key in self.jobs[job_id].keys():
            value = self.jobs[job_id][key]
            job_data += "('%s', '%s', '%s'): '%s'\n" % (job_loc, job_id, key, value)
        return job_data
    # End of method get_job_data.

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
        re.sub("(\\r\\n){2,}", "\\r\\n", job_description.strip())
        re.sub("\\r{2,}", "\\r", job_description)
        re.sub("\\n{2,}", "\\n", job_description).strip()
        return job_description
    # End of method process_job_description.
# End of class Jobs.


class JobIDs(object):
    """ Class containing job listing information.

    Attributes:
        job_ids, a set of job IDs fetched from www.wyzant.com/tutor/jobs.
    """
    def __init__(self) -> None:
        """ Constructor method for this class.

        Parameters:
        Returns:
        """
        self.job_ids = set()
    # End of method __init__.

    def reset(self) -> None:
        """ Reset job_ids.

        Parameters:
        Returns:
        """
        self.job_ids = set()
    # End of method reset.

    def add_job_id(self, new_job_id: str) -> None:
        """ Add new job_id to collection of existing job_id's.

        Parameters:
            new_job_id (str): new job_id to add to the collection of job_ids.
        Returns:
        """
        self.job_ids.add(new_job_id)
    # End of method add_job_id.

    def count(self) -> int:
        """ Get number of job_ids.

        Parameters:
        Returns:
            count (int): the number of job_ids.
        """
        return len(self.job_ids)
    # End of method count.
# End of class JobIDs.


class NewJobIDs(object):
    """ Class containing job ID information.

    Attributes:
        new_job_ids (Job_IDs): new job_ids.
    """
    def __init__(self, current: set, previous: set, jobs: dict) -> None:
        """ Look for job IDs in current (job_ids) and not in previous (job_ids).

        Parameters:
            current (Job_IDs): the current list of job IDs fetched from www.wyzant.com/tutor/jobs.
            previous (Job_IDs): the previous list of jobs IDs fetched from www.wyzant.com/tutor/jobs.
            jobs (Jobs): the current list of jobs fetched from www.wyzant.com/tutor/jobs.
        Returns:
        """
        job_ids_in_both = current.intersection(previous)
        # Find smallest card_num for job_id's in job_id_in_both.
        min_card_num = [jobs[job_id][CARD_NUM] for job_id in job_ids_in_both]
        min_card_num = min(min_card_num)
        # Find job_id's with card_num's < min_card_num.
        new_job_ids = [job_id for job_id in current if jobs[job_id][CARD_NUM] < min_card_num]
        self.new_job_ids = set(new_job_ids)
    # End of method __init__.
# End of class NewJobIDs.
