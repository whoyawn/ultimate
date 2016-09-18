import datetime
import time

import modes

update_interval = 50 # milliseconds

transitions = {
    ('follow', ['time', (datetime.time(23), datetime.time(5, 30))]),
    ('follow', ['time', (datetime.time(5, 30), datetime.time(23))])
}

def update_sensors():
    return [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0]
    ]


def push_colors(colors):
    pass


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

def run():
    current_mode = 'time'
    while True:
        current_time = datetime.time()

        time.sleep(update_interval / 1000)
        sensors = update_sensors()
        push_colors(modes.mode[current_mode](sensors, current_time))



run()

print(modes.mode['time']([[1, 2, 3, 4], [1, 2, 3, 4]], datetime.time(0)))
print(modes.mode['follow']([[1, 0, 0, 0], [0, 0, 1, 0]], datetime.time(0)))