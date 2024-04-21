import re
import logging
from uuid import uuid1

import requests
import astar
from geopy.distance import distance as distance_between, Distance

import db.init
from db.models import TaxiPath, Parking
from aircrafts.bot_aircraft import BotAircraft, AircraftStatus
from utils.fsd_server import FsdServer
from utils.aircraft_factory import AircraftFactory
from utils.connection import Connection
from utils.fsd_controller import FsdController
from messages.Position import Position
from messages.TextMessage import TextMessage
from helpers import (
    get_taxt_positions_by_airport_id_n_taxi_path_names,
    get_pushback_paths_by_parking_id,
    get_start_by_airport_id_n_runway_name,
    get_sid_approaches_by_airport_ident_n_approach_name,
    get_star_approaches_by_airport_ident_n_approach_name,
    fill_position_on_legs
)

logging.basicConfig(level=logging.DEBUG)
# logging.getLogger('aircrafts.aircrafts').setLevel(logging.INFO)


NUMBER_OF_AIRCRAFTS = 10


class Node:
    def __init__(self, position: Position, is_hold_short: bool, g=0.0, h=0.0):
        self.position = position
        self.links: list[Node] = []
        self.is_hold_short = is_hold_short
        self.name = str(hash(self))

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.position == other.position

    def __hash__(self):
        return hash(self.position)

    @property
    def id(self):
        return str(hash(self))


def get_taxi_path(start_parking: Parking, taxi_path_names: list[str]):
    pushback_paths = get_pushback_paths_by_parking_id(
        start_parking.parking_id
    )
    pushback_path = pushback_paths[0]
    push_to_position = pushback_path.end_position if pushback_path.start_position == start_parking.position else pushback_path.start_position
    all_nodes: set[Node] = set()
    all_taxi_paths = get_taxt_positions_by_airport_id_n_taxi_path_names(
        start_parking.airport_id,
        taxi_path_names
    )

    position_hash_node_map = {}

    def get_node_by_taxi_path(taxi_path: TaxiPath):
        hash_start_position = hash(taxi_path.start_position)
        hash_end_position = hash(taxi_path.end_position)
        if hash_start_position not in position_hash_node_map:
            position_hash_node_map[hash_start_position] = Node(
                taxi_path.start_position,
                is_hold_short=taxi_path.start_type in ('HSND', 'IHSND'),
            )
        if hash_end_position not in position_hash_node_map:
            position_hash_node_map[hash_end_position] = Node(
                taxi_path.end_position,
                is_hold_short=taxi_path.end_type in ('HSND', 'IHSND'),
            )
        return (
            position_hash_node_map.get(hash_start_position),
            position_hash_node_map.get(hash_end_position),
        )

    for tp in all_taxi_paths:
        start_node, end_node = get_node_by_taxi_path(tp)
        start_node.links.append(end_node)
        end_node.links.append(start_node)
        all_nodes.add(start_node)
        all_nodes.add(end_node)

    start_node = next(
        (n for n in all_nodes if n.position == push_to_position),
        None
    )
    target_node = next(
        (n for n in all_nodes if n.is_hold_short),
        None
    )

    def distance_between_nodes(n1: Node, n2: Node):
        return distance_between(n1.position, n2.position).meters

    return astar.find_path(
        start_node,
        target_node,
        neighbors_fnct=lambda n: n.links,
        heuristic_cost_estimate_fnct=distance_between_nodes,
        distance_between_fnct=distance_between_nodes
    )


class TrainingController(FsdController):
    frequency = '@18700'

    def delivered(
        self,
        target_conn: Connection,
        sid_name: str,
        star_name: str | None,
        initial_altitude: Distance,
        squawk: str
    ):
        aircraft = target_conn.aircraft
        if aircraft is None or not isinstance(aircraft, BotAircraft) or target_conn.callsign is None:
            return
        if aircraft.parking is None or aircraft.flightplan is None:
            return
        sid_approaches = get_sid_approaches_by_airport_ident_n_approach_name(
            aircraft.flightplan.departure_airport,
            sid_name
        )
        used_sid = sid_approaches[0]
        aircraft.set_sid_legs(
            fill_position_on_legs(
                used_sid.approach_legs,
                aircraft.flightplan.departure_airport
            )
        )

        if star_name is not None:
            get_star_approaches_by_airport_ident_n_approach_name(
                aircraft.flightplan.arrival_airport,
                star_name
            )
        aircraft.set_squawk(squawk)
        aircraft.set_transponder_mode_c()
        aircraft.set_target_altitude(initial_altitude)
        aircraft.set_status(AircraftStatus.DELIVERED)

        last_route_str = f'{star_name} arrival' if star_name is not None else 'flightplan route'
        self.send_text_to_all_connections(
            target_conn.callsign,
            self.frequency,
            f'Cleared to {aircraft.flightplan.arrival_airport} via {sid_name}, ..., {last_route_str}, '
            f'climb and maintain {int(initial_altitude.feet)}, squawk {squawk}, {target_conn.callsign}'
        )

    def pushback_approved(self, target_conn: Connection):
        aircraft = target_conn.aircraft
        if aircraft is None or not isinstance(aircraft, BotAircraft) or target_conn.callsign is None or aircraft.parking is None:
            return

        pushback_paths = get_pushback_paths_by_parking_id(
            aircraft.parking.parking_id)
        if len(pushback_paths) == 0:
            self.send_text_to_all_connections(
                target_conn.callsign,
                self.frequency,
                f'Unable, {target_conn.callsign}'
            )
            return
        if aircraft is None:
            return

        self.send_text_to_all_connections(
            target_conn.callsign,
            self.frequency,
            f'Startup and pushback approved, {target_conn.callsign}'
        )
        pushback_path = pushback_paths[0]
        push_to_position = pushback_path.end_position if pushback_path.start_position == aircraft.position else pushback_path.start_position
        aircraft.start_pushback([push_to_position])

    def taxi_approved(self, target_conn: Connection, taxiway_names: list[str], runway_name: str):
        aircraft = target_conn.aircraft
        if aircraft is None or not isinstance(aircraft, BotAircraft) or target_conn.callsign is None:
            return

        path = get_taxi_path(
            aircraft.parking,
            taxiway_names
        )
        if path is None:
            self.send_text_to_all_connections(
                target_conn.callsign,
                self.frequency,
                f'Unable, {target_conn.callsign}'
            )
            return

        path_positions = [p.position for p in path]
        taxiway_name_sentence = ' '.join(taxiway_names)
        self.send_text_to_all_connections(
            target_conn.callsign,
            self.frequency,
            f'Runway {runway_name.upper()}, taxi via {taxiway_name_sentence}, {target_conn.callsign}'
        )
        path_positions.pop(0)
        aircraft.start_taxi(path_positions)

    def lineup_and_wait(self, target_conn: Connection, runway_name: str):
        aircraft = target_conn.aircraft
        if aircraft is None or not isinstance(aircraft, BotAircraft) or target_conn.callsign is None:
            return
        if len(aircraft.departure_path) == 0:
            self.send_text_to_all_connections(
                target_conn.callsign,
                self.frequency,
                'Unable'
            )
            return

        self.send_text_to_all_connections(
            target_conn.callsign,
            self.frequency,
            f'Line-up and wait, runway {runway_name.upper()}, {target_conn.callsign}'
        )
        aircraft.start_lineup_wait()

    def cleared_takeoff(self, target_conn: Connection, runway_name: str):
        aircraft = target_conn.aircraft
        if aircraft is None or not isinstance(aircraft, BotAircraft) or target_conn.callsign is None:
            return

        url = (
            'https://aviationweather.gov/api/data/metar'
            f'?ids={target_conn.aircraft.flightplan.departure_airport}&format=json'
        )
        response = requests.get(url)
        airport_data = response.json()[0]
        wdir = airport_data['wdir']
        wspd = airport_data['wspd']
        altim = airport_data['altim']

        self.send_text_to_all_connections(
            target_conn.callsign,
            self.frequency,
            f'Runway {runway_name.upper()}, wind {wdir} at {wspd} knots, QNH {altim}, cleared for takeoff, {target_conn.callsign}'
        )
        aircraft.start_departure()

    def change_altitude(self, target_conn: Connection, altitude: Distance):
        aircraft = target_conn.aircraft
        if aircraft is None or not isinstance(aircraft, BotAircraft) or target_conn.callsign is None:
            return

        action_str = 'Climb' if aircraft.position.altitude_ < altitude else 'Descend'

        self.send_text_to_all_connections(
            target_conn.callsign,
            self.frequency,
            f'{action_str} and maintain {int(altitude.feet)}, {target_conn.callsign}'
        )
        aircraft.set_target_altitude(altitude)

    def handle_instrucation(self, target_conn: Connection, message: TextMessage):
        if target_conn.aircraft is None:
            return
        aircraft = target_conn.aircraft
        if not isinstance(aircraft, BotAircraft):
            return
        sentences = message.message.split(',')
        lower_message = message.message.lower()

        if re.search(r'(cleared|clrd?) to \w+,? via', lower_message) is not None:
            # del
            sid_name_match = re.search(
                r'via ([a-z]{2,5}\d[a-z]?)',
                lower_message
            )
            sid_name = sid_name_match.group(1)
            sid_name = sid_name.upper()
            # ex. CHALI1C -> CHAL1C
            sid_name = sid_name[:4] + \
                sid_name[5:] if len(sid_name) == 7 else sid_name
            star_name_match = re.search(
                r'([a-z]{2,5}\d[a-z]?) arrival',
                lower_message
            )
            star_name = None
            if star_name_match is not None:
                star_name = star_name_match.group(1)
                star_name = star_name.upper()
            initial_altitude_match = re.search(
                r'(initial altitude|climb and maintain|c\/m) ?(\d{4}|FL\d{3})',
                lower_message
            )
            initial_altitude = initial_altitude_match.group(2)
            initial_altitude = int(initial_altitude[2:]) * 100 \
                if initial_altitude.startswith('fl') \
                else int(initial_altitude)
            squawk_match = re.search(r'(squawk|sq) ?([0-7]{4})', lower_message)
            squawk = squawk_match.group(2)
            self.delivered(
                target_conn,
                sid_name,
                star_name,
                Distance(feet=initial_altitude),
                squawk
            )
            return
        elif re.search(r'(start(up)?|s\/u) (and|&|n) pushback approved?', lower_message) is not None:
            # gnd
            self.pushback_approved(target_conn)
            return
        elif re.search(r'((climb|decend) and maintain|[cd]\/m) (fl\d{3}|\d{3,5})', lower_message) is not None:
            altitude_match = re.search(
                r'((climb/decend) and maintain|[cd]\/m) (fl\d{3}|\d{3,5})',
                lower_message
            )
            altitude = altitude_match.group(3)
            altitude = int(
                altitude[2:]) * 100 if altitude.startswith('fl') else int(altitude)
            altitude = Distance(feet=altitude)
            self.change_altitude(target_conn, altitude)
            return
        elif len(sentences) > 2:
            path_str = sentences[2].strip().lower()
            runway_name_match = re.search(
                r'(runway|rwy) ?(\d{2}[lrc]?)',
                lower_message
            )
            runway_name = runway_name_match.group(2).upper()
            if path_str.startswith('taxi via'):
                path_str = sentences[2].strip().lower()
                taxiway_names = [
                    n.upper() for n in path_str.replace('taxi via ', '').split(' ') if n != ''
                ]
                self.taxi_approved(target_conn, taxiway_names, runway_name)

                start = get_start_by_airport_id_n_runway_name(
                    aircraft.parking.airport_id,
                    runway_name
                )
                aircraft.set_departure_path([start.position])
                return
            elif re.search(r'(line[- ]?up (and|n|&) wait|l\/u (and|n|&) w|luw)', lower_message) is not None:
                self.lineup_and_wait(
                    target_conn,
                    runway_name,
                )
                return
            elif re.search(r'(clear(ed)?|clrd?) (to |for )?(takeoff|t\/o)', lower_message) is not None:
                self.cleared_takeoff(
                    target_conn,
                    runway_name,
                )
                return

        raise Exception('Cannot parse instruction')

    def handle_text_message(self, message):
        super().handle_text_message(message)

        sentences = message.message.split(',')
        callsign = sentences[0]
        target_conn = next(
            conn for conn in self.connections.values() if conn.callsign == callsign
        )
        if target_conn is None or target_conn.aircraft is None:
            return

        try:
            return self.handle_instrucation(target_conn, message)
        except Exception as e:
            logging.exception(e)

        # cannot parse instruction
        self.send_text_to_all_connections(
            target_conn.callsign,
            self.frequency,
            f'Say again, {target_conn.callsign}'
        )


def on_pushback_completed(conn: Connection):
    conn.send_text(
        self.frequency,
        f'Pushback completed, {conn.callsign}'
    )


class TrainingServer(FsdServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.factory = AircraftFactory()

    def on_start(self):
        for _ in range(NUMBER_OF_AIRCRAFTS):
            # factory.generate_w_random_situation(random_progress=True)
            conn = Connection(
                lambda: None,
                lambda: None,
                self._on_text_message,
            )
            conn.id = str(uuid1())
            aircraft = self.factory.generate_on_parking('RCTP')
            if aircraft is None:
                continue

            aircraft.on_pushback_completed = on_pushback_completed
            conn.aircraft = aircraft
            conn.callsign = conn.aircraft.callsign
            conn.type = 'PILOT'
            self.connections[conn.id] = conn

    def on_tick(self):
        pass

    def on_tick_connection(self, conn, after_time):
        if conn.type != 'PILOT' or conn.aircraft is None:
            return

        # update bot aircrafts
        aircraft = conn.aircraft
        if isinstance(aircraft, BotAircraft):
            aircraft.update_status(after_time)

    def on_connection_made(self, connection):
        pass

    def on_message(self, connection, message):
        pass


training_server = TrainingServer(
    '0.0.0.0',
    Controller=TrainingController
)
