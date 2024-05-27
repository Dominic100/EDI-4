import time

class AdaptiveSignalController:
    def __init__(self, intersections):
        self.intersections = intersections
        self.cycle_time = 60

    def collect_traffic_data(self):
        traffic_data = {}
        for intersection in self.intersections:
            traffic_data[intersection.id] = intersection.get_traffic_data()
        return traffic_data

    def analyze_traffic_data(self, traffic_data):
        analysis = {}
        for intersection_id, data in traffic_data.items():
            current_state = self.get_current_state(data)
            predicted_state = self.get_predicted_state(data)
            analysis[intersection_id] = (current_state, predicted_state)
        return analysis

    def get_current_state(self, data):
        return data['current']

    def get_predicted_state(self, data):
        return data['predicted']

    def optimize_signal_timing(self, analysis):
        timings = {}
        for intersection_id, states in analysis.items():
            current_state, predicted_state = states
            green_times = self.allocate_green_times(current_state, predicted_state)
            timings[intersection_id] = green_times
        return timings

    def allocate_green_times(self, current_state, predicted_state):
        green_times = [15, 15, 15, 15]
        if current_state['east_west_queue'] > current_state['north_south_queue']:
            green_times[0] = 20
            green_times[1] = 20
        else:
            green_times[2] = 20
            green_times[3] = 20
        return green_times

    def adjust_signal_timing(self, timings):
        for intersection_id, green_times in timings.items():
            intersection = self.get_intersection_by_id(intersection_id)
            intersection.set_signal_timing(green_times)

    def get_intersection_by_id(self, intersection_id):
        for intersection in self.intersections:
            if intersection.id == intersection_id:
                return intersection
        return None

    def run(self):
        while True:
            traffic_data = self.collect_traffic_data()
            analysis = self.analyze_traffic_data(traffic_data)
            timings = self.optimize_signal_timing(analysis)
            self.adjust_signal_timing(timings)
            time.sleep(self.cycle_time)

class Intersection:
    def __init__(self, id):
        self.id = id

    def get_traffic_data(self):
        return {'current': {'east_west_queue': 10, 'north_south_queue': 5}, 'predicted': {}}

    def set_signal_timing(self, green_times):
        pass


