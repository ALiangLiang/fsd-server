from messages.AssumeControlMessage import AssumeControlMessage


class ReleaseControlMessage(AssumeControlMessage):
    command = '=R'
