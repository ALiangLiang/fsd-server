import threading
from datetime import datetime, timedelta

from utils.connection import Connection


def set_interval(func, sec: float, last_time: datetime):
    def func_wrapper():
        now = datetime.now()
        set_interval(func, sec, now)
        func(now - last_time)
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


class Tick:
    def __init__(
        self,
        sec: float,
        connections: dict[str, Connection],
        on_tick,
        on_tick_connection
    ) -> None:
        self.sec = sec
        self.connections = connections
        self.on_tick = on_tick
        self.on_tick_connection = on_tick_connection

    def start(self):
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
            self.sec,
            datetime.now()
        )
