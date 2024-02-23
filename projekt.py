import os
import pandas
import numpy
import matplotlib.pyplot
import plotly.graph_objects
from buses import analysis

# Usunięcie pustych rekordów
directory = os.getcwd() + '\data\cleanData'

# Wczytanie dancyh z pliku
fullData = analysis.dataToDict(directory)
fullData = analysis.dictToDataFrame(fullData)

# Obliczenie prędkości
fullData = analysis.addSpeed(fullData)

# Odrzucenie skrajnych wyników
fullData = analysis.discardOver100kmph(fullData)

# Wyróżnienie przedziałów czasowych
fullData.set_index('time', inplace = True)

peakMorningData = fullData.between_time('5:00', '9:00')
peakEveningData = fullData.between_time('15:00', '19:00')
peakData = pandas.concat([peakMorningData, peakEveningData])
peakData.reset_index(inplace = True)

nightData = fullData.between_time('0:00', '5:00')
nightData.reset_index(inplace = True)

middleData = fullData.between_time('9:00:00', '15:00')
middleData.reset_index(inplace = True)

fullData.reset_index(inplace = True)

# Ile autobusów przekroczyło 50 km/h?
peakCount = analysis.speedingBusesCount(peakData)
middleCount = analysis.speedingBusesCount(middleData)
nightCount = analysis.speedingBusesCount(nightData)
print(f'peak: {peakCount}, middle: {middleCount}, night: {nightCount}')

# Linie z największą ilością autobusów przekraczających prędkość
peakLines = analysis.mostSpeedingLines(peakData, 3)
middleLines = analysis.mostSpeedingLines(middleData, 3)
nightLines = analysis.mostSpeedingLines(nightData, 3)
print('peak:')
print(peakLines)
print('middle:')
print(middleLines)
print('night:')
print(nightLines)

# Średnia prędkość autobusów
peakDataOver5 = peakData[peakData['speed'] > 5]
middleDataOver5 = middleData[middleData['speed'] > 5]
nightDataOver5 = nightData[nightData['speed'] > 5]

peakAverage = analysis.averageSpeed(peakDataOver5)
middleAverage = analysis.averageSpeed(middleDataOver5)
nightAverage = analysis.averageSpeed(nightDataOver5)
print(f'peak: {peakAverage}, middle: {middleAverage}, night: {nightAverage}')

# Rozkłady prędkości
peakGraph = analysis.speedDistributionGraph(peakDataOver5)
matplotlib.pyplot.show()
middleGraph = analysis.speedDistributionGraph(peakDataOver5)
matplotlib.pyplot.show()
nightGraph = analysis.speedDistributionGraph(peakDataOver5)
matplotlib.pyplot.show()

# Mapy
peakMap = analysis.over50Map(peakData)
middleMap = analysis.over50Map(middleData)
nightMap = analysis.over50Map(nightData)
peakMap.show()
middleMap.show()
nightMap.show()

fullMap = analysis.over50Map(fullData)
#fullMap.show()