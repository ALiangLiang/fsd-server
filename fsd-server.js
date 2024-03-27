const net = require('net')
const PilotPositionUpdateMessage = require('./messages/PilotPositionUpdateMessage')
const FlightplanMessage = require('./messages/FlightplanMessage')
const AddATCMessage = require('./messages/AddATCMessage')
const Position = require('./messages/Position')
const Time = require('./messages/Time')
const { fixRadialDistance } = require('./helpers')

const server = net.createServer();

async function send(socket, msg) {
  return new Promise((resolve) => {
    console.log('Send msg to client:', msg)
    socket.write(msg + '\r\n', resolve)
  })
}

server.listen(6809, function () {
  console.log('TCP Server start')
})

let pos = new Position(25.04, 121.14)
let lastTime = new Date()

const MY_CALLSIGN = 'XE_WL_OBS'
const AC_CALLSIGN = 'CAL123'
const SQUAWK_CODE = '4601'
const GROUND_SPEED = 523 // km/h
const ALTITUDE = 40571 // feet
const PBH_TUPLE = [0, 0, 0, false] // pitch, bank, heading, on ground
const PRESSURE_DELTA = -1573

const REMARK = 'PBN/A1B1C1D1L1O1S2 DOF/240327 REG/N891SB EET/RJJJ0030 RKRR0043 OPR/SIA PER/D RMK/TCAS SIMBRIEF'
const ROUTE = 'PIANO1C PIANO L3 SALMI B576 CJU Y722 OLMEN OLMEN2E'

function tickMoveAircraft(socket) {
  setInterval(async () => {
    const now = new Date()
    const timeDiff = now - lastTime
    lastTime = now
    const distance = (GROUND_SPEED / 3600) * timeDiff // meters
    console.log('move meters:', distance)
    pos = fixRadialDistance(pos, 0, distance)

    const message = new PilotPositionUpdateMessage(
      AC_CALLSIGN,
      'N',
      SQUAWK_CODE,
      '4',
      pos,
      ALTITUDE,
      GROUND_SPEED,
      PBH_TUPLE,
      PRESSURE_DELTA
    )
    await send(socket, message.toString());
  }, 2000)
}

async function sendFlightPlan(socket) {
  const message = new FlightplanMessage(
    AC_CALLSIGN,
    MY_CALLSIGN,
    'I',
    'S',
    '1/B738/H-SDE1E2E3FGHIJ2J3J4J5M1RWXY/LB1D1',
    'N0489',
    'RCTP',
    new Time(13, 35),
    new Time(13, 35),
    'F390',
    'RKSI',
    1,
    55,
    3,
    30,
    'RKPK',
    REMARK,
    ROUTE
  ).toString()
  try {
    await send(socket, message.toString())
  } catch (err) {
    console.error(err)
    // TODO: send Error Message
  }
}

server.on('connection', async function (socket) {
  tickMoveAircraft(socket)

  socket.on('data', function (data) {
    console.log('Data sent to server : ' + data);
    if (data.toString()[0] == '#') {
      if (data.toString().substring(1, 2) == 'AA') {
        const message = AddATCMessage.parseRawMessage(data.toString())
      }
    }

    // send one time instead of sending on receiving data
    sendFlightPlan(socket)
  })
})