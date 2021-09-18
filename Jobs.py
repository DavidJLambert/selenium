""" Jobs.py

SUMMARY: Use Selenium to watch for new online jobs on Wyzant.com.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.4.0

DATE: Sept 17, 2021
"""
import constants as c


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

    def __str__(self) -> str:
        """ Prints an instance.

        Parameters:
        Returns:
            Date in the dictionaries that contain jobs information, ordered ascending by age, then by Card #. 
        """
        output = ""
        for key, value in sorted(self.jobs.items(), key=lambda x: (x[1]['Age'], x[1]['Card #'])):
            output += str(value) + "\n"

        return output.strip()
    # End of method __str__.

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
            JOB_ID, CARD_NUMBER, APPLICATIONS, JOB_AGE, STUDENT_NAME, JOB_TOPIC, PAY_RATE, JOB_DESCRIPTION
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
        """  Find new job_id's in jobs but not jobs_prev.

        Parameters:
            job_ids_prev (set): jobs_prev.get_job_ids().
        Returns:
            new_job_ids (set): the new job_ids in self, but not in job_ids_prev.
        """
        job_ids_current = self.job_ids
        new_job_ids = job_ids_current.difference(job_ids_prev)
        '''
        job_ids_in_both = job_ids_current.intersection(job_ids_prev)
        # Find largest (newest) job_id in job_id_in_both.
        max_job_id_both = max(job_ids_in_both)
        # Find current job_id's with job_id > max_job_id_both
        new_job_ids = [job_id for job_id in job_ids_current
                       if job_id > max_job_id_both]
        '''
        return set(new_job_ids)
    # End of method get_new_job_ids.

    def get_job_data(self, job_data: str, job_id: str) -> (str, str, int):
        """  Extract job data from jobs[job_id], add to job_data.

        Parameters:
            job_data (str): job_ids.
            job_id (str): job_ids_prev.
        Returns:
            job_summary (str): summary of this job.
            job_data (str): all of the details of this job.
            age (int): the age of the job, in minutes.
        """
        for key in self.jobs[job_id].keys():
            value = self.jobs[job_id][key]
            job_data += f"('{job_id}', '{key}'): '{value}'\n"
        topic = self.jobs[job_id][c.JOB_TOPIC]
        subject = self.jobs[job_id]["Subject"]
        age = self.jobs[job_id]["Age"]
        job_summary = f"{c.JOB_TOPIC}: {topic}, Subject: {subject}"
        return job_summary, job_data, age
    # End of method get_job_data.

    def count_jobs(self) -> int:
        """  Count the number of jobs.

        Parameters:
        Returns:
            count (int): the number of jobs.
        """
        return len(self.job_ids)
    # End of method count_jobs.

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

# End of class Jobs.
