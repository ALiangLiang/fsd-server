export enum AircraftStatus {
  NOT_DELIVERED = 0,
  DELIVERED = 1,
  APPROVED_PUSHBACK_STARTUP = 2,
  APPROVED_TAXI = 3,
  LINEUP_WAIT = 4,
  CLEARED_TAKEOFF = 5,
}

export interface Aircraft {
  id: string
  callsign: string
  parking: Parking
  status: AircraftStatus
  squawkCode: string
}

export interface Parking {
  id: number
  name: string
  type: string
}

export interface Flightplan {
  route: string
  departureAirport: string
  arrivalAirport: string
  cruiseAltitude: number
}