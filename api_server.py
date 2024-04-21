from pydantic import BaseModel, ConfigDict
from geopy.distance import Distance
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from training_server import training_server, TrainingController
from helpers import get_sid_approach_names_by_airport_ident

app = FastAPI()

origins = [
    'http://192.168.0.5:9000',
    'http://dev.d.wlliou.pw:9000',
    'http://d.wlliou.pw:16809',
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def to_lower_camel(string: str) -> str:
    words = string.split('_')
    return words[0] + ''.join(word.capitalize() for word in words[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_lower_camel,
        populate_by_name=True
    )


@app.get('/airports/{airport_ident}/sids')
def get_sids(airport_ident: str):
    return [sid.fix_ident for sid in get_sid_approach_names_by_airport_ident(airport_ident)]


@app.get('/aircrafts')
def get_aircrafts():
    connections = [conn for conn in training_server.connections.values()]
    return [{
        'id': conn.id,
        'callsign': conn.aircraft.callsign,
        'parking': (conn.aircraft.parking.name or '') + str(conn.aircraft.parking.number),
        'altitude': int(conn.aircraft.position.altitude_.feet),
        'squawkCode': conn.aircraft.squawk_code,
        'flightplanRoute': conn.aircraft.flightplan.route,
        'flightplan': {
            'departureAirport': conn.aircraft.flightplan.departure_airport,
            'arrivalAirport': conn.aircraft.flightplan.arrival_airport,
            'route': conn.aircraft.flightplan.route,
            'cruiseAltitude': int(conn.aircraft.flightplan.cruise_altitude.feet),
            'cruiseSpeed': int(conn.aircraft.flightplan.cruise_speed.knots),
        } if conn.aircraft.flightplan is not None else None,
        'targetAltitude': int(conn.aircraft.target_altitude.feet) if conn.aircraft.target_altitude is not None else None,
        'status': conn.aircraft.status
    } for conn in connections if conn.aircraft is not None]


class ClearanceDelivery(CamelModel):
    sid_name: str
    initial_altitude: int
    squawk_code: str


@app.post('/aircrafts/{aircraft_id}/clearance-delivery')
def clearance_delivery(aircraft_id: str, form: ClearanceDelivery):
    source_conn = training_server.connections[aircraft_id]
    target_conn = training_server.connections[aircraft_id]
    controller = TrainingController(
        source_conn,
        training_server.connections
    )
    controller.delivered(
        target_conn,
        form.sid_name,
        None,
        Distance(feet=form.initial_altitude),
        form.squawk_code,
    )
    return {}


@app.post('/aircrafts/{aircraft_id}/startup-pushback-approved')
def startup_pushback_approved(aircraft_id: str):
    source_conn = training_server.connections[aircraft_id]
    target_conn = training_server.connections[aircraft_id]
    controller = TrainingController(
        source_conn,
        training_server.connections
    )
    controller.pushback_approved(target_conn)
    return {}


class Taxi(CamelModel):
    taxi_path: list[str]
    runway_name: str


@app.post('/aircrafts/{aircraft_id}/taxi')
def taxi(aircraft_id: str, taxi: Taxi):
    source_conn = training_server.connections[aircraft_id]
    target_conn = training_server.connections[aircraft_id]
    controller = TrainingController(
        source_conn,
        training_server.connections
    )
    controller.taxi_approved(target_conn, taxi.taxi_path, taxi.runway_name)
    return {}


class LineupAndWait(CamelModel):
    runway_name: str


@app.post('/aircrafts/{aircraft_id}/lineup-and-wait')
def taxi(aircraft_id: str, lineup_and_wait: LineupAndWait):
    source_conn = training_server.connections[aircraft_id]
    target_conn = training_server.connections[aircraft_id]
    controller = TrainingController(
        source_conn,
        training_server.connections
    )
    controller.lineup_and_wait(target_conn, lineup_and_wait.runway_name)
    return {}


class ClearedTakeoff(CamelModel):
    runway_name: str


@app.post('/aircrafts/{aircraft_id}/cleared-takeoff')
def taxi(aircraft_id: str, cleared_takeoff: ClearedTakeoff):
    source_conn = training_server.connections[aircraft_id]
    target_conn = training_server.connections[aircraft_id]
    controller = TrainingController(
        source_conn,
        training_server.connections
    )
    controller.cleared_takeoff(
        target_conn,
        cleared_takeoff.runway_name,
    )
    return {}


class Aircraft(CamelModel):
    target_altitude: int


@app.put('/aircrafts/{aircraft_id}')
def taxi(aircraft_id: str, aircraft: Aircraft):
    source_conn = training_server.connections[aircraft_id]
    target_conn = training_server.connections[aircraft_id]
    controller = TrainingController(
        source_conn,
        training_server.connections
    )
    controller.change_altitude(
        target_conn,
        Distance(feet=aircraft.target_altitude)
    )
    return {}
