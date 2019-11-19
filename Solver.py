# Copyright 2019 (C) Lukas Berger [berger.lukas01@gmail.com]

import Agent
from mapfdu import mapfdu


def initialize(data):
    """This initializes the Problem instance.
    Data should contain:
    graph: A dictionary of vertices with vertex sets as Neighborhood definition
    agents: Initial position of the agents in a tuple
    real_goals: A tuple of vertices, where the real goals are located on
    goals: All the possible goals as a tuple of sets. Including the real goals
    collisions (optional): the initial amount of collisions. Can be None if necessary
    See the commented example below, to understand how it works."""
    graph = data["graph"]
    agents_positions = data["agents"]
    real_goal = data["real_goals"]
    goals = data["goals"]
    collisions = data["collisions"]
    agents = []
    for agent_pos in agents_positions:
        agent = Agent.Agent(graph, agents_positions.index(agent_pos),
                            agent_pos, real_goal[agents_positions.index(agent_pos)],
                            goals[agents_positions.index(agent_pos)])
        agents.append(agent)
    for a in agents:
        a.init_agents(agents)
    return agents, collisions


def solve(agents, max_rounds, verbosity):
    """
    This implements the round based execution of the agents

    :param agents: The initialized Agent instance.
    :param max_rounds: The maximum of rounds it should take, before aborting the solving process.
    :param verbosity: Console output for better understanding, what is happening.
    :return: Tuple (True, rounds) if it solved the instance. (False, None) Else.
    """
    finished_agents = 0
    rounds = 1
    while finished_agents < len(agents) and rounds < max_rounds:
        if verbosity:
            print(f"rounds: {rounds}\n======================================")
        finished_agents = 0
        if rounds > 1:
            for agent in agents:
                if verbosity:
                    print(agent)
                agent.update_agents(agents)
                agent.check_for_escaping()
                agent.move()
                if agent.on_goal():
                    finished_agents += 1
        else:
            for agent in agents:
                if verbosity:
                    print(agent)
                agent.update_agents(agents)
                agent.check_for_escaping()
                agent.move()
                if agent.on_goal():
                    finished_agents += 1
        rounds += 1
    if finished_agents == len(agents):
        return True, rounds
    return False, None
    # print(f"rounds: {rounds}\n======================================")
    # for agent in agents:
    #    print(agent)

"""
TEST SECTION


gaph = {0: {1, 3},
         1: {0, 2},
         2: {1, 5},
         3: {0},
         5: {8, 2},
         7: {8},
         8: {5, 7}}
agents_pos = (8, 0)
goals = ({0, 2}, {8, 1})
real_goals = (2, 1)


graph = {0: {1},
         1: {0, 2, 4},
         2: {1, 5},
         4: {1, 5, 7},
         5: {2, 4},
         7: {4}
         }
agents_pos = (1, 2)
goals = ({1, 4}, {0, 7})
real_goals = (4, 0)
agents = []
for pos in agents_pos:
    index = agents_pos.index(pos)
    agent = Agent.Agent(graph, index, pos, real_goals[index], goals[index])
    agents.append(agent)
for a in agents:
    a.init_agents(agents)
solve(agents, 50, True)
"""