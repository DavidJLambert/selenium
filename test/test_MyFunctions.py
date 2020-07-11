from unittest import TestCase
from junk import functions as f
from constants import JOB_LOCATIONS, JOB_ONLINE, JOB_IN_PERSON
import pytest


from test.job_dict import jobs
from test.job_dict_prev import jobs_prev

# TODO for wyzant.py, not wyzant.py.


class Test(TestCase):
    def test_process_job_age(self):
        assert f.process_job_age("13m") == 13
        assert f.process_job_age("2h") == 2*60
        assert f.process_job_age("3d") == 3*24*60
        assert f.process_job_age("Jun 14") == 8*24*60

    def test_process_pay_rate(self):
        assert f.process_pay_rate("Recommended rate: None") is None
        assert f.process_pay_rate("Recommended rate: $19/hr") == 19

    def test_job_loc2xpath1(self):
        assert f.job_loc2xpath(JOB_ONLINE) == "//label[@for='lesson_type_online']"
        assert f.job_loc2xpath(JOB_IN_PERSON) == "//label[@for='lesson_type_in_person']"

    def test_job_loc2xpath2(self):
        with pytest.raises(ValueError) as exec_info:
            f.job_loc2xpath("Random string")
        assert str(exec_info.value) == "Unknown job location: 'Random string'."

    def test_get_new_job_ids(self):
        job_ids = dict()
        job_ids_prev = dict()
        for job_loc in JOB_LOCATIONS:
            job_ids[job_loc] = set(jobs[job_loc].keys())
            job_ids_prev[job_loc] = set(jobs_prev[job_loc].keys())
            new_job_ids = f.get_new_job_ids(job_ids[job_loc], job_ids_prev[job_loc], jobs[job_loc])
            if job_loc == JOB_ONLINE:
                assert new_job_ids == {'5938125'}
            if job_loc == JOB_IN_PERSON:
                assert new_job_ids == set()

    def test_get_job_data(self):
        pass
