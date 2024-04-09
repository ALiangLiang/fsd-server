from messages.IMessage import IMessage
from db.models import Waypoint


class ClearedWaypointMessage(IMessage):
    command = '=W'

    def __init__(self, source: str, destination: str, pilot: str, waypoint_name: Waypoint):
        super().__init__()
        self.source = source
        self.destination = destination
        self.pilot = pilot
        self.waypoint_name = waypoint_name

    @classmethod
    def parse_raw_message(cls, raw_message):
        source, destination, pilot, waypoint_name = raw_message[len(
            cls.command):].split(':')
        return cls(source, destination, pilot, waypoint_name.rstrip(';'))

    def __str__(self):
        return self.command + ':'.join([
            self.source,
            self.destination,
            self.pilot,
            self.waypoint_name,
        ])
