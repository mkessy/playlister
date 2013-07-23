#script download all station id's

import songza
import time
import logging
import os
import simplejson as json

GENRE_FILE = 'backend/genres.json'
save_path = 'station_files'

date_string = time.strftime("%Y-%m-%d-%H:%M")
logging.basicConfig(filename=date_string+'.genre', level=logging.DEBUG)

with open(GENRE_FILE) as f:
    genres = json.load(f)

all_ids = {k:v['station_ids'] for k,v in genres.items()}

for genre in all_ids:

    if not os.path.exists(os.path.join(save_path, k+'_station.json')):
        logging.INFO('STARTING GENRE: ' + k)
        songza.get_stations(genre, genre['station_ids'], save_path)



