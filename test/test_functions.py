from unittest import TestCase
from varname import nameof

# Get test data and load into instances of Jobs.

from test.job_dict import jobs as jobs_dict
from test.job_dict_prev import jobs_prev as jobs_prev_dict

jobs_curr = dict()
for job_id, value_dict in jobs_dict.items():
    value_dict[c.JOB_ID] = job_id
    jobs.add_job(**value_dict)

jobs_prev = dict()
for job_id, value_dict in jobs_prev_dict.items():
    value_dict[c.JOB_ID] = job_id
    jobs_prev.add_job(**value_dict)


class Test(TestCase):
    def test_process_job_age(self):
        assert jobs.process_job_age("13m") == 13
        assert jobs.process_job_age("2h") == 2*60
        assert jobs.process_job_age("3d") == 3*24*60
        assert jobs.process_job_age("Jun 14") == 8*24*60

    def test_process_pay_rate(self):
        assert jobs.process_pay_rate("Recommended rate: None") is None
        assert jobs.process_pay_rate("Recommended rate: $19/hr") == 19

    def test_get_new_job_ids(self):
        new_job_ids = jobs.get_new_job_ids(jobs_prev.get_job_ids())
        assert new_job_ids == {'5938125'}

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
