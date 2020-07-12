import functions as f
import constants as c
from Jobs import Jobs

from unittest import TestCase
import pytest
from varname import nameof

# Get test data and load into instances of Jobs.

from test.job_dict import jobs as jobs_dict
from test.job_dict_prev import jobs_prev as jobs_prev_dict

jobs = dict()
for job_loc in jobs_dict.keys():
    jobs[job_loc] = Jobs()
    for job_id, value_dict in jobs_dict[job_loc].items():
        value_dict[c.JOB_ID] = job_id
        jobs[job_loc].add_job(**value_dict)

jobs_prev = dict()
for job_loc in jobs_prev_dict.keys():
    jobs_prev[job_loc] = Jobs()
    for job_id, value_dict in jobs_prev_dict[job_loc].items():
        value_dict[c.JOB_ID] = job_id
        jobs_prev[job_loc].add_job(**value_dict)


class Test(TestCase):
    def test_process_job_age(self):
        assert jobs[c.JOB_ONLINE].process_job_age("13m") == 13
        assert jobs[c.JOB_ONLINE].process_job_age("2h") == 2*60
        assert jobs[c.JOB_ONLINE].process_job_age("3d") == 3*24*60
        assert jobs[c.JOB_ONLINE].process_job_age("Jun 14") == 8*24*60

    def test_process_pay_rate(self):
        assert jobs[c.JOB_ONLINE].process_pay_rate("Recommended rate: None") is None
        assert jobs[c.JOB_ONLINE].process_pay_rate("Recommended rate: $19/hr") == 19

    def test_job_loc2xpath1(self):
        assert f.job_loc2xpath(c.JOB_ONLINE) == "//label[@for='lesson_type_online']"
        assert f.job_loc2xpath(c.JOB_IN_PERSON) == "//label[@for='lesson_type_in_person']"

    def test_job_loc2xpath2(self):
        with pytest.raises(ValueError) as exec_info:
            f.job_loc2xpath("Random string")
        assert str(exec_info.value) == "Unknown job location: 'Random string'."

    def test_get_new_job_ids(self):
        for job_loc1 in c.JOB_LOCATIONS:
            new_job_ids = jobs[job_loc1].get_new_job_ids(jobs_prev[job_loc1].get_job_ids())
            if job_loc1 == c.JOB_ONLINE:
                assert new_job_ids == {'5938125'}
            if job_loc1 == c.JOB_IN_PERSON:
                assert new_job_ids == set()

    def test_nested_print(self):
        snarg = dict()
        snarg[100] = 300
        snarg["AA"] = "BB"
        piffle = dict()
        piffle[10] = 30
        piffle["A"] = "B"
        piffle["C"] = snarg
        blarvitz = dict()
        blarvitz[1] = 3
        blarvitz["a"] = "b"
        blarvitz["c"] = piffle
        assert(f.nested_print(nameof(blarvitz), blarvitz)) == '''blarvitz[1] = 3
blarvitz["a"] = "b"
blarvitz["c"] = dict()
blarvitz["c"][10] = 30
blarvitz["c"]["A"] = "B"
blarvitz["c"]["C"] = dict()
blarvitz["c"]["C"][100] = 300
blarvitz["c"]["C"]["AA"] = "BB"
'''
