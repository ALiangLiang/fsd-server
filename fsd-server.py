import asyncio
import threading
import logging

import db.init
from messages.AddATCMessage import AddATCMessage
from messages.ATCPositionUpdateMessage import ATCPositionUpdateMessage
from messages.InformationRequestMessage import InformationRequestMessage, InformationCommand
from messages.InformationReplyMessage import InformationReplyMessage
from utils.aircraft_factory import AircraftFactory

logging.basicConfig(level=logging.DEBUG)
# logging.getLogger('aircrafts.aircrafts').setLevel(logging.INFO)


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
        logging.debug('Send msg to client: %s' % msg)
        try:
            self.transport.write((str(msg) + '\r\n').encode())
        except Exception as err:
            logging.error(err)

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
        raw_message = data.decode()
        major_command = raw_message[0]
        if major_command == '#':  # CommunicationMessage
            minor_command = raw_message[1:3]
            if minor_command == 'AT':
                logging.debug('Received ATISMessage')
            if minor_command == 'AC':
                logging.debug('Received ATISCancelMessage')
            elif minor_command == 'AA':
                logging.debug('Received AddATCMessage')
                message = AddATCMessage.parse_raw_message(raw_message)
                self.callsign = message.source
                logging.debug('callsign: %s' % self.callsign)
        elif major_command == '%':  # PositionUpdateMessage
            logging.debug('Received ATCPositionUpdateMessage')
            message = ATCPositionUpdateMessage.parse_raw_message(
                raw_message)
            self.callsign = message.callsign
        elif major_command == '$':  # AdministrativeMessage
            minor_command = raw_message[1:3]
            if minor_command == 'CQ':
                logging.debug('Received InformationRequestMessage')
                message = InformationRequestMessage.parse_raw_message(
                    raw_message)
                if message.sub_command == InformationCommand.FLIGHTPLAN.value:
                    callsign = message.fields[0]
                    aircraft = aircrafts.get(callsign)
                    if aircraft is None:
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
        elif major_command == '!':  # VerificationMessage
            minor_command = raw_message[1]
            if minor_command == 'S':
                logging.debug('Received ServerVerificationMessage')
            if minor_command == 'C':
                logging.debug('Received ClientVerificationMessage')
        else:
            logging.debug('Data received: %s' % raw_message)


factory = AircraftFactory()
aircrafts_list = [
    factory.generate_w_random_situation(),
    factory.generate_w_random_situation(),
    factory.generate_w_random_situation(),
    factory.generate_w_random_situation(),
    factory.generate_w_random_situation(),
    factory.generate_w_random_situation(),
    factory.generate_w_random_situation(),
    factory.generate_w_random_situation(),
    factory.generate_w_random_situation(),
    factory.generate_w_random_situation(),
]
aircrafts = {ac.callsign: ac for ac in aircrafts_list if ac is not None}
actived_clients: dict[str, Client] = {}


async def main():
    def send_all_aircraft_position():
        for aircraft in aircrafts.values():
            # arrived
            if len(aircraft.legs) == 0:
                aircrafts.pop(aircraft.callsign)
                continue

            position_update_message = aircraft.get_position_update_message()
            for client in actived_clients.values():
                client.send(str(position_update_message))
    t = set_interval(send_all_aircraft_position, 2)

    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: Client(),
        '0.0.0.0',
        6809
    )

    async with server:
        await server.serve_forever()
        logging.info('TCP Server start')

if __name__ == '__main__':
    asyncio.run(main())
