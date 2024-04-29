from uuid import uuid1
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from geopy.distance import Distance
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from training_server import training_server, TrainingController
from helpers import (
    get_sid_approach_names_by_airport_ident,
    get_parkings_by_airport_ident,
    get_parking_by_parking_id,
    get_approach_approaches_by_airport_ident
)
from utils.preset_flightplans import b738_config, flightplans
from utils.flightplan import Flightplan
from utils.connection import Connection

app = FastAPI()


def to_lower_camel(string: str) -> str:
    words = string.split('_')
    return words[0] + ''.join(word.capitalize() for word in words[1:])


app.mount("/console", StaticFiles(directory="web/dist"), name="static")


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_lower_camel,
        populate_by_name=True
    )


@app.get('/airports/{airport_ident}/sids')
def get_sids(airport_ident: str):
    return [sid.fix_ident for sid in get_sid_approach_names_by_airport_ident(airport_ident)]


@app.get('/airports/{airport_ident}/approaches')
def get_approaches(airport_ident: str):
    return [
        {
            'id': app.approach_id,
            'name': app.arinc_name,
            'runwayName': app.runway_name,
            'type': app.type
        } for app in get_approach_approaches_by_airport_ident(airport_ident) if app.type in ('ILS', 'LOC')
    ]


@app.get('/airports/{airport_ident}/parkings')
def get_parkings(airport_ident: str):
    return [
        {
            'id': p.parking_id,
            'name': p.full_name,
            'type': p.type_description
        } for p in get_parkings_by_airport_ident(airport_ident)
    ]


@app.get('/preset-flightplans')
def get_preset_flightplans():
    return [{
        'route': fp.route,
        'departureAirport': fp.departure_airport,
        'arrivalAirport': fp.arrival_airport,
        'cruiseAltitude': int(fp.cruise_altitude.feet),
    } for fp in flightplans]


@app.get('/aircrafts')
def get_aircrafts():
    connections = [conn for conn in training_server.connections.values()]
    return [{
        'id': conn.id,
        'callsign': conn.aircraft.callsign,
        'parking': {
            'id': conn.aircraft.parking.parking_id,
            'name': conn.aircraft.parking.full_name,
            'type': conn.aircraft.parking.type_description
        } if conn.aircraft.parking is not None else None,
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
        'expectRunway': conn.aircraft.expect_runway_end.name if conn.aircraft.expect_runway_end else None,
        'status': conn.aircraft.status
    } for conn in connections if conn.aircraft is not None]


class AircraftFlightplan(CamelModel):
    departure: str
    route: str
    arrival: str
    cruiseAltitude: int


class AircraftBody(CamelModel):
    intention: Literal['departure', 'arrival']
    parking_id: Optional[int | None] = Field(None)
    callsign: str | None
    flightplan: AircraftFlightplan | None
    approach_id: Optional[int | None] = Field(None)
    arrival_airport: Optional[str | None] = Field(None)


@app.post('/aircrafts')
def create_aircraft(form: AircraftBody):
    flightplan = Flightplan(
        departure_airport=form.flightplan.departure,
        arrival_airport=form.flightplan.arrival,
        flight_rules='I',
        route=form.flightplan.route,
        cruise_altitude=Distance(feet=form.flightplan.cruiseAltitude),
        **b738_config
    ) if form.flightplan is not None else None

    if form.intention == 'departure':
        aircraft = training_server.factory.generate_on_parking(
            departure_airport_ident=form.flightplan.departure,
            callsign=form.callsign,
            flightplan=flightplan,
            parking=None if form.parking_id is None else get_parking_by_parking_id(
                form.parking_id
            ),
        )
    else:
        aircraft = training_server.factory.generate_on_approaching(
            arrival_airport_ident=form.arrival_airport,
            callsign=form.callsign,
            flightplan=flightplan,
            approach_id=form.approach_id,
        )

    if aircraft is None:
        raise HTTPException(status_code=400, detail='Error')

    conn = Connection(
        lambda: None,
        training_server._on_lost_connection,
        training_server._on_text_message,
    )
    conn.id = str(uuid1())
    conn.aircraft = aircraft
    conn.callsign = aircraft.callsign
    conn.type = 'PILOT'
    training_server.connections[conn.id] = conn

    return {'id': conn.id, 'callsign': aircraft.callsign}


class Aircraft(CamelModel):
    target_altitude: int


@app.put('/aircrafts/{aircraft_id}')
def update_aircraft(aircraft_id: str, aircraft: Aircraft):
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


@app.delete('/aircrafts/{aircraft_id}')
def delete_aircraft(aircraft_id: str):
    source_conn = training_server.connections[aircraft_id]
    target_conn = training_server.connections[aircraft_id]
    controller = TrainingController(
        source_conn,
        training_server.connections
    )
    controller.shutdown(target_conn)
    return {}


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


@app.post('/aircrafts/{aircraft_id}/taxi')
def taxi(aircraft_id: str, taxi: Taxi):
    source_conn = training_server.connections[aircraft_id]
    target_conn = training_server.connections[aircraft_id]
    controller = TrainingController(
        source_conn,
        training_server.connections
    )
    controller.taxi_approved(target_conn, taxi.taxi_path)
    return {}


@app.post('/aircrafts/{aircraft_id}/lineup-and-wait')
def lineup_and_wait(aircraft_id: str):
    source_conn = training_server.connections[aircraft_id]
    target_conn = training_server.connections[aircraft_id]
    controller = TrainingController(
        source_conn,
        training_server.connections
    )
    controller.lineup_and_wait(target_conn)
    return {}


@app.post('/aircrafts/{aircraft_id}/cleared-takeoff')
def cleared_takeoff(aircraft_id: str):
    source_conn = training_server.connections[aircraft_id]
    target_conn = training_server.connections[aircraft_id]
    controller = TrainingController(
        source_conn,
        training_server.connections
    )
    controller.cleared_takeoff(target_conn)
    return {}


class ClearedLandBody(CamelModel):
    vacated_taxiway: str | None


@app.post('/aircrafts/{aircraft_id}/cleared-land')
def cleared_land(aircraft_id: str, cleared_land_body: ClearedLandBody):
    source_conn = training_server.connections[aircraft_id]
    target_conn = training_server.connections[aircraft_id]
    controller = TrainingController(
        source_conn,
        training_server.connections
    )
    controller.cleared_land(target_conn)
    return {}


class Taxi2BayBody(CamelModel):
    parking_id: int
    taxi_path: list[str]


@app.post('/aircrafts/{aircraft_id}/taxi-to-bay')
def taxi_to_bay(aircraft_id: str, taxi_to_bay_body: Taxi2BayBody):
    source_conn = training_server.connections[aircraft_id]
    target_conn = training_server.connections[aircraft_id]
    controller = TrainingController(
        source_conn,
        training_server.connections
    )
    controller.taxi_to_bay(
        target_conn,
        taxi_to_bay_body.taxi_path,
        taxi_to_bay_body.parking_id,
    )
    return {}
