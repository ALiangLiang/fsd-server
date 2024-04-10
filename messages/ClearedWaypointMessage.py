from messages.IMessage import IMessage


class ClearedWaypointMessage(IMessage):
    command = '=W'

    def __init__(self, source: str, destination: str, pilot: str, waypoint_name: str | None):
        super().__init__()
        self.source = source
        self.destination = destination
        self.pilot = pilot
        self.waypoint_name = waypoint_name

    @classmethod
    def parse_raw_message(cls, raw_message):
        source, destination, pilot, waypoint_name = raw_message[len(
            cls.command):].split(':')
        waypoint_name = waypoint_name.rstrip(
            ';') if waypoint_name != '' else None
        return cls(source, destination, pilot, waypoint_name)

    def __str__(self):
        return self.command + ':'.join([
            self.source,
            self.destination,
            self.pilot,
            self.waypoint_name if self.waypoint_name is not None else '',
        ])
