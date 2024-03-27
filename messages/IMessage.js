module.exports = class IMessage {
  command = ''
  static parseRawMessage() { throw new Error('Not implement') }
  toString() { throw new Error('Not implement') }
}