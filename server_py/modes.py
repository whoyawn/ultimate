from PIL import Image

gradient_file = 'res/gradient.png'

gradient = Image.open(gradient_file).load()

def color_at_time(time):
    pixel = (time.hour + time.minute / 60.0) * 10.0
    color = gradient[0, int(pixel)]
    return color


def mode_time(sensors, time):
    color = color_at_time(time)
    return [[color for x in range(len(sensors[0]))] for y in range(len(sensors))]


def mode_follow(sensors, time):
    intensity = 0.5
    return [[(255, 255, 255, sensors[y][x] * intensity) for x in range(len(sensors[0]))] for y in range(len(sensors))]


def mode_alarm(sensors, time):
    blink_a = [[(255, 0, 0, 255) for x in range(len(sensors[0]))] for y in range(len(sensors))]
    blink_b = [[(0, 0, 255, 255) for x in range(len(sensors[0]))] for y in range(len(sensors))]

    if time.microsecond / 1000 >= 500:
        return blink_a
    else:
        return blink_b

mode = {
    'time': mode_time,
    'follow': mode_follow,
    'alarm': mode_alarm
}