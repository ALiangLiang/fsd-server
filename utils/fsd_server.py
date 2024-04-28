import asyncio
from datetime import timedelta, datetime
from logging import getLogger
import threading

from utils.fsd_controller import FsdController
from utils.connection import Connection


TICK_INTERVAL = 2

logger = getLogger(__name__)


def set_interval(func, sec: float, last_time: datetime):
    def func_wrapper():
        now = datetime.now()
        set_interval(func, sec, now)
        func(now - last_time)
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


class FsdServer:
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6809,
        Controller=FsdController
    ):
        self.host = host
        self.port = port
        self.connections: dict[str, Connection] = {}
        self.Controller = Controller

    def start_tick(self):
        def send_all_aircraft_position(after_time: timedelta):
            self.on_tick()

            # copy to avoid RuntimeError: dictionary changed size during iteration
            for conn in self.connections.values():
                self.on_tick_connection(conn, after_time)

                if conn.type != 'PILOT' or conn.aircraft is None:
                    continue

                aircraft = conn.aircraft
                position_update_message = aircraft.get_position_update_message()
                for connection in self.connections.values():
                    connection.send(str(position_update_message))
            # average 200 seconds to generate an new aircraft
            # if randint(0, 100) > 98:
            #     factory.generate_w_random_situation()
        return set_interval(
            send_all_aircraft_position,
            TICK_INTERVAL,
            datetime.now()
        )

    def _on_text_message(self, connection: Connection, raw_message: str):
        controller = self.Controller(connection, self.connections)
        for raw_message_row in raw_message.split('\r\n'):
            print('Data row received: %s' % raw_message_row)
            try:
                message = controller.route(raw_message_row)
                self.on_message(connection, message)
            except Exception as err:
                logger.exception(err)

    def _on_connection_made(self, connection: Connection):
        self.connections[connection.id] = connection
        self.on_connection_made(connection)

    def _on_lost_connection(self, connection: Connection):
        self.connections.pop(connection.id)

    async def serve(self):
        print(f"FSD Server started at {self.host}:{self.port}")
        loop = asyncio.get_running_loop()
        self._tcp_server = await loop.create_server(
            lambda: Connection(
                self._on_connection_made,
                self._on_lost_connection,
                self._on_text_message,
            ),
            self.host,
            self.port
        )
        self.start_tick()

        self.on_start()

        async with self._tcp_server:
            await self._tcp_server.serve_forever()

    def stop(self):
        print(f"FSD Server stopped at {self.host}:{self.port}")

    def on_start(self):
        pass

    def on_tick(self):
        pass

    def on_tick_connection(self, connection: Connection, after_time: timedelta):
        pass

    def on_connection_made(self, connection: Connection):
        pass

    def on_message(self, connection: Connection, message):
        pass
