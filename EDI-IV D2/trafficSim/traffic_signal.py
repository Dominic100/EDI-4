import random
import time
from .road import Road

class TrafficSignal:
    def __init__(self, roads, config={}):
        # Initialize roads
        self.roads = roads
        # Set default configuration
        self.set_default_config()
       
        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)
        # Calculate properties
        self.init_properties()
        self.time = time.time()
        self.last_green_time = {i: 0 for i in range(len(self.roads))}
        self.last_update_time = 0  # Initialize the last update time

    def update_time(self):
        self.time = time.time()

    def set_default_config(self):
        self.traffic_matrix = [[0, 0, 1, 0, 1, 0, 0, 1],
                               [0, 0, 0, 1, 1, 1, 0, 0],
                               [1, 0, 0, 0, 0, 1, 1, 0],
                               [0, 1, 0, 0, 0, 0, 1, 1],
                               [1, 1, 0, 0, 0, 0, 1, 0],
                               [0, 1, 1, 0, 0, 0, 0, 1],
                               [0, 0, 1, 1, 1, 0, 0, 0],
                               [1, 0, 0, 1, 0, 1, 0, 0]]
        self.new_cycle = []
        self.cycle = [(False, True, False, True), (False, False, True, False), (False, True, False, False), (True, False, False, False)]
        for i in range(8):
            for j in range(i, 8):
                temp = [False, False, False, False, False, False, False, False]
                if(self.traffic_matrix[i][j]==1):
                    temp[i] = True
                    temp[j] = True
                    self.new_cycle.append(temp)
                                
        self.slow_distance = 50
        self.slow_factor = 0.4
        self.stop_distance = 12
        self.traffic = 0

        self.current_cycle_index = 0

        self.last_t = 0

    def init_properties(self):
        for i in range(len(self.roads)):
            for road in self.roads[i]:
                road.set_traffic_signal(self, i)

    @property
    def current_cycle(self):
        return self.new_cycle[self.current_cycle_index]
    
    def update(self, sim):         
        if len(self.roads) > 1:
            current_time = time.time()
            avg_num_vehicles = []
            for i in range(len(self.roads)):
                avg_num_vehicles.append(sum([road.get_num_vehicles() for road in self.roads[i]]) / len(self.roads[i]))

            s = 0
            ind1 = 0 
            ind2 = 0
            max_density_index1 = 0
            max_density_index2 = 0
            ind = 0
            flag = False
            
            for i in range(12):
                for j in range(8):
                    if(self.new_cycle[i][j] == True):
                        ind2 = ind1
                        ind1 = j
                    
                if(s < (avg_num_vehicles[ind1] + avg_num_vehicles[ind2])):
                    s = avg_num_vehicles[ind1] + avg_num_vehicles[ind2]
                    max_density_index1 = ind1
                    max_density_index2 = ind2
                    ind = i
                
                ind1 = 0
                ind2 = 0
                
            for i in range(len(self.roads)):
                for road in self.roads[i]:
                    num_vehicles = road.get_num_vehicles()
                    if num_vehicles != 0:
                        vehicles = road.get_vehicles()
                        for vehicle in vehicles:
                            if vehicle.vehicleType == "emergency":
                                max_density_index1 = i
                                flag = True
                                break
                            else:
                                flag = False
                        
            if flag:
                tempind = []
                for j in range(max_density_index1, 8):
                    if self.new_cycle[max_density_index1][j]==True:
                        tempind.append(j)
                        
                max_density_index2 = avg_num_vehicles.index(max(avg_num_vehicles[j] for j in tempind))

            sTotal = 0
            for i in range(len(avg_num_vehicles)):
                sTotal += avg_num_vehicles[i]
            
            s = int(s)
            if s == 0:
                s = 1
            cycle_length = 100 * s
            if sim.t % cycle_length == 0:
                cycle_length = random.randint(20, 40) / (s + 1e-8)

            if current_time - self.last_update_time > 3:  # Ensure 5 seconds gap before updating
                if (current_time - self.last_green_time[max_density_index1] > 3) and (current_time - self.last_green_time[max_density_index2] > 3):
                    self.current_cycle_index = ind
                    self.last_update_time = current_time  # Update the last update time

            if len(self.roads) < 4:
                self.current_cycle_index = 0

            self.update_time()
            self.last_green_time[self.current_cycle_index] = current_time
            
        else:
            cycle_length = 20
        
            if sim.t % cycle_length == 0:
                cycle_length = random.randint(20, 40)
            k = (sim.t // cycle_length) % 4
            self.current_cycle_index = int(k)
            if len(self.roads) < 4:
                self.current_cycle_index = 0
