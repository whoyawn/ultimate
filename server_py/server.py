import datetime
import time
import pika
import json
import pyrebase

import modes

update_interval = 50 # milliseconds

transitions = {
    #'follow': [
    #    ('time', datetime.time(23), datetime.time(5, 30)) # state, [type of condition, start, end]
    #],
    #'time': [
    #    ('time', datetime.time(5, 30), datetime.time(23))
    #],
    #'alarm': [
    #    ('time', datetime.time(8), datetime.time(8, 2)),
    #    ('time', datetime.time(9), datetime.time(9, 2))
    #]
    'follow': [],
    'time': [],
    'alarm': []
    #('alarm',  ['stock', 'aapl', 250])
}


def update_sensors():
    (method, properties, body) = sensor_channel.basic_get(queue='matrix-sensor', no_ack=False)
    if body is None:
        return None
    else:
        return json.loads(body.decode('utf-8'))


def push_colors(colors):
    color_channel.basic_publish(exchange='',
                                routing_key='matrix-color',
                                body=json.dumps(colors))


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


## Setting up RabbitMQ connections
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
color_channel = connection.channel()
color_channel.queue_delete(queue='matrix-color')
color_channel.queue_declare(queue='matrix-color')

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
sensor_channel = connection.channel()
sensor_channel.queue_delete(queue='matrix-sensor')
sensor_channel.queue_declare(queue='matrix-sensor')

## Setting up Firebase
config = {
    "apiKey": "AIzaSyAsv3-mp3gzOYIw8K2rcGObm0BX83smlYc",
    "authDomain": "stockgame-c5e3f.firebaseapp.com",
    "databaseURL": "https://stockgame-c5e3f.firebaseio.com",
    "storageBucket": "stockgame-c5e3f.appspot.com",
    "messagingSenderId": "63230265155"
}

firebase = pyrebase.initialize_app(config)
fb_db = firebase.database()

stretch = 2000

def run():
    current_mode = 'time'
    current_time = datetime.datetime.now().time()
    latest_sensors = None
    fb_update_cycles = 0
    colors = None
    while True:
        current_time = (datetime.datetime.combine(datetime.date.today(), current_time) + datetime.timedelta(milliseconds=50*stretch)).time()
        time.sleep(update_interval / 1000)

        # Update sensor data and color matrix
        sensors = update_sensors()
        if sensors is not None:
            latest_sensors = sensors
        if latest_sensors is not None:
            colors = modes.mode[current_mode](latest_sensors, current_time)
            push_colors(colors)

        # Update Firebase
        fb_update_cycles += 1
        if fb_update_cycles >= 500 / update_interval:
            fb_update_cycles = 0

            # Push color and sensor data
            if colors is not None:
                data = {
                    "color": json.dumps(colors),
                    "sensors": json.dumps(latest_sensors)
                }
                fb_db.child("Group").child("group1").child("matrix").update(data)

            # Push time and current mode
            fb_db.child("Group").child("group1").update({'state' : current_mode})
            fb_db.child("Group").child("group1").update({'time' : int(current_time.hour) * 100 + current_time.second})
            print(int(current_time.hour) * 100 + current_time.second)

            # Get transition data
            bedtime = fb_db.child("Group").child("group1").child("bedtime").get().val()
            bedtime = datetime.time(int(bedtime / 100), bedtime % 100)
            waketime = fb_db.child("Group").child("group1").child("waketime").get().val()
            waketime = datetime.time(int(waketime / 100), waketime % 100)
            alarms = fb_db.child("Group").child("group1").child("alarms").get().val()
            for alarm in alarms:
                alarmtime = datetime.time(int(alarm['setoffTime'] / 100), alarm['setoffTime'] % 100)
                #alarmstop = alarmtime + datetime.timedelta(0, 0, alarm['duration'])
                alarmstop = (datetime.datetime.combine(datetime.date.today(), alarmtime) + datetime.timedelta(seconds=alarm['duration'])).time()
                transitions['alarm'] += [('time', alarmtime, alarmstop)]
            transitions['follow'] += [('time', bedtime, waketime)]
            transitions['time'] += [('time', waketime, bedtime)]

        # Transition if needed
        transition_done = False
        if 'alarm' in transitions:
            for condition in transitions['alarm']:
                if condition[0] == 'time' and time_in_range(condition[1], condition[2], current_time):
                    current_mode = 'alarm'
                    transition_done = True
        if 'follow' in transitions:
            for condition in transitions['follow']:
                if condition[0] == 'time' and time_in_range(condition[1], condition[2], current_time):
                    current_mode = 'follow'
                    transition_done = True
        if not transition_done:
            current_mode = 'time'


run()

connection.close()