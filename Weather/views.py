import urllib.request
import json
from datetime import datetime
import datetime as DT
import numpy as np
import pandas as pd
from django.shortcuts import render
from .utils import get_simple_plot, get_regression_plot
from datetime import time


def index(request):
    return render(request, "main/index.html")


def currentWeather(request):
    if request.method == 'POST':
        city = request.POST['city']
        source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?q=' +
                                        city + '&units=metric&appid=55980624037377da2434c1be6c3f3d39').read()
        list_of_data = json.loads(source)
        data = {
            "country_code": str(list_of_data['sys']['country']),
            "coordinate": str(list_of_data['coord']['lon']) + ', '
                          + str(list_of_data['coord']['lat']),
            "temp": str(list_of_data['main']['temp']) + ' °C',
            "pressure": str(list_of_data['main']['pressure']),
            "humidity": str(list_of_data['main']['humidity']),
            'main': str(list_of_data['weather'][0]['main']),
            'description': str(list_of_data['weather'][0]['description']),
            'icon': list_of_data['weather'][0]['icon'],
            "sunrise": datetime.fromtimestamp(list_of_data['sys']['sunrise']).strftime('%H:%M'),
            "sunset": datetime.fromtimestamp(list_of_data['sys']['sunset']).strftime('%H:%M'),
            "wind": str(list_of_data['wind']['speed']),
            "name": str(list_of_data['name']),
        }
    else:
        data = {}

    return render(request, "main/currentWeather.html", data)


def pollution(request):
    if request.method == 'POST':
        city = request.POST['city']
        geoData = urllib.request.urlopen('http://api.openweathermap.org/geo/1.0/direct?q=' +
                                         city + '&limit=1&appid=55980624037377da2434c1be6c3f3d39').read()
        location_data = json.loads(geoData)
        lat, lon = str(location_data[0]['lat']), str(location_data[0]['lon'])
        source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/air_pollution?lat=' +
                                        lat + '&lon=' + lon + '&appid=55980624037377da2434c1be6c3f3d39').read()
        list_of_data = json.loads(source)

        data = {
            "cityName": str(city),
            "aqi": str(list_of_data['list'][0]['main']['aqi']),
            "co": str(list_of_data['list'][0]['components']['co']),
            "no": str(list_of_data['list'][0]['components']['no']),
            "no2": str(list_of_data['list'][0]['components']['no2']),
            "o3": str(list_of_data['list'][0]['components']['o3']),
            "so2": str(list_of_data['list'][0]['components']['so2']),
            "pm2_5": str(list_of_data['list'][0]['components']['pm2_5']),
            "pm10": str(list_of_data['list'][0]['components']['pm10']),
            "nh3": str(list_of_data['list'][0]['components']['nh3']),
        }
    else:
        data = {}

    return render(request, "main/pollution.html", data)


def forecast(request):
    error_message = None
    list_of_graphs = None
    if request.method == 'POST':
        city = request.POST['city']
        geoData = urllib.request.urlopen('http://api.openweathermap.org/geo/1.0/direct?q=' +
                                         city + '&limit=1&appid=55980624037377da2434c1be6c3f3d39').read()
        location_data = json.loads(geoData)
        lat, lon = str(location_data[0]['lat']), str(location_data[0]['lon'])
        pollution_source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat=' +
                                                  lat + '&lon=' + lon + '&units=metric&appid=55980624037377da2434c1be6c3f3d39').read()
        pollution_data = json.loads(pollution_source)
        weather_source = urllib.request.urlopen('https://api.openweathermap.org/data/2.5/onecall?lat=' +
                                                lat + '&lon=' + lon + '&exclude=minutely,hourly&units=metric&'
                                                                      'appid=55980624037377da2434c1be6c3f3d39').read()
        weather_data = json.loads(weather_source)
        compounds = ["AQI", "NO", 'NO2', 'O3', 'SO2', 'PM2_5', 'PM10', 'NH3', 'CO']
        data = {'Compounds': compounds}
        dataW = {'Components': ['Temperature(°C)', 'Humidity(%)', 'Wind speed(m/s)', 'Clouds(%)']}
        date, stampD = [], []
        AQI, NO, NO2, O3, SO2, PM2_5, PM10, NH3, CO = [], [], [], [], [], [], [], [], []

        for timestamp in pollution_data['list']:
            date_time = datetime.fromtimestamp(timestamp['dt'])
            d = date_time.strftime("%d/%m/%Y %H:%M:%S")
            data[d] = [timestamp['main']['aqi'], timestamp['components']['no'],
                       timestamp['components']['no2'], timestamp['components']['o3'], timestamp['components']['so2'],
                       timestamp['components']['pm2_5'], timestamp['components']['pm10'],
                       timestamp['components']['nh3'], timestamp['components']['co']]
            date.append(timestamp['dt'])
            stampD.append(timestamp['dt'])
            AQI.append(timestamp['main']['aqi'])
            NO.append(timestamp['components']['no'])
            NO2.append(timestamp['components']['no2'])
            O3.append(timestamp['components']['o3'])
            SO2.append(timestamp['components']['so2'])
            PM2_5.append(timestamp['components']['pm2_5'])
            PM10.append(timestamp['components']['pm10'])
            NH3.append(timestamp['components']['nh3'])
            CO.append(timestamp['components']['co'])

        compDict = {'AQI': AQI, "NO": NO, 'NO2': NO2, 'O3': O3, 'SO2': SO2, 'PM2_5': PM2_5, 'PM10': PM10,
                    'NH3': NH3, 'CO': CO}

        for day in weather_data['daily']:
            date_time = datetime.fromtimestamp(day['dt'])
            d = date_time.strftime("%m-%d-%Y")
            dataW[d] = [day['temp']['day'], day['humidity'], day['wind_speed'], day['clouds']]

        currentYear = str(datetime.now().year)

        df = pd.DataFrame(data)
        date_columns = [c for c in df.columns.tolist() if c.endswith(currentYear)]
        df2 = df.melt(id_vars='Compounds', value_vars=date_columns, var_name='Date', value_name='Concentration')
        df2['Date'] = pd.to_datetime(df2['Date'])

        dfW = pd.DataFrame(dataW)
        date_columnsW = [c for c in dfW.columns.tolist() if c.endswith(currentYear)]
        df2W = dfW.melt(id_vars='Components', value_vars=date_columnsW, var_name='Date', value_name='Volume')
        df2W['Date'] = pd.to_datetime(df2W['Date'])

        title = 'Air Pollution - ' + city
        titleW = 'Weather Conditions - ' + city
        graphType = request.POST['graphType']

        if graphType == "scatter plot":
            data_time = np.asarray(date)
            list_of_graphs = []
            for compound in compDict:
                title = 'Air Pollution - ' + city + ' - ' + compound
                count = np.asarray(compDict[compound])
                dfr = pd.DataFrame({'Date': data_time, 'Concentration': count})
                dfr.Date = pd.to_datetime(dfr.Date)
                #dfr['date_ordinal'] = pd.to_datetime(dfr['Date']).apply(lambda dateC: dateC.toordinal())
                #dfr['stamp'] = stampD
                graph = get_regression_plot(title, data=dfr, weather=False, x=stampD, y=compDict[compound])
                list_of_graphs.append(graph)

        elif graphType != "":
            graph = get_simple_plot(graphType, title, data=df2, weather=False)
            graphW = get_simple_plot(graphType, titleW, data=df2W, weather=True)

            list_of_graphs = [graph, graphW]
        else:
            error_message = 'Please select a graph type to continue'

    context = {
        'list_of_graphs': list_of_graphs,
        'error_message': error_message,
    }

    return render(request, "main/forecast.html", context)


def geoCity(request):
    if request.method == 'POST':
        city = request.POST['city']
        geoData = urllib.request.urlopen('http://api.openweathermap.org/geo/1.0/direct?q=' +
                                         city + '&limit=3&appid=55980624037377da2434c1be6c3f3d39').read()
        location_data = json.loads(geoData)
        list_of_cities = []

        for location in location_data:
            loc_list = location['local_names']
            del loc_list['feature_name']
            loc_list = list(loc_list.items())
            list_of_cities.append({'name': location['name'], 'local_names': loc_list,
                                   'lat': location['lat'], 'lon': location['lon'], 'country': location['country']})
    else:
        list_of_cities = {}

    context = {
        'list_of_cities': list_of_cities,
    }

    return render(request, "main/geoCity.html", context)
