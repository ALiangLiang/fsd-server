from messages.IMessage import IMessage


class PlaneParamsMessage(IMessage):
    command = '-MD'

    def __init__(self, source: str, destination: str, params: int):
        super().__init__()
        self.source = source
        self.destination = destination
        self.params = params

    @classmethod
    def parse_raw_message(cls, raw_message):
        source, destination, params_str = raw_message[len(
            cls.command):].split(':')
        return cls(source, destination, int(params_str))

    def __str__(self):
        return self.command + ':'.join([
            self.source,
            self.destination,
            self.params,
        ])
