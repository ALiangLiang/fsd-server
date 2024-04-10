from messages.IMessage import IMessage
from utils.physics import Speed


class ClearedSpeedMessage(IMessage):
    command = '=S'

    def __init__(self, source: str, destination: str, pilot: str, speed: Speed | None):
        super().__init__()
        self.source = source
        self.destination = destination
        self.pilot = pilot
        self.speed = speed

    @classmethod
    def parse_raw_message(cls, raw_message):
        source, destination, pilot, speed_str = raw_message[len(
            cls.command):].split(':')
        speed = Speed(knots=int(speed_str)) if speed_str != '' else None
        return cls(source, destination, pilot, speed)

    def __str__(self):
        return self.command + ':'.join([
            self.source,
            self.destination,
            self.pilot,
            int(self.speed.knots) if self.speed is not None else '',
        ])
