from messages.IMessage import IMessage


class PlaneInfoMessage(IMessage):
    command = '-PD'

    def __init__(self, source: str, destination: str, ident: str):
        super().__init__()
        self.source = source
        self.destination = destination
        self.ident = ident

    @classmethod
    def parse_raw_message(cls, raw_message):
        source, destination, ident = raw_message[len(cls.command):].split(':')
        return cls(source, destination, ident)

    def __str__(self):
        return self.command + ':'.join([
            self.source,
            self.destination,
            self.ident,
        ])
