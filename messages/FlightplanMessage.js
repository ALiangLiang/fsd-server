const IMessage = require('./IMessage')

module.exports = class FlightplanMessage extends IMessage {
  command = '$FP'

  constructor(
    source,
    destination,
    flightRules,
    typeOfFlight,
    aircraftType,
    cruiseSpeed,
    departureAirport,
    estimatedDeparture,
    actualDeparture,
    cruiseAlt,
    arrivalAirport,
    hoursEnRoute,
    minitesEnroute,
    hoursFuel,
    minutesFuel,
    alternateAirport,
    remarks,
    route
  ) {
    super()
    this.source = source
    this.destination = destination
    this.flightRules = flightRules
    this.typeOfFlight = typeOfFlight
    this.aircraftType = aircraftType
    this.cruiseSpeed = cruiseSpeed
    this.departureAirport = departureAirport
    this.estimatedDeparture = estimatedDeparture
    this.actualDeparture = actualDeparture
    this.cruiseAlt = cruiseAlt
    this.arrivalAirport = arrivalAirport
    this.hoursEnRoute = hoursEnRoute
    this.minitesEnroute = minitesEnroute
    this.hoursFuel = hoursFuel
    this.minutesFuel = minutesFuel
    this.alternateAirport = alternateAirport
    this.remarks = remarks
    this.route = route
  }

  static parseRawMessage(rawMessage) {
    throw new Error('Not implement')
  }

  toString() {
    return this.command + [
      this.source,
      this.destination,
      this.flightRules,
      this.aircraftType,
      this.cruiseSpeed,
      this.departureAirport,
      this.estimatedDeparture.toString(),
      this.actualDeparture.toString(),
      this.cruiseAlt,
      this.arrivalAirport,
      this.hoursEnRoute,
      this.minitesEnroute,
      this.hoursFuel,
      this.minutesFuel,
      this.alternateAirport,
      this.remarks,
      this.route,
      this.typeOfFlight,
      '0',
      ''
    ].join(':')
  }
}