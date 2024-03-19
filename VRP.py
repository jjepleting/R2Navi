import random
from pyscipopt import Model, quicksum
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPoint
from qgis.utils import iface

# Function to generate random coordinates within a specified range
def generate_random_coordinates(num_points, min_x, max_x, min_y, max_y):
    return [(random.uniform(min_x, max_x), random.uniform(min_y, max_y)) for _ in range(num_points)]

# Function to solve VRP using SCIP
def solve_vrp_scip(depots, customers, capacity):
    model = Model("VehicleRoutingProblem")

    # Decision Variables
    x = {}
    for i in range(len(customers)):
        for j in range(len(customers)):
            x[i, j] = model.addVar(vtype="B", name=f"x[{i},{j}]")

    # Constraints
    for i in range(len(customers)):
        model.addCons(quicksum(x[i, j] for j in range(len(customers))) == 1)

    model.addCons(quicksum(x[i, j] for i in range(len(customers)) for j in range(len(customers))) <= capacity)

    # Objective Function (minimize total distance)
    model.setObjective(quicksum(dist(customers[i], customers[j]) * x[i, j] for i in range(len(customers)) for j in range(len(customers))), "minimize")

    # Solve the problem
    model.optimize()

    # Extract Solution
    solution = []
    for i in range(len(customers)):
        for j in range(len(customers)):
            if model.getVal(x[i, j]) > 0:
                solution.append((i, j))

    return solution

# Function to calculate Euclidean distance between two points
def dist(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

# Function to display solution in QGIS
def display_solution_qgis(solution, depots, customers):
    # Create a new layer for the solution
    layer = QgsVectorLayer("LineString?crs=EPSG:4326", "Optimal Route", "memory")
    provider = layer.dataProvider()

    # Add features to the layer based on the solution
    for i, j in solution:
        feature = QgsFeature()
        start_point = QgsPoint(customers[i][0], customers[i][1])  # Extract x and y coordinates from tuple
        end_point = QgsPoint(customers[j][0], customers[j][1])    # Extract x and y coordinates from tuple
        feature.setGeometry(QgsGeometry.fromPolyline([start_point, end_point]))
        provider.addFeatures([feature])

    # Add the layer to the QGIS map canvas
    QgsProject.instance().addMapLayer(layer)

# Function to generate random data and solve VRP
def generate_and_solve_vrp():
    # Generate random data
    depot_coordinates = (0, 0)
    num_customers = 10
    min_coordinate, max_coordinate = -100, 100
    customer_coordinates = generate_random_coordinates(num_customers, min_coordinate, max_coordinate, min_coordinate, max_coordinate)
    capacity = 30

    # Solve VRP using SCIP
    vrp_solution = solve_vrp_scip([depot_coordinates], customer_coordinates, capacity)

    # Display solution in QGIS
    display_solution_qgis(vrp_solution, [depot_coordinates], customer_coordinates)

# Function to clear data and reset map
def clear_data():
    QgsProject.instance().removeAllMapLayers()

# Create R2Navi menu
menu = QMenu('&R2Navi', iface.mainWindow().menuBar())
menu.setObjectName('R2Navi')
iface.mainWindow().menuBar().insertMenu(iface.mainWindow().menuBar().actions()[-1], menu)

# Create actions for each functionality
generate_action = QAction('Generate Random Data', iface.mainWindow())
generate_action.triggered.connect(generate_and_solve_vrp)
menu.addAction(generate_action)

solve_action = QAction('Solve VRP', iface.mainWindow())
solve_action.triggered.connect(generate_and_solve_vrp)
menu.addAction(solve_action)

display_action = QAction('Display Solution', iface.mainWindow())
display_action.triggered.connect(generate_and_solve_vrp)
menu.addAction(display_action)

clear_action = QAction('Clear Data', iface.mainWindow())
clear_action.triggered.connect(clear_data)
menu.addAction(clear_action)
