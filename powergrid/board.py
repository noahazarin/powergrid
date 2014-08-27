import json
import itertools

from networkx.readwrite import json_graph
import networkx


class Board(object):
    def __init__(self, data_path):
        with open(data_path, 'r') as graph_file:
            graph_data = json.load(graph_file)
        self.graph = json_graph.node_link_graph(graph_data, multigraph=False)
        self.name_node_map = {node[1]['name']: node[0] for node in self.graph.nodes(data=True)}
        self.all_paths = networkx.all_pairs_dijkstra_path(self.graph)
        self.all_costs = networkx.all_pairs_dijkstra_path_length(self.graph)
        # add blank houses set to each node
        for node in self.graph.nodes():
            self.graph.node[node]['houses'] = set()

    def add_house(self, city_name, player):
        if city_name not in self.name_node_map:
            return False
        node = self.name_node_map[city_name]
        if player.color in self.graph.node[node]['houses']:
            return False
        if len(self.graph.node[node]['houses']) >= 3:
            return False
        self.graph.node[node]['houses'].add(player.color)
        return True

    def clear_board(self):
        for node in self.graph.nodes():
            self.graph.node[node]['houses'] = set()

    def get_cost(self, player, cities):
        if not cities:
            return 0, []

        # get cities with player houses
        player_nodes = [n[0] for n in self.graph.nodes(data=True) if player in n[1]['houses']]
        if not player_nodes:
            # player has no houses yet, pick a city to start
            player_nodes = [self.name_node_map[cities[0]]]

        # get requested city nodes
        city_nodes = {self.name_node_map[city]: city for city in cities}

        total_cost = 0
        build_paths = []

        # find the cheapest cities to move to, one by one
        while cities:
            prod = itertools.product(player_nodes, city_nodes.keys())
            min_ = 10000
            min_city = None
            min_player = None
            for player_node, city_node in prod:
                cost = self.all_costs[player_node][city_node]
                if cost < min_:
                    min_ = cost
                    min_city = city_node
                    min_player = player_node

            # found cheapest city to place
            total_cost += min_
            build_paths.append(self.all_paths[min_player][min_city])
            total_cost += [10, 15, 20][len(self.graph.node[min_city]['houses'])]
            city = city_nodes[min_city]
            del city_nodes[min_city]
            cities.remove(city)
            player_nodes.append(min_city)
        return total_cost, build_paths

    def get_board_info(self):
        info = {"cities": []}
        cities = list(self.name_node_map.items())
        cities.sort(key=lambda x: self.graph.node[x[1]]['region'])

        for city, city_node in cities:
            node = self.graph.node[city_node]
            info['cities'].append({'name': city, 'houses': list(node['houses']), 'region_color': node['region']})
        return info