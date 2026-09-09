"""Local flight data for the T10 assessment.

The tool layer is deliberately local so the project can be demonstrated without
a paid flight API. The agent/tool architecture can later be connected to an API.
"""

FLIGHTS = [
    {"id":"AI101","airline":"Air India","from_city":"Delhi","to_city":"Mumbai","departure":"06:30","arrival":"08:45","price":5200,"stops":0},
    {"id":"6E204","airline":"IndiGo","from_city":"Delhi","to_city":"Mumbai","departure":"08:10","arrival":"10:20","price":4850,"stops":0},
    {"id":"UK955","airline":"Vistara","from_city":"Delhi","to_city":"Mumbai","departure":"10:40","arrival":"12:55","price":6100,"stops":0},
    {"id":"6E718","airline":"IndiGo","from_city":"Delhi","to_city":"Mumbai","departure":"14:15","arrival":"16:25","price":4550,"stops":0},
    {"id":"AI865","airline":"Air India","from_city":"Delhi","to_city":"Mumbai","departure":"19:30","arrival":"21:45","price":4300,"stops":0},

    {"id":"6E301","airline":"IndiGo","from_city":"Delhi","to_city":"Bengaluru","departure":"07:20","arrival":"10:05","price":5600,"stops":0},
    {"id":"AI505","airline":"Air India","from_city":"Delhi","to_city":"Bengaluru","departure":"11:10","arrival":"14:00","price":6900,"stops":0},
    {"id":"6E902","airline":"IndiGo","from_city":"Delhi","to_city":"Bengaluru","departure":"18:40","arrival":"21:30","price":5100,"stops":0},

    {"id":"AI401","airline":"Air India","from_city":"Mumbai","to_city":"Delhi","departure":"06:00","arrival":"08:10","price":5400,"stops":0},
    {"id":"6E110","airline":"IndiGo","from_city":"Mumbai","to_city":"Delhi","departure":"20:10","arrival":"22:20","price":4700,"stops":0},
]
