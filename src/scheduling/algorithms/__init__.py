"""CPU scheduling algorithms package.

Author signature: Eng Ahmed El-khatib
Pure Python - GUI-free.
"""

from scheduling.algorithms.fcfs import schedule_fcfs
from scheduling.algorithms.preemptive_priority import schedule_preemptive_priority
from scheduling.algorithms.priority import schedule_priority
from scheduling.algorithms.round_robin import schedule_round_robin
from scheduling.algorithms.sjf import schedule_sjf
from scheduling.algorithms.srtf import schedule_srtf

__all__ = [
    "schedule_fcfs",
    "schedule_sjf",
    "schedule_priority",
    "schedule_srtf",
    "schedule_round_robin",
    "schedule_preemptive_priority",
]
