from random import choice
import itertools
from typing import Literal
import logging

logger = logging.getLogger(__name__)


def squawk_code_2_int(squawk_code: str) -> int:
    squawk_int = 0
    for i, char in enumerate(squawk_code):
        squawk_int += int(char) << (3 * (3 - i))
    return squawk_int


def squawk_int_2_code(squawk_int: int) -> str:
    squawk_code = ''
    for i in range(4):
        squawk_code += str((squawk_int >> (3 * (3 - i))) & 0b111)
    return squawk_code


def choise_squawk_code_in_ranges(*ranges: tuple[int, int]):
    nums = list(
        itertools.chain(
            *(range(start, end) for start, end in ranges)
        )
    )
    return squawk_int_2_code(choice(nums))


def generate_taipei_fir_squawk_code(
    departure_airport: str,
    arrival_airport: str,
    flight_rule: Literal['I', 'V', 'Y', 'Z']
):
    is_departure_domestic = departure_airport.startswith('RC')
    is_arrival_domestic = arrival_airport.startswith('RC')
    is_international = is_departure_domestic + is_arrival_domestic == 1
    if flight_rule == 'V':
        return choise_squawk_code_in_ranges(
            (squawk_code_2_int('0601'), squawk_code_2_int('0677')),
        )
    elif is_international:
        return choise_squawk_code_in_ranges(
            (squawk_code_2_int('2601'), squawk_code_2_int('2777')),
            (squawk_code_2_int('6240'), squawk_code_2_int('6277')),
        )
    elif departure_airport in ('RCTP', 'RCSS', 'RCMQ', 'RCFG', 'RCMT', 'RCPO'):
        return choise_squawk_code_in_ranges(
            (squawk_code_2_int('4301'), squawk_code_2_int('4377')),
            (squawk_code_2_int('4401'), squawk_code_2_int('4477')),
            (squawk_code_2_int('4501'), squawk_code_2_int('4577')),
            (squawk_code_2_int('4601'), squawk_code_2_int('4677')),
        )
    elif departure_airport in ('RCBS', 'RCQC', 'RCCM', 'RCWA'):
        return choise_squawk_code_in_ranges(
            (squawk_code_2_int('2001'), squawk_code_2_int('2077')),
            (squawk_code_2_int('2101'), squawk_code_2_int('2177')),
        )
    elif departure_airport in ('RCKU', 'RCKH', 'RCNN',
                               'RCKW', 'RCSQ', 'RCDC',
                               'RCAY', 'RCSP', 'RCLM'):
        return choise_squawk_code_in_ranges(
            (squawk_code_2_int('1001'), squawk_code_2_int('1077')),
            (squawk_code_2_int('1101'), squawk_code_2_int('1177')),
        )
    elif departure_airport in ('RCYU', 'RCCS', 'RCFN',
                               'RCQS', 'RCLY ', 'RCGI'):
        return choise_squawk_code_in_ranges(
            (squawk_code_2_int('0301'), squawk_code_2_int('0377')),
            (squawk_code_2_int('1501'), squawk_code_2_int('1577')),
        )
    else:
        return choise_squawk_code_in_ranges(
            (squawk_code_2_int('0001'), squawk_code_2_int('6777'))
        )
