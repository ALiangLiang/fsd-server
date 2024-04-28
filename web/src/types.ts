export enum AircraftStatus {
  NOT_DELIVERED = 0,
  DELIVERED = 1,
  APPROVED_PUSHBACK_STARTUP = 2,
  APPROVED_TAXI_TO_RWY = 3,
  LINEUP_WAIT = 4,
  CLEARED_TAKEOFF = 5,
  CLEARED_LAND = 6,
  MISSED_APPROACH = 7,
  VACATE_RUNWAY = 8,
  APPROVED_TAXI_TO_BAY = 9,
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

export interface Approach {
  id: number
  name: string
  runwayName: string
  type: 'ILS' | 'LOC' | 'RNAV'
}