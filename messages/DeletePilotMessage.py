from messages.IMessage import IMessage


class DeletePilotMessage(IMessage):
    command = '#DP'

    def __init__(self, source: str):
        super().__init__()
        self.source = source

    @classmethod
    def parse_raw_message(cls, raw_message):
        source = raw_message[len(cls.command):].split(':')
        return cls(source)

    def __str__(self):
        return self.command + ':'.join([
            self.source,
        ])
