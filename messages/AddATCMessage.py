from messages.IMessage import IMessage


class AddATCMessage(IMessage):
    command = '#AA'

    def __init__(self, source, destination, real_name, account, password, rating, protocol_version='B'):
        super().__init__()
        self.source = source
        self.destination = destination
        self.real_name = real_name
        self.account = account
        self.password = password
        self.rating = rating
        self.protocol_version = protocol_version

    @staticmethod
    def parse_raw_message(raw_message):
        [_command, source, destination, real_name, account, password,
            rating, protocol_version] = raw_message.split(':')
        return AddATCMessage(source, destination, real_name, account, password, rating, protocol_version)

    def __str__(self):
        return self.command + ':'.join([
            self.source,
            self.destination,
            self.real_name,
            self.account,
            self.password,
            self.rating,
            self.protocol_version
        ])
