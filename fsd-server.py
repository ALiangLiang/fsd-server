import asyncio
import threading
import logging
from datetime import datetime, timedelta
from random import randint

from geopy.distance import Distance

import db.init
from messages.AddATCMessage import AddATCMessage
from messages.ATCPositionUpdateMessage import ATCPositionUpdateMessage
from messages.ClearedFlightlevelMessage import ClearedFlightlevelMessage
from messages.ClearedSpeedMessage import ClearedSpeedMessage
from messages.ClearedWaypointMessage import ClearedWaypointMessage
from messages.InformationRequestMessage import InformationRequestMessage, InformationCommand
from messages.InformationReplyMessage import InformationReplyMessage
from messages.TextMessage import TextMessage
from utils.aircraft_factory import AircraftFactory
from utils.leg import Leg

logging.basicConfig(level=logging.DEBUG)
# logging.getLogger('aircrafts.aircrafts').setLevel(logging.INFO)


def set_interval(func, sec: float, last_time: datetime):
    def func_wrapper():
        now = datetime.now()
        set_interval(func, sec, now)
        func(now - last_time)
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


class Client(asyncio.Protocol):
    def __init__(self):
        self.transport = None
        self.callsign: str | None = None
        self.frequency: str | None = None
        self.is_send_flightplan = False

    def send(self, msg: str):
        logging.debug('Send msg to client: %s' % msg)
        try:
            self.transport.write((str(msg) + '\r\n').encode())
        except Exception as err:
            logging.error(err)

    def send_text(self, target: str, msg: str):
        return self.send(
            TextMessage(
                self.callsign,
                target,
                msg
            )
        )

    def send_text_to_channel(self, msg: str):
        return self.send_text(self.frequency, msg)

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        logging.info('Connection from %s:%s' % peername)
        self.transport = transport

        actived_clients[peername] = self

    def connection_lost(self, exc: Exception | None) -> None:
        actived_clients.pop(
            self.transport.get_extra_info('peername')
        )

    def data_received(self, data):
        raw_message = data.decode().rstrip()
        for raw_message_row in raw_message.split('\r\n'):
            print('Data row received: %s' % raw_message_row)
            self.handle_raw_message(raw_message_row)

    def find_leg_by_ident(self, legs: list[Leg], ident: str):
        for l in legs:
            if l.fix is None:
                continue
            if l.fix.ident == ident:
                return l
        return None

    def handle_raw_message(self, raw_message: str):
        major_command = raw_message[0]
        if major_command == '#':  # CommunicationMessage
            minor_command = raw_message[1:3]
            if minor_command == 'AT':
                logging.debug('Received ATISMessage')
            if minor_command == 'AC':
                logging.debug('Received ATISCancelMessage')
            elif minor_command == 'AA':
                message = AddATCMessage.parse_raw_message(raw_message)
                self.callsign = message.source
                logging.debug('callsign: %s' % self.callsign)
        elif major_command == '%':  # PositionUpdateMessage
            logging.debug('Received ATCPositionUpdateMessage')
            message = ATCPositionUpdateMessage.parse_raw_message(
                raw_message)
            self.callsign = message.callsign
            self.frequency = message.frequency
        elif major_command == '$':  # AdministrativeMessage
            minor_command = raw_message[1:3]
            if minor_command == 'CQ':
                logging.debug('Received InformationRequestMessage')
                message = InformationRequestMessage.parse_raw_message(
                    raw_message)
                if message.sub_command == InformationCommand.FLIGHTPLAN.value:
                    callsign = message.fields[0]
                    aircraft = factory.aircrafts.get(callsign)
                    if aircraft is None and self.callsign is not None:
                        return
                    self.send(
                        aircraft.get_flightplan_message(self.callsign)
                    )
                elif message.sub_command == InformationCommand.NAME.value:
                    self.send(
                        InformationReplyMessage(
                            message.destination,
                            message.source,
                            InformationCommand.NAME.value,
                            ['A bot', 'USER', '4']
                        )
                    )
                elif message.sub_command == InformationCommand.ATIS.value:
                    # TODO: send ATIS message back
                    pass
        elif major_command == '=':  # ClearanceMessage
            minor_command = raw_message[1]
            if minor_command == 'A':
                self.send(raw_message)
            if minor_command == 'R':
                self.send(raw_message)
            if minor_command == 'W':
                message = ClearedWaypointMessage.parse_raw_message(raw_message)
                aircraft = factory.aircrafts.get(message.pilot)
                if aircraft is None:
                    return
                found_leg = self.find_leg_by_ident(
                    aircraft.legs,
                    message.waypoint_name
                )
                if found_leg is None:
                    self.send(
                        aircraft.get_text_message(
                            self.frequency,
                            'Unable, %s not in our route' % message.waypoint_name
                        )
                    )
                    return
                aircraft.direct_to_leg(found_leg)
                self.send(
                    aircraft.get_text_message(
                        self.frequency,
                        'Direct to %s, %s' % (
                            found_leg.ident,
                            aircraft.callsign
                        )
                    )
                )
            if minor_command == 'S':
                message = ClearedSpeedMessage.parse_raw_message(raw_message)
                aircraft = factory.aircrafts.get(message.pilot)
                if aircraft is None:
                    return
                aircraft.set_speed_limit(message.speed)
                action = 'Reduce' if aircraft.speed > aircraft.speed_limit else 'Increase'
                instrucment = '%s speed to %d knots' % (
                    action, message.speed.knots)
                self.send_text_to_channel(
                    '%s, %s' % (aircraft.callsign, instrucment)
                )
                self.send(
                    aircraft.get_text_message(
                        self.frequency,
                        '%s, %s' % (instrucment, aircraft.callsign)
                    )
                )
            if minor_command == 'F':
                message = ClearedFlightlevelMessage.parse_raw_message(
                    raw_message)
                aircraft = factory.aircrafts.get(message.pilot)
                if aircraft is None:
                    return
                aircraft.set_target_altitude(message.flight_level)
                target_altitude: Distance = aircraft.target_altitude
                action = 'Decend' if aircraft.position.altitude_ > target_altitude else 'Climb'
                altitude_str = f'FL{int(target_altitude.feet // 100)}' if \
                    target_altitude > Distance(feet=13000) else \
                    f'{int(target_altitude.feet)}ft'
                instrucment = '%s and maintain %s' % (action, altitude_str)
                self.send_text_to_channel(
                    '%s, %s' % (aircraft.callsign, instrucment)
                )
                self.send(
                    aircraft.get_text_message(
                        self.frequency,
                        '%s, %s' % (instrucment, aircraft.callsign)
                    )
                )
        elif major_command == '!':  # VerificationMessage
            minor_command = raw_message[1]
            if minor_command == 'S':
                logging.debug('Received ServerVerificationMessage')
            if minor_command == 'C':
                logging.debug('Received ClientVerificationMessage')
        else:
            logging.debug('Data received: %s' % raw_message)


NUMBER_OF_AIRCRAFTS = 10
factory = AircraftFactory()
for i in range(NUMBER_OF_AIRCRAFTS):
    factory.generate_w_random_situation()
actived_clients: dict[str, Client] = {}


async def main():
    def send_all_aircraft_position(after_time: timedelta):
        for aircraft in factory.aircrafts.values():
            # arrived
            if aircraft.is_no_more_legs:
                factory.aircrafts.pop(aircraft.callsign)
                for client in actived_clients.values():
                    client.send(aircraft.get_delete_message())
                continue

            aircraft.update_status(after_time)
            position_update_message = aircraft.get_position_update_message()
            for client in actived_clients.values():
                client.send(str(position_update_message))
        # average 200 seconds to generate an new aircraft
        if randint(0, 100) > 90:
            factory.generate_w_random_situation()
    t = set_interval(send_all_aircraft_position, 2, datetime.now())

    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: Client(),
        '0.0.0.0',
        6809
    )
    logging.info('TCP Server created')

    async with server:
        await server.serve_forever()
        logging.info('TCP Server start')

if __name__ == '__main__':
    asyncio.run(main())
