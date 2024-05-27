from scipy.spatial import distance
from collections import deque
import time

class Road:
    def __init__(self, start, end):
        self.start = start
        self.end = end

        self.vehicles = deque()

        self.init_properties()
        self.last_green_time = None  # Initialize the last green signal time
        self.has_unstopped = False  # Flag to track if unstop has been called

    def get_num_vehicles(self):
        return len(self.vehicles)
    
    def get_vehicles(self):
        return self.vehicles

    def init_properties(self):
        self.length = distance.euclidean(self.start, self.end)
        self.angle_sin = (self.end[1] - self.start[1]) / self.length
        self.angle_cos = (self.end[0] - self.start[0]) / self.length
        self.has_traffic_signal = False

    def set_traffic_signal(self, signal, group):
        self.traffic_signal = signal
        self.traffic_signal_group = group
        self.has_traffic_signal = True

    @property
    def traffic_signal_state(self):
        if self.has_traffic_signal:
            i = self.traffic_signal_group
            return self.traffic_signal.current_cycle[i]
        return True

    def update(self, dt):
        n = len(self.vehicles)

        if n > 0:
            # Update first vehicle
            self.vehicles[0].update(None, dt)
            # Update other vehicles
            for i in range(1, n):
                lead = self.vehicles[i - 1]
                self.vehicles[i].update(lead, dt)

            current_time = time.time()

            # Check for traffic signal
            if self.traffic_signal_state:
                # Traffic signal is green or doesn't exist
                if self.last_green_time is None:
                    self.last_green_time = current_time  # Record the time the signal turned green
                    self.has_unstopped = False  # Reset the flag when the signal turns green

                if not self.has_unstopped and current_time - self.last_green_time > 1:
                    # Unstop and unslow vehicles if 1 second has passed since the signal turned green
                    self.vehicles[0].unstop()
                    for vehicle in self.vehicles:
                        vehicle.unslow()
                    self.has_unstopped = True  # Set the flag to indicate unstop has been called
            else:
                # Traffic signal is red
                self.last_green_time = None  # Reset the last green time
                self.has_unstopped = False  # Reset the flag when the signal turns red

                if self.vehicles[0].x >= self.length - self.traffic_signal.slow_distance:
                    # Slow vehicles in the slowing zone
                    self.vehicles[0].slow(self.traffic_signal.slow_factor * self.vehicles[0]._v_max)
                if self.vehicles[0].x >= self.length - self.traffic_signal.stop_distance and \
                   self.vehicles[0].x <= self.length - self.traffic_signal.stop_distance / 2:
                    # Stop vehicles in the stop zone
                    self.vehicles[0].stop()
