import random

import matplotlib.pyplot as plt
import numpy
from deap import creator, base, tools

from src.cost_func import cost_func as evaluate
from src.crossover import crossover_in_place as mate
from src.mutate import mutate_in_place as mutate
from src.schedule_generator import init_generation, makeGraph

# Creating abstract fitness function, with two objective minimizer
creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))

# Creating an individual that inherits the list type, with a nb_mach attribute
creator.create("Individual", list, fitness=creator.FitnessMin)

# Initializing variables
NB_POP, MAX_MACH = 10, 10
MACHINES_MUTATION_PROBABILITY = 0.2
MUTATION_PROBABILITY = 0.1
CXPB = 0.5
MUTPB = 0.5
NGEN = 100

# Let us build the graph only once in order to save time
graph_name = "mediumRandom"
task_graph = makeGraph(graph_name)


def initChromosome(icls, content):
    """icls : class of the individual (i.e. "creator.Individual" in this case) """
    return icls(content)


def initPopulation(pcls, ind_init, filename):
    """
    pcls : class of the population (i.e. a toolbox attribute of an individual)
    ind_init : function to initialize individuals
    filename : the name of the graph file we want to use (for now use only smallRandom or mediumRandom)

    return : a list of individuals
    """
    contents = init_generation(NB_POP, MAX_MACH, task_graph)
    return pcls(ind_init(c) for c in contents)


# Creating and registering toolbox
toolbox = base.Toolbox()
toolbox.register("individual_guess", initChromosome, creator.Individual)
toolbox.register("population_guess", initPopulation, list, toolbox.individual_guess, graph_name)
toolbox.register("mutate", mutate, MUTATION_PROBABILITY, MACHINES_MUTATION_PROBABILITY)
toolbox.register("mate", mate)
toolbox.register("evaluate", evaluate, task_graph)
toolbox.register("select", tools.selTournament, tournsize=3)

# Creating and registering stats
stats = tools.Statistics(key=lambda ind: ind.fitness.values)
stats.register("avg", numpy.mean)
stats.register("std", numpy.std)
stats.register("min", numpy.min)
stats.register("max", numpy.max)

# Creating the population
pop = toolbox.population_guess()

# Creating a logbook for recording statistics
logbook = tools.Logbook()

# To the heart of the genetic algorithm

for g in range(NGEN):
    # Select the next generation individuals
    offspring = toolbox.select(pop, len(pop))
    # Clone the selected individuals
    offspring = [toolbox.clone(ind) for ind in offspring]

    # Apply crossover on the offspring
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < CXPB:
            toolbox.mate(child1, child2)
            del child1.fitness.values
            del child2.fitness.values

    # Apply mutation on the offspring
    for mutant in offspring:
        if random.random() < MUTPB:
            toolbox.mutate(mutant)
            del mutant.fitness.values

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # The population is entirely replaced by the offspring
    pop[:] = offspring

    # Recording statistics
    record = stats.compile(pop)
    logbook.record(gen=g, evals=len(invalid_ind), **record)

# logbook.header = "gen", "evals", "avg", "min", "max"
# print(logbook)

gen = logbook.select("gen")
fit_mins = logbook.select("min")
# size_avgs = logbook.chapters["size"].select("avg")



fig, ax1 = plt.subplots()
line1 = ax1.plot(gen, fit_mins, "b-", label="Minimum Fitness")
ax1.set_xlabel("Generation")
ax1.set_ylabel("Fitness", color="b")
for tl in ax1.get_yticklabels():
    tl.set_color("b")

# ax2 = ax1.twinx()
# line2 = ax2.plot(gen, size_avgs, "r-", label="Average Size")
# ax2.set_ylabel("Size", color="r")
# for tl in ax2.get_yticklabels():
#     tl.set_color("r")

lns = line1  # + line2
labs = [l.get_label() for l in lns]
ax1.legend(lns, labs, loc="center right")

plt.show()
