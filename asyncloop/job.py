import collections


PendingJob = collections.namedtuple('PendingJob', 'job_coro callback')
