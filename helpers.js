const { open } = require('node:fs/promises')
const turf = require('@turf/turf')

const Position = require('./messages/Position')

module.exports = {}

const PI = Math.PI;
const toRadians = function (degrees) {
  return degrees * PI / 180;
};
const toDegrees = function (radians) {
  return radians * 180 / PI;
};

module.exports.fixRadialDistance = function fixRadialDistance(position, bearing, distance) {
  const _pos = turf.destination(
    turf.point([position.longitude, position.latitude]),
    distance,
    bearing,
    { units: 'meters' }
  ).geometry.coordinates
  return new Position(_pos[1], _pos[0])
}

module.exports.getBearingDistance = function getBearingDistance(position1, position2) {
  const bearing = turf.bearing(
    turf.point([position1.longitude, position1.latitude]),
    turf.point([position2.longitude, position2.latitude])
  )
  const distance = turf.distance(
    turf.point([position1.longitude, position1.latitude]),
    turf.point([position2.longitude, position2.latitude]),
    { units: 'meters' }
  )

  return {
    distance, // meters
    bearing
  };
}

module.exports.readEarthFix = async function readEarthFix() {
  const file = await open('earth_fix.dat')
  const fixes = []
  for await (const line of file.readLines()) {
    if (line[0] !== ' ') continue

    const [latitude, longitude, ident, type, region] = line.trim().replace(/  +/g, ' ').split(' ')
    if (region !== 'RC') continue

    fixes.push({
      position: new Position(parseFloat(latitude), parseFloat(longitude)),
      ident,
      type,
      region
    })
  }
  return fixes
}

module.exports.readEarthNav = async function readEarthNav() {
  const file = await open('earth_nav.dat')
  const navs = []
  for await (const line of file.readLines()) {
    if (line[0] !== ' ') continue

    const [, latitude, longitude, , , , , ident, type, region, name] = line.trim().replace(/  +/g, ' ').split(' ')
    if (region !== 'RC') continue

    navs.push({
      position: new Position(parseFloat(latitude), parseFloat(longitude)),
      ident,
      type,
      region,
      name
    })
  }
  return navs
}

module.exports.readProcedures = async function readEarthNav(airport, fixes) {
  const file = await open(`CIFP/${airport}.dat`)
  const procedures = {}
  for await (const line of file.readLines()) {
    if (line === '') continue

    const [typeNSeq, , ident, runway, navaid] = line.trim().replace(/ /g, '').split(',')
    const [type, seq] = typeNSeq.split(':')

    if (type === 'RWY') continue

    procedures[ident] = procedures[ident] || {}
    const procedure = procedures[ident]
    procedure.ident = ident
    procedure.type = type
    procedure.runway = runway
    // TODO: sort by seq
    procedure.navaids = procedure.navaids || []
    const fix = fixes.find((fix) => fix.ident === navaid)
    if (fix === undefined) continue
    procedure.navaids.push(fix)
  }
  return procedures
}
