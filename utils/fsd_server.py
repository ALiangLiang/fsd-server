import asyncio
from datetime import timedelta
from logging import getLogger

from utils.fsd_controller import FsdController
from utils.connection import Connection
from utils.tick import Tick


TICK_INTERVAL = 2

logger = getLogger(__name__)


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
        self._tick = Tick(
            sec=TICK_INTERVAL,
            connections=self.connections,
            on_tick=self.on_tick,
            on_tick_connection=self.on_tick_connection,
        )
        self.Controller = Controller

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

    async def start(self):
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
        self._tick.start()

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
