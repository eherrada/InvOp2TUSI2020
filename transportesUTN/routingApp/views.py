from __future__ import print_function
from django.shortcuts import render
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from django.views.decorators.csrf import csrf_exempt
from .forms import cities_form
from math import inf
from itertools import product

def home(request):
    return render(request, 'services.html')

def tsp(request):
    return render(request, 'tsp.html')

def shortest_path(request):
    return render(request, 'shortest_path.html')

def our_team(request):
    return render(request, 'our_team.html')

def about_us(request):
    return render(request, 'about_us.html')


@csrf_exempt
def travlingSales(request):
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model()

    city_index = ['Chascomus', 'Samborombón', 'Castelli', 'Tandil', 'Balcarce', 'Maipú', 'Mar del Plata',
                'Coronel Vidal', 'Miramar', 'Pinamar', 'Azul', 'Dolores', 'General Guido', 'Lobería']
    city_list_index = []

    city_list = request.POST.getlist('city')
    for i in city_list:
        city_list_index.append(city_index.index(i)+1)
    city_list_index.sort(reverse=True)
    print(city_list_index)

    city_array = remove_list(city_list_index)
    data['distance_matrix'] = remove_cities(data['distance_matrix'], city_list_index)
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)



    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)


    # Print solution on console.
    if solution:
        resultado = print_solution(manager, routing, solution, city_array)
        return render(request, 'results.html', {'resultado': resultado, 'matriz': data['distance_matrix'],
                                               'ciudades': city_array})

def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = [
        [0, 81, 48, 144, 386, 371, 236, 370, 303, 411, 312, 293, 171, 209, 401],
        [81, 0, 52, 65, 307, 291, 157, 291, 220, 327, 228, 263, 88, 125, 362],
        [48, 52, 0, 116, 303, 323, 208, 342, 275, 383, 284, 257, 143, 181, 357],
        [144, 65, 116, 0, 246, 230, 96, 230, 163, 271, 171, 248, 31, 69, 300],
        [386, 307, 303, 246, 0, 108, 152, 173, 175, 202, 221, 101, 218, 178, 117],
        [371, 291, 323, 230, 108, 0, 136, 74, 76, 94, 205, 206, 202, 163, 85],
        [236, 157, 208, 96, 152, 136, 0, 136, 137, 177, 120, 175, 69, 29, 221],
        [370, 291, 342, 230, 173, 74, 136, 0, 67, 45, 126, 271, 200, 161, 171],
        [303, 220, 275, 163, 175, 76, 137, 67, 0, 109, 138, 96, 136, 97, 152],
        [411, 327, 383, 271, 202, 94, 177, 45, 109, 0, 170, 299, 256, 217, 142],
        [312, 228, 284, 171, 221, 205, 120, 126, 138, 170, 0, 306, 142, 146, 290],
        [293, 263, 257, 248, 101, 206, 175, 271, 96, 299, 306, 0, 304, 265, 214],
        [171, 88, 143, 31, 218, 202, 69, 200, 136, 256, 142, 304, 0, 42, 273],
        [209, 125, 181, 69, 178, 163, 29, 161, 97, 217, 146, 265, 42, 0, 248],
        [401, 362, 357, 300, 117, 85, 221, 171, 152, 142, 290, 214, 273, 248, 0],
    ]  # yapf: disable
    data['num_vehicles'] = 1
    data['depot'] = 0
    return data


def remove_cities(data_model, city_list):
    city_matrix = data_model
    for city in city_list:
        for i in city_matrix:
            i.pop(city)
        city_matrix.pop(city)
    return city_matrix

def remove_list(city_list):
    city_array = ['La Plata', 'Chascomus', 'Samborombón ', 'Castelli', 'Tandil', 'Balcarce', 'Maipú', 'Mar del Plata',
                    'Coronel Vidal', 'Miramar', 'Pinamar', 'Azul', 'Dolores', 'General Guido', 'Lobería']
    for city in city_list:
        city_array.pop(city)
    return city_array



def print_solution(manager, routing, solution, city_array):
    """Prints solution on console."""
    print('Objective: {} miles'.format(solution.ObjectiveValue()))
    index = routing.Start(0)
    plan_output = 'Ruta del vehiculo :\n'
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += city_array[index]+' -> '
        #plan_output += ' {} ->'.format(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    #plan_output += ' {}\n'.format(manager.IndexToNode(index))
    plan_output += ' La Plata\n'
    plan_output += ' ||  Distancia Recorrida: {} Kms\n'.format(route_distance)
    return plan_output

def floyd_warshall(n, edge):
    response=[]
    rn = range(n)
    dist = [[inf] * n for i in rn]
    nxt = [[0] * n for i in rn]
    for i in rn:
        dist[i][i] = 0
    for u, v, w in edge:
        dist[u - 1][v - 1] = w
        nxt[u - 1][v - 1] = v - 1
    for k, i, j in product(rn, repeat=3):
        sum_ik_kj = dist[i][k] + dist[k][j]
        if dist[i][j] > sum_ik_kj:
            dist[i][j] = sum_ik_kj
            nxt[i][j] = nxt[i][k]
    
    for i, j in product(rn, repeat=2):
        if i != j:
            path = [i]
            while path[-1] != j:
                path.append(nxt[path[-1]][j])
            response.append("%3d → %3d|%4d|%s"
                  % (i + 1, j + 1, dist[i][j],
                     ' → '.join(str(p + 1) for p in path)))
    return response

def spresult(request):
    
    city_list = request.POST.getlist('city')
    rute = "  "+city_list[0] +" →   "+city_list[1]
    
    rta = floyd_warshall(8, [[1, 3, 48], [2, 1, 81], [2, 3, 52], [4, 2, 65], [3, 5, 303], [5, 6, 108],[5, 7, 152] ,[6, 8, 74],[7, 4, 96],[8, 7, 135]])
    temp = []
    for i in rta:
        temp.append(i.split("|"))
    
    for i in temp:
        if i[0] == rute:
            cityString = i[0].replace("1","La Plata").replace("2","Chascomus").replace("3","Samboronbon").replace("4","Castelli").replace("5","Tandil").replace("6","Balcarce").replace("7","Maipu").replace("8","Mar del Plata").replace("→","hasta")
            km = i[1]
            direction = i[2].replace("1","La Plata").replace("2","Chascomus").replace("3","Samboronbon").replace("4","Castelli").replace("5","Tandil").replace("6","Balcarce").replace("7","Maipu").replace("8","Mar del Plata")
            
            return render(request, 'spresult.html',{'ciudades': cityString,'kms':km,'ruta':direction})


    


    