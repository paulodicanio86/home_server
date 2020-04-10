import json

schedule = {}

schedule['lamp'] = {'name': 'Lamp', 'pin': 7,
                    'mode': 'on_off', 'on': ['10:00', '11:00'], 'off': ['10:01', '11:01']}
schedule['water'] = {'name': 'Waterpump', 'pin': 7,
                     'mode': 'duration', 'on': ['12:00'], 'duration': 7, 'last_on': '?'}

with open('schedule.json', 'w') as f:
    json.dump(schedule, f, indent=4)
