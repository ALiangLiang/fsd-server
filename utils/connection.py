import asyncio
from asyncio.transports import BaseTransport
import logging
from typing import Literal

from aircrafts.aircraft import Aircraft
from messages.TextMessage import TextMessage
from messages.IMessage import IMessage
from utils.leg import Leg


class Connection(asyncio.Protocol):
    def __init__(self, _on_connection_made, _on_lost_connection, _on_message):
        self.id = None
        self.transport: BaseTransport = None
        self.callsign: str | None = None
        self.type: Literal['ATC', 'PILOT'] = 'PILOT'
        self.frequency: str | None = None
        self.aircraft: Aircraft | None = None
        self.is_send_flightplan = False
        self.user = None
        self._on_connection_made = _on_connection_made
        self._on_lost_connection = _on_lost_connection
        self._on_message = _on_message

    def send(self, msg: str | IMessage):
        # logging.debug('Send msg to connection: %s' % msg)
        try:
            if self.transport is None:
                return
            self.transport.write((str(msg) + '\r\n').encode())
        except Exception as err:
            logging.exception(err)

    def send_text(self, target: str, msg: str):
        return self.send(
            TextMessage(
                self.callsign,
                target,
                msg
            ).__str__()
        )

    def send_text_to_channel(self, msg: str):
        return self.send_text(self.frequency, msg)

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        logging.info('Connection from %s:%s' % peername)
        self.id = peername
        self.transport = transport

        self._on_connection_made(self)

    def connection_lost(self, exc):
        self._on_lost_connection(self)

    def data_received(self, data):
        self._on_message(self, data.decode().rstrip())

    def find_leg_by_ident(self, legs: list[Leg], ident: str):
        for l in legs:
            if l.fix is None:
                continue
            if l.fix.ident == ident:
                return l
        return None
