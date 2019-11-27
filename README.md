# Cognitive-MAPFDU
Here lies the code to the cognitive agent for multi-agent path finding under destination uncertanty.

## Usage of the agent
### Initialize the agents
In order to test this agent, one must provide a problem instance, which consist of a Graph **_g_**, a tuple of initial positions **_agent\_pos_** a tuple of sets of goals **_goals_** and a tuple of real goals **_real\_goals_**, where the tuple index corresponds with the index in **_agent\_pos_**. Not that **_goals_** must contain Let us look at the example:

```python
from Agent import Agent
from Solver import solve

G = {0 : {1, 3},
     1 : {0, 2, 4},
     2 : {1, 5}
     3 : {0, 4},
     4 : {1, 3 ,5},
     5 : {2, 4}} 

agent_pos = (0, 5)
goals = ({1,3}, {4,5})
real_goals (1, 5)
```
 Let us make a list to store the agents. To initialize the agents just loop though all positions and then use **_init\_agents_** to feed them the informations about the other agents positions and goals.
 
 ```python
 agents = []
for pos in agent_pos:
    current_index = agent_pos.index(pos)
    agents.append(Agent(G, index, pos, real_goals[index], goals[index]))
for agent in agents:
    agent.init_agents(agents)
```
### Solving the instance
After you initialized the agents you can simply use **_Solver.solve_** to make them try to solve the given instance.
 ```python
solve(agents=agents, max_rounds=100, verbosity=False)
```
The **_max_rounds_** paramter determines after how many rounds the calculation will be aborted, because, unfortunatenly, infinite executions are possible, although unlikely. If the **_verbosity_** parameter is set to **_True_**. A console output for every agent in every round will be displayed. This can be used to comprehend the agents behavior or simply for debugging purposes.
## Generating a random problem instance
Let us look at the randomly generated problem instances **_GraphGenerator_**. The funciton **_generate\_problem\_instance(n, m, agent\_amount, lower\_goal\_amount, upper\_goal\_amount)_** will geneate n X m graph, then it will place the agents and goals randomly on the graph.The agent amount defines how many agents the problem instance will have. The amount of goals per agents can be adjusted using the **_lower\_goal\_amount_** and the **_upper\_goal\_amount_** parameter.
Here is an example of generating an initialized problem instance.
 ```python
from GraphGenerator imort generate_problem_instance as gpi
from Solver import initialize

n = 5
m = 5
agent_amount = 3
lower_goal_amount = 2
upper_goal_amount = 4
instance = gpi(m, n, agent_amount, lower_goal_amount, upper_goal_amount)
 agents = initialize(instance)
```
From that on, one can solve the given instance, by simply using the solve function again:
After you initialized the agents you can simply use **_Solver.solve_** to make them try to solve the given instance.
 ```python
solve(agents=agents, max_rounds=100, verbosity=False)
```
