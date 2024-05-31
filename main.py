from geneticAlgo import GeneticAlgo
from customer import Customer
from depot import Depot
from vehicle import Vehicle

#Capacitated Multi Depot Vehicle Routing Problem
MDVRP = GeneticAlgo(2, 15, 4, 10, 200, 10)
MDVRP.genetic_solve()
print("Best solution: ")
print(MDVRP.best_solution)
MDVRP.plot_results()