import unittest
from geopy.distance import distance

import astar

from helpers import (
    get_airport_by_ident,
    get_taxt_positions_by_airport_ident_n_taxi_path_names,
    get_parking_by_airport_n_name_n_number,
    get_sid_approaches_by_airport_ident_n_approach_name,
    get_runway_end_by_airport_id_n_runway_name
)
from messages.Position import Position
from db.models import TaxiPath


class Node:
    def __init__(self, position: Position, is_hold_short: bool, edge_name: str = '', g=0.0, h=0.0):
        self.position = position
        self.edge_name = edge_name
        self.g = g
        self.h = h
        self.links: list[Node] = []
        self.is_hold_short = is_hold_short
        self.name = str(hash(self))

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.position == other.position

    def __lt__(self, other):
        return (self.g + self.h) < (other.g + other.h)

    def __hash__(self):
        return hash(self.position)

    @property
    def id(self):
        return str(hash(self))


class TestHelpers(unittest.TestCase):

    def test_get_airport_by_ident(self):
        airport = get_airport_by_ident('RCTP')
        self.assertIsNotNone(airport)

    def test_get_parking_by_airport_n_name_n_number(self):
        parking = get_parking_by_airport_n_name_n_number('RCTP', 'GC', 3)
        self.assertEqual(parking.name, 'GC')
        self.assertEqual(parking.number, 3)

    def test_get_taxt_positions_by_airport_n_taxi_path_names(self):
        start_parking = get_parking_by_airport_n_name_n_number('RCTP', 'GC', 3)
        taxi_path_names = ['C3', 'Q', 'Q6', 'S', 'S1']
        all_nodes: set[Node] = set()
        all_taxi_paths = get_taxt_positions_by_airport_ident_n_taxi_path_names(
            'RCTP',
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
                    edge_name=taxi_path.name
                )
            if hash_end_position not in position_hash_node_map:
                position_hash_node_map[hash_end_position] = Node(
                    taxi_path.end_position,
                    is_hold_short=taxi_path.end_type in ('HSND', 'IHSND'),
                    edge_name=taxi_path.name
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
            (n for n in all_nodes if n.position == start_parking.position),
            None
        )
        target_node = next(
            (n for n in all_nodes if n.is_hold_short),
            None
        )

        def distance_between(n1: Node, n2: Node):
            """computes the distance between two nodes"""
            return distance(n1.position, n2.position).meters

        path = astar.find_path(
            start_node,
            target_node,
            neighbors_fnct=lambda n: n.links,
            heuristic_cost_estimate_fnct=distance_between,
            distance_between_fnct=distance_between
        )
        self.assertIsNotNone(path)
        # for node in path:
        #     print(str(node.position.longitude) +
        #           ',' + str(node.position.latitude))

    def test_get_sid_approaches_by_airport_ident_n_approach_name(self):
        sid_approaches = get_sid_approaches_by_airport_ident_n_approach_name(
            'RCTP',
            'CHAL1C'
        )
        self.assertEqual(len(sid_approaches), 1)

    def test_get_runway_end_by_airport_id_n_runway_name(self):
        get_runway_end_by_airport_id_n_runway_name(
            119066, '05R').position_on_gs
