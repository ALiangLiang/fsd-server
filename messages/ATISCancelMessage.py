from messages.IMessage import IMessage


class ATISCancelMessage(IMessage):
    command = '#AC'

    def __init__(self, source: str, destination: str):
        super().__init__()
        self.source = source
        self.destination = destination

    @classmethod
    def parse_raw_message(cls, raw_message):
        source, destination = raw_message[len(cls.command):].split(':')
        return cls(source, destination)

    def __str__(self):
        return self.command + ':'.join([
            self.source,
            self.destination,
        ])
