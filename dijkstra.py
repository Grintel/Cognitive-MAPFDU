# Copyright 2019 (C) Lukas Berger [lukas.berger@uranus.uni-freiburg.de]
# used https://de.wikipedia.org/wiki/Dijkstra-Algorithmus as reference for my implementation

from math import inf as infinity


def dijkstra(graph, start, goal):
    """ Returns the shortest Path to the goal as a list"""
    distances = {}
    predecessors = {}
    q = {}
    initialize(graph, start, distances, predecessors, q)
    iteration = 0
    while (len(q) >= 1):

        u = find_smallest_distance(q, distances)
        if u == goal:
            break
        del q[u]
        for neighbor in graph[u]:
            if neighbor in q:
                update_distance(u, neighbor, distances, predecessors)
        iteration += 1
    return get_path(start, goal, predecessors)


def initialize(graph, start, distances, predecessors, q):
    """Initialize all the values for dijkstra"""
    for vertex in graph:
        distances[vertex] = infinity
        predecessors[vertex] = None
        q[vertex] = 0
    distances[start] = 0


def update_distance(u, v, distances, predecessors):
    """Update the distance of v, if the new found path is shorter"""
    alt = distances[u] + 1
    if alt < distances[v]:
        distances[v] = alt
        predecessors[v] = u


def find_smallest_distance(q, distances):
    """ finds the vertex in q with the smallest distance"""
    min_dist = infinity
    min_vertex = None
    for vertex in q:
        if distances[vertex] < min_dist:
            min_vertex = vertex
            min_dist = distances[vertex]
            return min_vertex


def get_path(start, goal, predecessors):
    """ Returns the Path from start to goal as a list """
    pred = goal
    path = []
    while pred != start:
        pred = predecessors[pred]
        path.append(pred)
    path.insert(0, goal)
    path = list(reversed(path))
    return path
