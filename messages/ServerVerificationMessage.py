from messages.IMessage import IMessage


class ServerVerificationMessage(IMessage):
    command = '!S'

    def __init__(self, source: str, destination: str, seed: int):
        super().__init__()
        self.source = source
        self.destination = destination
        self.seed = seed

    @staticmethod
    def parse_raw_message(raw_message):
        source, destination, seed = raw_message[len(
            ServerVerificationMessage.command):].split(':')
        return ServerVerificationMessage(source, destination, seed)

    def __str__(self):
        str1 = str(self.seed).zfill(9)
        length = len(str1)
        start_index = length - 9
        str2 = str1[start_index:length - start_index]
        return self.command + ":".join([
            self.source,
            self.destination,
            '1',
            str2,
        ])
