# CityDayPlanner

Сервер запущен на: [http://23.105.248.30/](http://23.105.248.30/)

Презентация: [CityDayPlanner.pdf](https://omrigan.github.io/CityDayPlanner/CItyDayPlanner.pdf)



## Пример API
Request:
```
{
            "ordered_events": [
                {"type": "fixed_place",
                 "location": {
                   "lat": 55.7494539, 
                   "lng": 37.62160470000001
                 },
                 "finish_time": "15:00"},
                {"type": "cafe",
                 "brand": "даблби",
                 "delay": 15},
                {"type": "park",
                 "delay": 0},
                {"type": "restaurant",
                 "delay": 20},
                {"type": "fixed_place",
                 "start_time": "23:00",
                 "location": {"lat": 55.7494539, "lng": 37.62160470000001 },
                 "delay": 20}
            ],
            "unordered_events": []
}
```

Response: 
```json
{
    "resulting_dist": 1517.3725174143433,
    "route": [
        {
            "amenity": "cafe",
            "brand": "даблби",
            "contact:email": "info@double-b.ru",
            "contact:facebook": "https://www.facebook.com/DoubleBCoffeeTea",
            "contact:instagram": "https://www.instagram.com/doublebcoffeetea",
            "contact:telegram": "https://telegram.me/doublebdaily",
            "contact:website": "http://double-b.ru",
            "cuisine": "coffee_shop",
            "delay": 15.0,
            "diet:vegetarian": "no",
            "drink:coffee": "yes",
            "finish_time": "15:55",
            "location": {
                "lat": "55.747484",
                "lng": "37.6259389"
            },
            "name": "Даблби",
            "name:en": "Double B",
            "name:ru": "Даблби",
            "original_brand": "Даблби",
            "start_time": "15:40",
            "takeaway": "yes",
            "type": "cafe"
        },
        {
            "brand": "парк \"зарядье\"",
            "delay": 60.0,
            "finish_time": "17:35",
            "location": {
                "lat": 55.7515994,
                "lng": 37.6288575
            },
            "name": "Парк \"Зарядье\"",
            "start_time": "16:35",
            "type": "park"
        },
        {
            "brand": "порто мальтезе",
            "delay": 20.0,
            "finish_time": "18:35",
            "location": {
                "lat": 55.7527595,
                "lng": 37.6268736
            },
            "name": "Порто Мальтезе",
            "start_time": "18:15",
            "type": "restaurant"
        },
        {
            "delay": 225.0,
            "finish_time": "23:00",
            "start_time": "19:15",
            "type": "free_time"
        },
        {
            "delay": 0.0,
            "finish_time": "23:00",
            "location": {
                "lat": 55.7494539,
                "lng": 37.62160470000001
            },
            "start_time": "23:00",
            "type": "fixed_place"
        }
    ]
}
```