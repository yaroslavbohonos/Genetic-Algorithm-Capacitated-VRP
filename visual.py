import matplotlib.pyplot as plt
import numpy as np

def plot_routes_fitness(depots, customers, best_solution, fitness_values):
    fig, axs = plt.subplots(1, 2, figsize=(15, 6))

    # Plotting Routes
    colors = plt.cm.rainbow(np.linspace(0, 1, len(best_solution)))
    for route, color in zip(best_solution, colors):
        x = [depots[route[0]].x] + [customers[i - len(depots)].x for i in route[1:-1]] + [depots[route[-1]].x]
        y = [depots[route[0]].y] + [customers[i - len(depots)].y for i in route[1:-1]] + [depots[route[-1]].y]
        axs[0].plot(x, y, marker='o', color=color)

    # Plotting depots and customers
    axs[0].scatter([depot.x for depot in depots], [depot.y for depot in depots], c='red', marker='s', label='Depots', s=120)
    axs[0].scatter([customer.x for customer in customers], [customer.y for customer in customers], c='blue', marker='o', label='Customers', s=30)

    axs[0].set_xlabel('X Coordinate')
    axs[0].set_ylabel('Y Coordinate')
    axs[0].set_title('CMDVRP Problem')
    axs[0].legend()

    # Plot fitness over generations
    generations = range(1, len(fitness_values) + 1)
    axs[1].plot(generations, fitness_values, color='green')
    axs[1].set_xlabel('Generation')
    axs[1].set_ylabel('Fitness')
    axs[1].set_title('Fitness over Generations')

    # Make the window non-resizable
    manager = plt.get_current_fig_manager()
    manager.window.resizable(False, False)

    # Show the plot
    plt.show()