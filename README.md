# CityDayPlanner

The key idea of the project is optmizing day-to-day people's routes in a city.

There are [slides in Russian](https://github.com/Omrigan/CityDayPlanner/blob/master/docs/CityDayPlanner.pdf)

## Usage scenario
When someone wants to use the app, he creates a schedule for the day in Google Calendar. The schedule may contain placeholders, specifying only category of the place desired to visit. 

CityDayPlanner will extract the data from GCal and build the optmized version of the schedule, substituting most suitable places for given placeholders. The goal is to reduce total travelling time.

## Underlying technologies
The whole system is written in python. 

We use OSRM for building routes between specific places. 

There are three sources for places:
 - OpenStreetMap
 - Google Maps
 - Moscow Open Data

The optimization is performed through dynamic programming.
