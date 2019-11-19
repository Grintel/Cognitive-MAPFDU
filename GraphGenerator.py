# Copyright 2019 (C) Lukas Berger [lukas.berger@uranus.uni-freiburg.de]

import random
import dijkstra as dijk


def generate_grid(m, n):
    """ Generates an N X M grid-graph using dictionaries """
    map_dict = {}
    for y in range(0, n):
        for x in range(0, m):
            linker = set()
            if x != 0:
                linker.add(map_positions(x - 1, y, m))
            if y != 0:
                linker.add(map_positions(x, y - 1, m))
            if x != m-1:
                linker.add(map_positions(x + 1, y, m))
            if y != n-1:
                linker.add(map_positions(x, y + 1, m))
            map_dict[map_positions(x, y, m)] = linker
    return map_dict    


def map_positions(x, y, m):
    """
     A small function for my sanity, i want to call the x and y of the graph.
    Maps coordinates (x,y) to an absolute rising value
    """
    return y * m + x


def place_random_agents(graph, amount):
    """
    Places an amount of agents randomly on the map.
    """
    if amount > len(graph.keys()) - 1:
        raise ValueError("You cannot place more agents on the graph, than vertecies itself")
    agent_list = []
    for i in range(0, amount):
        agent_pos = random.sample(graph.keys(), 1)[0]
        while agent_pos in agent_list:
            agent_pos = random.sample(graph.keys(), 1)[0]
        agent_list.append(agent_pos)
    return tuple(agent_list)


def place_random_goals_for_two(graph, goals1, goals2):
    """
     Generates a tuple of sets, which corresponds to the goals of agent 1/2
    NOTE THAT I HAVE ALMOST NO RESTRICTION ON GENERATING THESE GOALS
    """
    agent1_goals = set()
    while len(agent1_goals) < goals1:
        goal = random.sample(graph.keys(), 1)[0]
        if goal not in agent1_goals:
            agent1_goals.add(goal)
    agent2_goals = set()
    while len(agent2_goals) < goals2:
        goal = random.sample(graph.keys(), 1)[0]
        if goal not in agent2_goals:
            agent2_goals.add(goal)
    return agent1_goals, agent2_goals


def place_real_goal(graph, agents):
    """ Places the real goal randomly on the graph """
    goals = []
    for i in range(0, len(agents)):
        pos = random.sample(graph.keys(), 1)[0]
        while pos in goals:
            pos = random.sample(graph.keys(), 1)[0]
        goals.append(pos)
    return tuple(goals)


def place_random_goals(graph, agents, real_goals, lower_goal_limit, upper_goal_limit):
    """ Generates a tuple of sets, which corresponds to the goals of agent 1/2
    NOTE THAT THERE CAN BE ONLY ONE GOAL ON A VERTEX SIMULATANEOUSLY"""
    if len(graph.keys()) < upper_goal_limit * len(agents):
        raise ValueError("You cannot put more goals into the graph,than verticies itself")
    all_goals = []
    all_goals_of_all_agents = set()
    for agent in agents:
        goal_amount = random.randint(lower_goal_limit, upper_goal_limit)
        goal_list = list()
        goal_list.append(real_goals[agents.index(agent)])
        all_goals_of_all_agents.add(real_goals[agents.index(agent)])
        for i in range(1, goal_amount):
            goal_pos = random.sample(graph.keys(), 1)[0]
            while goal_pos in real_goals or goal_pos in goal_list or goal_pos in all_goals_of_all_agents:
                goal_pos = random.sample(graph.keys(), 1)[0]
            goal_list.append(goal_pos)
            all_goals_of_all_agents.add(goal_pos)
        all_goals.append(set(goal_list))
    return tuple(all_goals)


def delete_vertex(graph, vertex):
    """ Deletes a vertex out of a graph and all of its dependencies """
    for v in graph:
        if vertex in graph[v]:
            graph[v].remove(vertex)
    del graph[vertex]


def generate_paths_for_two(graph, agents, goals):
    """ Generates lists of paths from agents to the corresponding goals """
    paths1 = {}
    paths2 = {}
    # calculate paths for agent 1
    for goal in goals[0]:
        path = dijk.dijkstra(graph, agents[0], goal)
        paths1[goal] = path
    # calculate paths for agent 2
    for goal in goals[1]:
        path = dijk.dijkstra(graph, agents[1], goal)
        paths2[goal] = path
    return paths1, paths2


def generate_paths(graph, agents, goals):
    """Calculates all the paths of the agents """
    path_list = []
    for goal_collection in goals:
        paths = {}
        for goal in goal_collection:
            agent_pos = agents[goals.index(goal_collection)]
            path = dijk.dijkstra(graph, agent_pos, goal)
            paths[goal] = path
        path_list.append(paths)
    return tuple(path_list)


def get_collisions(graph, agents, goals):
    """
    Returns the number of collision of all all agents in the graph
    """
    collisions = 0
    path_collection = []
    for goal_collection in goals:
        paths = []
        for goal in goal_collection:
            path = dijk.dijkstra(graph, agents[goals.index(goal_collection)], goal)
            paths.append(path)
        path_collection.append(paths)
    for agent_paths in path_collection:
        for other_agent_paths in path_collection:
            if agent_paths != other_agent_paths:
                for agent_path in agent_paths:
                    for vertex in agent_path:
                        for other_agent_path in other_agent_paths:
                            if vertex in other_agent_path:
                                collisions += 1
                                break
    return collisions


def is_neighbor(graph, u, v):
    """ Tests if v is neighbor of u in graph """
    if v in graph[u]:
        return True
    return False


def is_neighbor_of_path(graph, vertex, path):
    """ Tests if vertex is part of the given path in the given graph"""
    for v in path:
        if is_neighbor(graph, v, vertex):
            return True
    return False


def is_part_of_path(vertex, path):
    """ Tests whether vertex is part of path"""
    if vertex in path:
        return True
    return False


def reduce_not_used_vertices(graph, paths):
    """ Reduces the given graph of all unused vertices
        by checking if a vertex is part of a path, or neighbor of a part of path"""
    copy = graph.copy()
    all_paths = []
    for path_collection in paths:
        for path in path_collection.values():
            all_paths += path
    for vertex in copy.keys():
        if vertex not in all_paths:
            if not is_neighbor_of_path(graph, vertex, all_paths):
                delete_vertex(graph, vertex)


def reduce_not_used_escapes(graph, paths):
    """ Reduces all unused escapes, which means vertices that are neighbors
    of a path, but there is an escape earlier in that specific path """
    all_paths = []
    first_escapes = []
    redundant_escapes = []
    for path_collection in paths:
        for path in path_collection.values():
            all_paths += path
    for path_collection in paths:
        for path in path_collection.values():
            first_escape = None
            for vertex in path[::-1]:
                for neighbor in graph[vertex]:
                    if neighbor not in all_paths:
                        first_escape = neighbor
                        if neighbor is not None:
                            if neighbor not in redundant_escapes:
                                redundant_escapes.append(neighbor)
            first_escapes.append(first_escape)
    for escape in redundant_escapes:
        if escape not in first_escapes:
            delete_vertex(graph, escape)


def generate_problem_instance(n, m, agent_amount, lower_goal_amount, upper_goal_amount):
    """
    Generates a dict of all the required information to create a problem instance
    """
    data = {}
    graph = generate_grid(n, m)
    agents = place_random_agents(graph, agent_amount)
    real_goals = place_real_goal(graph, agents)
    goals = place_random_goals(graph, agents, real_goals, lower_goal_amount, upper_goal_amount)
    paths = generate_paths(graph, agents, goals)
    reduce_not_used_vertices(graph, paths)
    reduce_not_used_escapes(graph, paths)
    data["collisions"] = get_collisions(graph, agents, goals)
    data["goals"] = goals
    data["Paths"] = paths
    data["real_goals"] = real_goals
    data["agents"] = agents
    data["graph"] = graph
    ("Graph:\n", graph_print(graph), "\nagents:\t", agents,
     "\nreal_goals:\t", real_goals, "\nreal_gaols\t", goals)
    return data


def graph_print(graph):
    """ s the graph in a reasonable manner so i can keep some sanity debugging this mess"""
    output = "graph = {"
    for key in graph.keys():
        output += "\t"
        output += str(key)
        output += ": {"
        count = 0
        for value in graph[key]:
            if count != 0:
                output += ", "
                output += str(value)
            else:
                output += str(value)
            count += 1
        output += "},\n"
    output = output[0:len(output)-2]
    output += "}"
    return output
