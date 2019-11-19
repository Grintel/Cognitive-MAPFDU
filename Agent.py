# Copyright 2019 (C) Lukas Berger [lukas.berger@uranus.uni-freiburg.de]

import dijkstra as dijk
from math import inf as infinity
from GraphGenerator import delete_vertex


class Agent:
    """
    Realization of the agent
    """

    def __init__(self, graph, id, pos, real_goal, goals):
        self.graph = graph
        self.id = id
        self.pos = pos
        self.real_goal = real_goal
        self.goal_path = dijk.dijkstra(self.graph, self.pos, self.real_goal)
        self.goals = goals
        self.agents = {}
        self.escape = None
        self.escaping = False
        self.escape_path = []
        self.all_paths = []
        self.finished = False

    def __str__(self):
        output = f"ID:{self.id}\n"
        output += f"\tPos:\t{self.pos}\n"
        output += f"\tGoal:\t{self.real_goal}\n"
        output += f"\tPath:\t{self.goal_path}\n"
        output += f"\tEscaping:\t{self.escaping}\n"
        output += f"\tEscapePath:\t{self.escape_path}"
        return output

    def get_pos(self):
        return self.pos

    def get_goal(self):
        return self.real_goal

    def get_id(self):
        return self.id

    def get_goals(self):
        return self.goals

    def get_goal_path(self):
        return self.goal_path()

    def set_escape(self, escape):
        self.escape = escape

    def update_all_paths(self):
        """
        updates the paths of the other agents. Agents that are waiting or on goals have no paths
        """
        self.all_paths = []
        for agent in self.agents.values():
            for goal in agent.get_goals():
                if not agent.goals[goal] and not agent.on_goal and not agent.waiting:
                    self.all_paths.append(agent.paths[goal])

    def init_agents(self, agents):
        """
        The representation for agents (a dict with id for key and tuple with
        the current pos and the set of goals)
        """
        for a in agents:
            if a.get_id() != self.get_id():
                agent = self.ReducedAgent(a)
                self.agents[a.get_id()] = agent

    def update_agents(self, agents):
        """
        Updates all agents and checks if an agent is waiting or if it moved
        away from a goal
        """
        if not self.on_goal():
            for a in agents:
                if self.get_id() != a.get_id():
                    # check if agent is on goal_list
                    if a.on_goal():
                        self.agents[a.get_id()].pos = a.get_pos()
                        self.agents[a.get_id()].on_goal = True
                        # print(f"agent {self.get_id()} knows agent {a.get_id()} is on goal")
                        for goal in self.agents[a.get_id()].get_goals():
                            self.agents[a.get_id()].goals[goal] = True
                        if a.get_pos() in self.graph.keys():
                            delete_vertex(self.graph, a.get_pos())
                    else:
                        agent = self.ReducedAgent(a)
                        agent.waited_since = self.agents[a.get_id()].waited_since
                        # check for position change
                        if self.agents[a.get_id()].get_pos() == agent.get_pos():
                            agent.waited_since += 1
                            if agent.waited_since > 1:
                                agent.waiting = True
                                # print(f"agent {self.get_id()} thinks agent {a.get_id()} is waiting")
                        # check if distance to goals has changed to find out whether the agents
                        # has to ignore this goal or not
                        if not agent.waiting:
                            for goal in agent.get_goals():
                                if len(agent.paths[goal]) > len(self.agents[a.get_id()].paths[goal]):
                                    agent.goals[goal] = True
                                    agent.waited_since = 0
                                if len(agent.paths[goal]) < len(self.agents[a.get_id()].paths[goal]):
                                    agent.goals[goal] = False
                                    agent.waited_since = 0
                        else:
                            for goal in agent.get_goals():
                                agent.goals[goal] = True
                        self.agents[a.get_id()] = agent

    def move_on_goal_path(self):
        """
        Agent moves on the next index on its goal path if it is already on,
        creates a new goal path otherwise
        """
        moved = False
        if not self.on_goal():
            already_taken = False
            if len(self.goal_path) <= 1:
                self.update_goal_path()
            if self.goal_path[1] in self.graph[self.pos]:
                for agent in self.agents.keys():
                    if self.agents[agent].get_pos() == self.goal_path[1]:
                        already_taken = True
                        # print(f"ALREADY TAKEN by {agent}")
                if not already_taken:
                    # print(f"agent: {self.get_id()} moved from {self.get_pos()} to {self.goal_path[1]}")
                    moved = self.move_to(self.goal_path[1])
                    self.update_goal_path()
            else:
                self.update_goal_path()
                self.move_on_goal_path()
        return moved

    def update_goal_path(self):
        """ calculates new goal path from current position"""
        self.goal_path = dijk.dijkstra(self.graph, self.pos, self.real_goal)

    def move_on_escape_path(self):
        """ lets the agent move on its escape path """
        moved = False
        if not self.on_escape():
            already_taken = False
            if self.escape_path[1] in self.graph[self.pos]:
                for agent in self.agents.keys():
                    if self.agents[agent].get_pos() == self.escape_path[1]:
                        already_taken = True
                if not already_taken:
                    # print(f"agent: {self.get_id()} moved from {self.get_pos()} to {self.escape_path[1]}"
                    moved = self.move_to(self.escape_path[1])
                    self.update_escape_path()
            else:
                self.update_escape_path()
                self.move_on_escape_path()
        return moved

    def update_escape_path(self):
        """ calculates new path to the current escape """
        self.escape_path = dijk.dijkstra(self.graph, self.pos, self.escape)

    def on_goal(self):
        """
        returns if agent is om goal
        :return: bool
        """
        if self.pos == self.real_goal:
            return True
        return False

    def on_escape(self):
        """
        returns if agent is on escape
        :return: bool
        """
        if self.pos == self.escape:
            return True
        return False

    def has_collision(self, agent_id):
        """
        Agent checks if its own goal path is in collision to all the
        goal paths of the other agent
        """
        paths = self.calculate_goal_paths(agent_id)
        for vertex in self.goal_path:
            for path in paths:
                if vertex in path:
                    return True
        return False

    def calculate_goal_paths(self, agent_id):
        """ Calculates paths to all goals of agent"""
        paths = []
        for goal in self.agents[agent_id].get_goals():
            if not self.agents[agent_id].goals[goal]:
                path = dijk.dijkstra(self.graph, self.agents[agent_id].get_pos(), goal)
                paths.append(path)
        return paths

    def find_nearest_escape(self, pos):
        """ searches for an escape which is a vertex which is on no path of all
        goal paths of all agents"""
        on_path = set()
        escapes = set()
        for path in self.all_paths:
            for vertex in path:
                on_path.add(vertex)
        for vertex in self.graph.keys():
            if vertex not in on_path:
                escapes.add(vertex)
        min_dist = infinity
        min_escape = None
        for escape in escapes:
            distance = len(dijk.dijkstra(self.graph, pos, escape))
            if distance < min_dist:
                min_dist = distance
                min_escape = escape
        return min_escape

    def must_escape(self, agent_id):
        """
        Tests whether an agent has to escape or not according to its distance
        to the next escape
        """
        if self.has_collision(agent_id):
            escape = self.find_nearest_escape(self.pos)
            a_escape = self.find_nearest_escape(self.agents[agent_id].get_pos())
            if escape is not None:
                escape_path = dijk.dijkstra(self.graph, self.pos, escape)
                own_distance = len(escape_path)
                other_distance = len(dijk.dijkstra(self.graph, self.agents[agent_id].get_pos(), a_escape))
                if own_distance < other_distance:
                    return True, escape
                if own_distance > other_distance:
                    return False, escape
                if own_distance == other_distance:
                    if self.get_id() < agent_id:
                        return True, escape
                    else:
                        return False, escape
        return False, None

    def check_for_escaping(self):
        """ checks if agent must escape """
        if not self.on_goal():
            escaping = False
            agents_not_on_goals = 0
            for agent in self.agents.keys():
                if not self.agents[agent].on_goal:
                    agents_not_on_goals += 1
                    esc_tuple = self.must_escape(agent)
                    self.escaping = esc_tuple[0] or escaping
                    self.escape = esc_tuple[1]
                    if self.escaping:
                        self.update_escape_path()
                    else:
                        self.update_goal_path()
            if agents_not_on_goals == 0:
                self.escaping = False
                self.update_goal_path()

    def move(self):
        """ lets the agent move according to its current state (escaping or running to the goal) """
        moved = False
        for agent_id in self.agents.keys():
            if self.get_pos() == self.agents[agent_id].get_pos():
                raise self.AlreadyTakenError(f"Agent {self.get_id()} and \
                Agent {agent_id} are on the same position ")
        if not self.escaping:
            moved = self.move_on_goal_path() or moved
        elif not self.on_goal():
            moved = self.move_on_escape_path() or moved
        if not moved:
            self.immediate_escape()

    def move_to(self, vertex):
        """ Changes the agents position after checking if it is blocked by another agent """
        for agent in self.agents.keys():
            if self.agents[agent].get_pos() == vertex:
                raise self.AlreadyTakenError(f"Invalid move from agent {self.get_id()} \
                , {vertex} is already taken by {agent}")
        if vertex not in self.graph[self.get_pos()]:
            raise ValueError(f"{vertex} is no neighbor of {self.get_pos()}")
        # print(f"agent: {self.get_id()} moved from {self.get_pos()} to {vertex}")
        self.pos = vertex
        return True

    def get_all_agent_pos(self):
        """ Returns a Generator for agent position generator """
        for agent in self.agents.keys():
            yield self.agents[agent].get_pos()

    def immediate_escape(self):
        """
        In case of a collision of an agent, the agent finds the best suited immediate escape
        (an escape next to the agents position) and moves on it.
        This unfortunately happens more often than i anticipated.
        """
        if not self.on_goal():
            blocked_vertex = []
            for agent in self.agents.values():
                for vertex in self.graph[self.get_pos()]:
                    if not agent.on_goal:
                        if agent.get_pos() == vertex:
                            blocked_vertex.append(vertex)
            if len(blocked_vertex) > 0:
                all_vertices = self.get_all_vertices_on_paths()
                best_escape = set()
                ok_escape = set()
                bad_escape = set()
                for escape in self.graph[self.get_pos()]:
                    if escape not in blocked_vertex:
                        if escape not in all_vertices:
                            if escape in self.goal_path:
                                best_escape.add(escape)
                            ok_escape.add(escape)
                        bad_escape.add(escape)
                if len(best_escape) > 0:
                    self.move_to(best_escape.pop())
                    self.update_goal_path()
                    return
                if len(ok_escape) > 0:
                    self.move_to(ok_escape.pop())
                    self.update_goal_path()
                    return
                if len(bad_escape) > 0:
                    self.move_to(bad_escape.pop())
                    self.update_goal_path()

    def get_all_vertices_on_paths(self):
        """ Returns all the vertices of the paths of the agents, despite it being waiting"""
        vertices_on_paths = set()
        for agent in self.agents.values():
            vertices_on_paths.add(agent.get_pos())
            if not agent.on_goal:
                for path in agent.paths.values():
                    for vertex in path:
                        vertices_on_paths.add(vertex)
        return vertices_on_paths

    class ReducedAgent:
        """ The representation of the other agents within the agent itself"""
        def __init__(self, agent):
            self.pos = agent.get_pos()
            self.goals = {}
            self.paths = {}
            self.waited_since = 0
            self.waiting = False
            self.on_goal = False
            for goal in agent.get_goals():
                self.goals[goal] = False
                self.paths[goal] = dijk.dijkstra(agent.graph, self.pos, goal)

        def get_paths(self):
            return self.paths

        def get_goals(self):
            return self.goals.keys()

        def get_pos(self):
            return self.pos

    class AlreadyTakenError(Exception):
        pass
