import requests

class WeatherPlugin(object):
    title = 'Weather Plugin'

    def get_weather(user, message):
        # Get the current weather for Seaside, Oregon.
        weather_url = "http://api.openweathermap.org/data/2.5/weather?lat=44.9429&lon=-123.0351&units=imperial"
        r = requests.get(weather_url)
        if r.json():
            weather = r.json()['weather'][0]
            main = r.json()['main']

            temp = str(main['temp'])[0:2]
            description = str(weather['description'])
            print "> Wow %s. %s degrees. FrankerZ" % (description, temp)

    commands = {
        "weather": get_weather,
        "w": get_weather
        }



def setup():
    return WeatherPlugin()