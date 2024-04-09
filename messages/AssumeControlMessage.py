from messages.IMessage import IMessage


class AssumeControlMessage(IMessage):
    command = '=A'

    def __init__(self, source: str, pilot: str):
        super().__init__()
        self.source = source
        self.pilot = pilot

    @classmethod
    def parse_raw_message(cls, raw_message):
        source, pilot = raw_message[len(cls.command):].split(':')
        return cls(source, pilot)

    def __str__(self):
        return self.command + ':'.join([
            self.source,
            self.pilot,
        ])
