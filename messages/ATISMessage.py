from messages.IMessage import IMessage


class ATISMessage(IMessage):
    command = '#AT'

    def __init__(self, source: str, destination: str, atis_revision: str, message: str):
        super().__init__()
        self.source = source
        self.destination = destination
        self.atis_revision = atis_revision
        self.message = message

    @classmethod
    def parse_raw_message(cls, raw_message):
        source, destination, atis_revision, message = raw_message[len(
            cls.command):].split(':')
        return cls(source, destination, atis_revision, message)

    def __str__(self):
        return self.command + ':'.join([
            self.source,
            self.destination,
            self.atis_revision,
            self.message,
        ])
