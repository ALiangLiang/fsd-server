const IMessage = require('./IMessage')

module.exports = class PilotPositionUpdateMessageex extends IMessage {
  command = '@'

  constructor(callsign, ident, squawkCode, rating, position, altitude, speed, pbh, pressureDelta) {
    super()
    this.callsign = callsign
    this.ident = ident
    this.squawkCode = squawkCode
    this.rating = rating
    this.position = position
    this.altitude = altitude
    this.speed = speed
    this.pbh = pbh
    this.pressureDelta = pressureDelta
  }

  static parseRawMessage(rawMessage) {
    throw new Error('Not implement')
  }

  tupleToPBH(pitch, bank, heading, onGround) {
    function scale(value) {
      return Math.floor((value + 360) % 360 * 2.8444444444444444444444444444);
    }

    const num = 1023;
    return (Math.floor(scale(pitch) & num))
      + (Math.floor(scale(bank) & num) << 10)
      + (heading = Math.floor(scale(heading) & num) << 21)
      + (onGround ? 2 : 0);
  }

  static pbhToTuple(value) {
    function unscale(value) {
      return value / 2.8444444444444444444444444444;
    }

    const num = 1023;
    return {
      Pitch: unscale((PBH >> 22) & 0xFFFF),
      Bank: unscale((PBH >> 12) & num),
      Heading: unscale((PBH >> 2) & num),
      OnGround: (PBH & 2) === 2
    };
  }

  toString() {
    return this.command + [
      this.ident,
      this.callsign,
      this.squawkCode,
      this.rating,
      this.position.toString(),
      this.altitude,
      this.speed,
      //this.tupleToPBH(...this.pbh),
      4261414408,
      this.pressureDelta
    ].join(':')
  }
}