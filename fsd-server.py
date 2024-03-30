import asyncio
import socket
import time
from geopy.distance import Distance
from messages.Position import Position
from messages.Time import Time
from messages.FlightplanMessage import FlightplanMessage
from messages.PilotPositionUpdateMessage import PilotPositionUpdateMessage
from helpers import read_earth_fix, read_earth_nav, read_procedures, get_bearing_distance, fix_radial_distance

MY_CALLSIGN = 'XE_WL_OBS'
AC_CALLSIGN = 'CAL123'
SQUAWK_CODE = '4601'
GROUND_SPEED = 523  # km/h
ALTITUDE = 40571  # feet
PBH_TUPLE = [0, 0, 0, False]  # pitch, bank, heading, on ground
PRESSURE_DELTA = -1573
REMARK = 'PBN/A1B1C1D1L1O1S2 DOF/240327 REG/N891SB EET/RJJJ0030 RKRR0043 OPR/SIA PER/D RMK/TCAS SIMBRIEF'
ROUTE = 'CHAL1C CHALI T3 MKG W6 TNN TNN1J'
DEPARTURE_AIRPORT = 'RCTP'
ARRIVAL_AIRPORT = 'RCKH'


async def send(socket, msg):
    print('Send msg to client:', msg)
    socket.send((msg + '\r\n').encode())


async def send_flight_plan(socket):
    message = FlightplanMessage(
        AC_CALLSIGN,
        MY_CALLSIGN,
        'I',
        'S',
        '1/B738/H-SDE1E2E3FGHIJ2J3J4J5M1RWXY/LB1D1',
        'N0489',
        DEPARTURE_AIRPORT,
        Time(13, 35),
        Time(13, 35),
        'F390',
        ARRIVAL_AIRPORT,
        1,
        55,
        3,
        30,
        'RCMQ',
        REMARK,
        ROUTE
    )
    try:
        await send(socket, str(message))
    except Exception as err:
        print(err)
        # TODO: send Error Message


def flatten_list(irregular_list):
    return [element for item in irregular_list for element in flatten_list(item)] if type(irregular_list) is list else [irregular_list]


async def main():
    fixes = await read_earth_fix()
    navs = await read_earth_nav()
    dep_procedures = await read_procedures(DEPARTURE_AIRPORT, fixes)
    arr_procedures = await read_procedures(ARRIVAL_AIRPORT, fixes)
    LEGS = flatten_list(
        [fixes.get(leg) or
         navs.get(leg) or
         dep_procedures.get(leg, {}).get('navaids') or
         arr_procedures.get(leg, {}).get('navaids') for leg in ROUTE.split(' ')],
    )
    LEGS = [i for i in LEGS if i is not None]
    print('LEGS:', [leg['ident'] for leg in LEGS])

    async def tick_move_aircraft(client_socket):
        pos = Position(25.07282418224231, 121.21606845136498)
        last_time = time.time()
        current_leg_index = 0
        while True:
            bearing, distance_to_leg = get_bearing_distance(
                pos,
                LEGS[current_leg_index]['position']
            )
            now = time.time()
            time_diff = now - last_time
            last_time = now
            distance = Distance(meters=(GROUND_SPEED / 3.6)
                                * time_diff)  # meters

            print('move meters:', distance.meters)

            if distance_to_leg < distance:
                if current_leg_index == len(LEGS) - 1:
                    break
                current_leg_index += 1
                continue

            print('Next leg:', LEGS[current_leg_index]['ident'])

            pos = fix_radial_distance(pos, bearing, distance)

            message = PilotPositionUpdateMessage(
                AC_CALLSIGN,
                'N',
                SQUAWK_CODE,
                '4',
                pos,
                ALTITUDE,
                GROUND_SPEED,
                PBH_TUPLE,
                PRESSURE_DELTA
            )
            await send(client_socket, str(message))
            time.sleep(2)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 6809))
    server.listen(5)
    print('TCP Server start')

    while True:
        client_socket, address = server.accept()
        print('Connected to', address)
        await send_flight_plan(client_socket)
        await tick_move_aircraft(client_socket)

if __name__ == '__main__':
    asyncio.run(main())
