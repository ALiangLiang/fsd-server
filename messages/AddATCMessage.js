const IMessage = require('./IMessage')

module.exports = class AddATCMessage extends IMessage {
  command = '#AA'

  constructor(source, destination, realName, account, password, rating, protocolVersion = 'B') {
    super()
    this.source = source
    this.destination = destination
    this.realName = realName
    this.account = account
    this.password = password
    this.rating = rating
    this.protocolVersion = protocolVersion
  }

  parseRawMessage(rawMessage) {
    const [_command, source, destination, realName, account, password, rating, protocolVersion] = rawMessage.split(':')
    return new AddATCMessage(source, destination, realName, account, password, rating, protocolVersion)
  }

  toString() {
    return this.command + [
      this.source,
      this.destination,
      this.realName,
      this.account,
      this.password,
      this.rating,
      this.protocolVersion
    ].join(':')
  }
}