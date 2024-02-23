import time
import requests
import json
import os

def harvestData(duration: float, fileName: str, directory: str):
    """
    Pobieraj dane przez 'duration' godzin do ścieżki 'directory' do plików o nazwach 'fileName'.
    """
    endpoint = 'https://api.um.warszawa.pl/api/action/busestrams_get/'
    callParameters = {
        'resource_id': 'f2e5503e-927d-4ad3-9500-4ab9e55deb59',
        'apikey': 'db787e64-34d2-4757-a506-a9e63d44a8a8',
        'type': '1'
    } 
    collectedData = {}
    
    stopTime = time.time() + (duration * 3600)
    recordID = 0
    while(stopTime - time.time() > 0):
        response = requests.get(endpoint, params = callParameters)
        if response.status_code == 200:
            response = response.json()["result"]
            collectedData[recordID] = response
            recordID += 1
            time.sleep(10)
    
    fullDirectory = os.path.join(directory, fileName + '.json')
    with open(fullDirectory, "w") as file:
        json.dump(collectedData, file)

def harvestFullDayData(folderName: str):
    """
    Pobieraj dane przez jedną dobę do folderu o nazwie 'folderName'.
    """
    directory = os.path.join(os.getcwd(), folderName)
    if not os.path.isdir(directory):
        os.mkdir(directory)
    
    for hour in range(1, 25):
        harvestData(1, f'hour{hour}', directory)
    

