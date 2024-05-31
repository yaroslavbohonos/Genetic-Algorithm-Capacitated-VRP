from depot import Depot
from customer import Customer
from vehicle import Vehicle
import numpy as np
from visual import plot_routes_fitness
import random
from copy import deepcopy

class GeneticAlgo():
    def __init__(self, depots_amount, customers_amount, vehicles_amount, population_size, generations, customer_capacity):
        self.depots = self.generate_unique_depots([Depot(i, np.random.rand() * 100, np.random.rand() * 100,) for i in range(depots_amount)])
        self.customers = self.generate_unique_customers([Customer(i, np.random.rand() * 100, np.random.rand() * 100, customer_capacity) for i in range(customers_amount)])
        self.vehicles = [Vehicle(i, (customer_capacity*customers_amount) // vehicles_amount) for i in range(vehicles_amount)]
        self.distance_matrix = self.create_distance_matrix(self.depots, self.customers)
        self.population_size = population_size
        self.generations = generations
        self.population = self.initial_population()
        self.fitness_values = []
        self.best_solution = random.choice(self.population)
        self.threshold_population_size = 40

    def generate_unique_depots(self, depots):
        unique_coords = set()
        for depot in depots:
            while (depot.x, depot.y) in unique_coords:
                depot.x = np.random.rand() * 100
                depot.y = np.random.rand() * 100
            unique_coords.add((depot.x, depot.y))
        return depots

    def generate_unique_customers(self, customers):
        unique_coords = set((depot.x, depot.y) for depot in self.depots)
        for customer in customers:
            while (customer.x, customer.y) in unique_coords:
                customer.x = np.random.rand() * 100
                customer.y = np.random.rand() * 100
            unique_coords.add((customer.x, customer.y))
        return customers

    def create_distance_matrix(self, depots, customers):
        points = depots + customers
        num_points = len(points)
        distance_matrix = np.zeros((num_points, num_points))
        for i in range(num_points):
            for j in range(num_points):
                distance_matrix[i][j] = np.sqrt((points[i].x - points[j].x)**2 + (points[i].y - points[j].y)**2)
        return distance_matrix

    def calculate_fitness(self, solution):
        total_distance = 0
        for route in solution:
            for i in range(len(route) - 1):
                total_distance += self.distance_matrix[route[i]][route[i + 1]]
        return total_distance

    def is_feasible(self, solution):
        visited_customers = set()
        for route in solution:
            if route[0] != route[-1]:
                return False
            for node in route[1:-1]:
                if node < len(self.depots):
                    return False
                visited_customers.add(node - len(self.depots))
        return len(visited_customers) == len(self.customers)

    def create_random_solution(self):
        while True:
            depot_assignments = {depot.id: [] for depot in self.depots}
            for customer in self.customers:
                assigned_depot = random.choice(self.depots)
                depot_assignments[assigned_depot.id].append(customer)

            routes = []
            for depot in self.depots:
                depot_customers = depot_assignments[depot.id]
                random.shuffle(depot_customers)

                for vehicle in self.vehicles:
                    route = [depot.id]
                    capacity_left = vehicle.capacity
                    while depot_customers and depot_customers[0].demand <= capacity_left:
                        customer = depot_customers.pop(0)
                        route.append(customer.id + len(self.depots))
                        capacity_left -= customer.demand
                    route.append(depot.id)
                    routes.append(route)

            if self.is_feasible(routes):
                return routes

    def initial_population(self):
        population = []
        for _ in range(self.population_size):
            solution = self.create_random_solution()
            population.append(solution)
        return population

    def binary_tournament_selection(self, sol1, sol2):
        if self.calculate_fitness(sol1) <= self.calculate_fitness(sol2):
            return sol1 
        else:
            return sol2

    def srex_crossover(self, parent1, parent2):
        parent1_routes = [route for route in parent1 if len(route) > 2]
        parent2_routes = [route for route in parent2 if len(route) > 2]
        route1 = random.choice(parent1_routes)
        route2 = random.choice(parent2_routes)
        child1 = deepcopy(parent1)
        child2 = deepcopy(parent2)
        
        for i in range(len(child1)):
            if child1[i] == route1:
                child1[i] = route2
        for i in range(len(child2)):
            if child2[i] == route2:
                child2[i] = route1
        
        return child1, self.calculate_fitness(child1), child2, self.calculate_fitness(child2)

    def mutate(self, solution):
        for route in solution:
            if len(route) > 3:
                idx1, idx2 = random.sample(range(1, len(route) - 1), 2)
                route[idx1], route[idx2] = route[idx2], route[idx1]
        solution_fitness = self.calculate_fitness(solution)
        if self.is_feasible(solution):
            return solution, solution_fitness
        else:
            return self.create_random_solution(), self.calculate_fitness(solution)


    def two_opt(self, route):
        improved = True
        while improved:
            improved = False
            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route) - 1):
                    new_route = route[:i] + route[i:j + 1][::-1] + route[j + 1:]
                    new_fitness = self.calculate_fitness([new_route])
                    if new_fitness < self.calculate_fitness([route]):
                        route = new_route
                        improved = True
                        break
                if improved:
                    break
        return route

    def local_search(self, solution):
        for route_index in range(len(solution)):
            solution[route_index] = self.two_opt(solution[route_index])
        solution_fitness = self.calculate_fitness(solution)
        if self.is_feasible(solution):
            return solution, solution_fitness
        else:
            return self.create_random_solution(), self.calculate_fitness(solution)

    def evolve_population(self):
        for _ in range(self.generations):
            parent1 = self.binary_tournament_selection(random.choice(self.population), random.choice(self.population))
            parent2 = self.binary_tournament_selection(random.choice(self.population), random.choice(self.population))
            child1, _, child2, _ = self.srex_crossover(parent1, parent2)
            child1, _ = self.local_search(child1)
            child2, _ = self.local_search(child2)
            if self.calculate_fitness(child1) < self.calculate_fitness(child2):
                self.population.append(child1)
            else:
                self.population.append(child2)

            if len(self.population) > self.threshold_population_size:
                self.population.sort(key=lambda sol: self.calculate_fitness(sol))
                self.population = self.population[:self.population_size]

            best_fitness = self.calculate_fitness(self.population[0])
            self.fitness_values.append(best_fitness)

            # Update best solution if found
            if best_fitness < self.calculate_fitness(self.best_solution):
                self.best_solution = deepcopy(self.population[0])

    def genetic_solve(self):
        self.evolve_population()

    def plot_results(self):
        plot_routes_fitness(self.depots, self.customers, self.best_solution, self.fitness_values)
