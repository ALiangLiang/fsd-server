class IMessage:
    command = ''

    def __str__(self):
        raise NotImplementedError

    @staticmethod
    def parse_raw_message(raw_message):
        raise NotImplementedError
