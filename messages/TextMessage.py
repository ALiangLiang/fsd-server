from messages.IMessage import IMessage


class TextMessage(IMessage):
    command = '#TM'

    def __init__(self, source, destination, message):
        super().__init__()
        self.source = source
        self.destination = destination
        self.message = message

    @staticmethod
    def parse_raw_message(raw_message):
        source, destination, message = raw_message[len(
            TextMessage.command):].split(':')
        return TextMessage(source, destination, message)

    def __str__(self):
        return self.command + ":".join([
            self.source,
            self.destination,
            self.message.replace(':', '$C'),
        ])
