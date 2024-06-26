import os
import json
import pandas
import numpy
import matplotlib.pyplot
import plotly.graph_objects

def cleanData(directory: str):
    """
    Stwórz kopię danych spod ścieżki 'directory' bez błędnych rekordów..
    """
    folderName = os.path.basename(directory).capitalize()
    cleanDirectory = os.path.join(directory, f'clean{folderName}')
    if not os.path.isdir(cleanDirectory):
        os.mkdir(cleanDirectory)

    hour = 1
    while(True):
        try:
            fileDirectory = os.path.join(directory, f'hour{hour}.json')
            with open(fileDirectory, 'r') as file:
                hourData = json.load(file)
        except:
            break
        
        index = 0
        cleanHourData = {}
        for record in hourData:
            if hourData[record] != 'Błędna metoda lub parametry wywołania':
                cleanHourData[str(index)] = hourData[record]
                index += 1
        
        cleanFileDirectory = os.path.join(cleanDirectory, f'hour{hour}.json')
        with open(cleanFileDirectory, "w") as cleanFile:
            json.dump(cleanHourData, cleanFile)

        hour += 1

def dataSize(directory: str):
    """
    Oblicz liczbę rekordów w folderze danych pod ścieżką 'directory'.
    """
    records = 0
    hour = 1
    while(True):
        if hour == 8:
            break
        try:
            fileDirectory = os.path.join(directory, f'hour{hour}.json')
            with open(fileDirectory, 'r') as file:
                hourData = json.load(file)
        except:
            break

        records += len(hourData)
        hour += 1

    return records

def dataToDict(directory: str):
    """
    Odczytaj dane ze ścieżki 'directory' i zwróć je w formie słownika.
    """
    dataDict = {}

    hour = 1
    while(True):
        fileDirectory = os.path.join(directory, f'hour{hour}.json')
        try:
            with open(fileDirectory, 'r') as file:
                hourData = dict(json.load(file))
        except:
            break

        dataDict[f'h{hour}'] = []
        for record in hourData:
            dataDict[f'h{hour}'].append(hourData[record])
        
        hour += 1
    
    return dataDict

def dictToDataFrame(data: dict):
    """
    Przekształć słownik danych w DataFrame.
    """
    lines = []
    longitudes = []
    vehicleNumbers = []
    times = []
    latitudes = []
    
    for hour in data:
        for record in data[hour]:
            for bus in record:
                lines.append(bus['Lines'])
                longitudes.append(float(bus['Lon']))
                vehicleNumbers.append(bus['VehicleNumber'])
                times.append(bus['Time'])
                latitudes.append(float(bus['Lat']))
    
    dataDict = {'id': vehicleNumbers,
                'line': lines,
                'lon': longitudes,
                'lat': latitudes,
                'time': times}

    dataFrame = pandas.DataFrame(dataDict)
    return dataFrame 

def distance(latitude1: list, longitude1: list, latitude2: list, longitude2: list):
    """
    Zwróć dystans w metrach między dwoma punktami (operacja na kolumnach tabeli).
    """
    lat1, lon1 = numpy.radians(latitude1), numpy.radians(longitude1)
    lat2, lon2 = numpy.radians(latitude2), numpy.radians(longitude2)
    earthRadius = 6371000
    # Korzysta ze wzoru na odległość haversine
    latDiff = lat2 - lat1
    lonDiff = lon2 - lon1
    distance = 2.0 * earthRadius                                  \
        * numpy.arcsin(numpy.sqrt(numpy.sin(latDiff/2)**2         \
                            + numpy.cos(lat1) * numpy.cos(lat2)   \
                                * numpy.sin(lonDiff/2)**2))
    return distance

def addSpeed(data: pandas.DataFrame):
    """
    Dodaj do DataFrame z danymi kolumnę prędkość.
    """
    data['time'] = pandas.to_datetime(data['time'], errors='coerce')
    data.sort_values(by=['id', 'time'], inplace=True)
    data['timeDiff'] = data.groupby('id')['time'].diff().dt.total_seconds()
    data['distance'] = distance(data['lat'].shift(), data['lon'].shift(), data['lat'], data['lon'])
    data['speed'] = (data['distance'] / data['timeDiff']) * 3.6
    return data

def discardOver100kmph(data: pandas.DataFrame):
    """
    Odrzuć rekordy z prędkością powyżej 100 km/h.
    """
    afterDiscard = data[data['speed'] <= 100]
    return afterDiscard

def speedingBusesCount(data: pandas.DataFrame):
    """
    Policz autobusy, które przekroczyły 50 km/h.
    """
    over50 = data[data['speed'] > 50]
    busesCount = over50['id'].nunique()
    return busesCount

def mostSpeedingLines(data: pandas.DataFrame, top: int):
    """
    Wskaż 'top' linii autobusowych, których największa liczna autobusów przekroczyła 50km/h.
    """
    data = discardOver100kmph(data)
    data = data[data['speed'] > 50]
    data = data.groupby('line')['id'].nunique()
    data = data.sort_values(ascending=False).head(top)
    return data

def averageSpeed(data: pandas.DataFrame):
    """
    Oblicz średnią prędkość autobusów.
    """
    return (sum(data['distance']) / sum(data['timeDiff'])) * 3.6

def speedDistributionGraph(data: pandas.DataFrame):
    """
    Narysuj wykres rozkładu prędkości.
    """
    totalRecords = len(data.index)
    speedRanges = ['v <= 5'] + [f'{x} < v <= {x + 5}' for x in range(5, 95, 5)] + ['95 < v']
    parts = []
    
    selectedData = data[data['speed'] <= 5]
    selectedRecords = len(selectedData.index)
    ratio = selectedRecords / totalRecords
    parts.append(round(ratio, 4))
    for lowerBound in range(5, 100, 5):
        upperBound = lowerBound + 5
        selectedData = data[data['speed'] > lowerBound]
        selectedData = selectedData[selectedData['speed'] <= upperBound]
        selectedRecords = len(selectedData.index)
        ratio = selectedRecords / totalRecords
        parts.append(round(ratio, 4))
    
    labels = [f'{speedRanges[i]} ({parts[i]})' for i in range(len(speedRanges))]
    fig, ax = matplotlib.pyplot.subplots()
    ax.pie(parts)
    matplotlib.pyplot.legend(labels, title='Przedziały prędkości', loc='best', fontsize = 14)
    matplotlib.pyplot.axis('equal')
    matplotlib.pyplot.title('Rozkład prędkości autobusów [km/h]', fontsize = 16)
    return fig

def over50Map(data: pandas.DataFrame):
    """
    Zaznacz na mapie Warszawy punkty, gdzie zostało przekroczone 50 km/h.
    """
    over50 = data[data['speed'] > 50]

    fig = plotly.graph_objects.Figure(plotly.graph_objects.Densitymapbox(
    lat = over50['lat'],
    lon = over50['lon'],
    z = over50['speed'],
    radius = 10, 
    colorscale = 'geyser',
    colorbar = dict(title='Speed [km/h]')
    ))
    
    fig.update_layout(
        mapbox_style = 'carto-positron',
        mapbox_center = {'lat': 52.2297, 'lon': 21.0122},
        mapbox_zoom = 10
    )

    return fig
