import asyncio
import threading

import db.init
from aircrafts.b738 import B738
from messages.ATCPositionUpdateMessage import ATCPositionUpdateMessage
from messages.AddATCMessage import AddATCMessage
from messages.Position import Position
from utils.flightplan import Flightplan
from utils.physics import Speed
from helpers import (
    get_start_leg,
    get_sid_legs,
    get_star_legs,
    get_app_legs,
    get_fix_by_ident,
)


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


class Client(asyncio.Protocol):
    def __init__(self):
        self.transport = None
        self.callsign: str | None = None
        self.is_send_flightplan = False

    def send(self, msg: str):
        print('Send msg to client:', msg)
        try:
            self.transport.write((msg + '\r\n').encode())
        except Exception as err:
            print(err)

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

        actived_clients[peername] = self

    def connection_lost(self, exc: Exception | None) -> None:
        actived_clients.pop(
            self.transport.get_extra_info('peername')
        )

    def data_received(self, data):
        raw_message = data.decode()
        print('Data received:', raw_message)

        major_command = raw_message[0]
        if major_command == '#':
            minor_command = raw_message[1:2]
            if minor_command == 'AT':
                print('Received ATISMessage')
            elif minor_command == 'AA':
                print('Received AddATCMessage')
                message = AddATCMessage.parse_raw_message(raw_message)
                self.callsign = message.source
                print('callsign', self.callsign)
        elif major_command == '%':
            print('Received ATCPositionUpdateMessage')
            message = ATCPositionUpdateMessage.parse_raw_message(
                raw_message)
            self.callsign = message.callsign
            print('callsign', self.callsign)


actived_clients: dict[str, Client] = {}


async def main():
    clients = []
    aircrafts = [
        B738(
            callsign='CAL123',
            position=get_start_leg('RCTP', '05L').position,
            flightplan=Flightplan(
                departure_airport='RCTP',
                arrival_airport='RCKH',
                flight_rules='I',
                cruise_speed=Speed(mph=489),
                route='CHALI T3 MKG W6 TNN',
                cruise_altitude=200,

            ),
            sid_legs=get_sid_legs('RCTP', '05L', 'CHAL1C'),
            star_legs=get_star_legs('RCKH', 'TNN1J'),
            approach_legs=get_app_legs('RCKH', 'I09')[0]
        ),
        B738(
            callsign='CAL318',
            position=get_start_leg('RCTP', '05R').position,
            flightplan=Flightplan(
                departure_airport='RCTP',
                arrival_airport='RCQC',
                flight_rules='I',
                cruise_speed=Speed(mph=489),
                route='CHALI T3 AJENT',
                cruise_altitude=200,
            ),
            sid_legs=get_sid_legs('RCTP', '05R', 'CHAL1A'),
            approach_legs=get_app_legs(
                'RCQC', 'I02', transition_name='MASON')[0]
        ),
        B738(
            callsign='EVA737',
            position=get_fix_by_ident(
                'JAMMY', 'RC').position.set_altitude(37000),
            speed=Speed(mph=489),
            is_on_ground=False,
            flightplan=Flightplan(
                departure_airport='VHHH',
                arrival_airport='RCTP',
                flight_rules='I',
                cruise_speed=Speed(mph=489),
                route='OCEAN V3 ENVAR M750 TONGA',
                cruise_altitude=370,
            ),
            enroute_legs=[],
            approach_legs=get_app_legs(
                'RCTP', 'I05R', transition_name='JAMMY')[0]
        ),
    ]

    def send_all_aircraft_position():
        for aircraft in [*aircrafts]:
            # arrived
            if len(aircraft.legs) == 0:
                aircrafts.remove(aircraft)
                continue

            position_update_message = aircraft.get_position_update_message()
            for client in actived_clients.values():
                print()
                client.send(str(position_update_message))

                if client.is_send_flightplan == False and client.callsign is not None:
                    flightplan_message = aircraft.get_flightplan_message(
                        client.callsign
                    )
                    if flightplan_message is not None:
                        client.send(str(flightplan_message))
            for client in clients:
                if client.callsign is not None:
                    client.is_send_flightplan = True
    t = set_interval(send_all_aircraft_position, 2)

    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: Client(),
        '0.0.0.0',
        6809
    )

    async with server:
        await server.serve_forever()
        print('TCP Server start')

if __name__ == '__main__':
    asyncio.run(main())
