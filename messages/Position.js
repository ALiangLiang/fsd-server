module.exports = class Position {
  constructor(latitude, longitude) {
    this.latitude = latitude
    this.longitude = longitude
  }

  static parseRawMessage(rawMessage) {
    const args = rawMessage.split(':')
    lat = args[0]
    lng = args[1]
    return new this(lat, lng)
  }

  toString() {
    return this.latitude + ':' + this.longitude
  }
}