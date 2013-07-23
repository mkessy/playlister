import time
import requests
import simplejson as json
import logging
import os
import tempfile

import sys

from math import log, ceil
from Queue import PriorityQueue
from collections import defaultdict

#script to download playlists from songza

#Constants
BASE_URL = 'http://songza.com'
BASE_API = 'http://songza.com/api/1' #not a requestable url
BASE_STATION = 'http://songza.com/api/1/station/%s' #where %s is stationid

BASE_SONG = 'http://songza.com/api/1/station/%s/next' #where %s is stationid

BASE_BROWSE = 'http://songza.com/api/1/tags'
BASE_SUB_BROWSE = 'http://songza.com/api/1/gallery/tags/%s'

SUB_BROWSE_CATS = {
                   'genres':'genres',
                   'activities':'activities',
                   'moods':'moods',
                   'decades':'decades',
                   'culture':'culture',
                   'record_store_clerk':'record_store_clerk'
                   }

HEADER = {'User-Agent':
          "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)"}

REQUEST_KWARGS = {'headers':HEADER, 'timeout':10.0, 'allow_redirects':False}

HTTPError = requests.exceptions.HTTPError
logging.basicConfig(filename='test_log2.log', level=logging.DEBUG)


#BEGIN UTILITY FUNCTIONS

def expected_tries(N):
    """Calculate the expected number of tries to get
    0.999% coverage of the given playlist"""

    return int(ceil( log(0.001)/log( (float(N)-1)/N ) ))

def get_station_info(stationid):
    """Returns a dictionary with relevant station info"""

    station_url = BASE_STATION % (stationid,)
    res = requests.get(station_url, **REQUEST_KWARGS)

    if res.status_code != 200:
        raise HTTPError('Status: %s\nUrl: %s' % (res.status_code, res.url))

    station_info = res.json()
    return station_info

#END UTILITY FUNCTIONS

def get_songs(stationid, song_count, song_names):
    """Attempts to track all songs from the given stationid"""

    next_song_url = BASE_SONG % (stationid,)

    songs = []
    max_tries = 10
    #max_tries = expected_tries(song_count)
    SLEEP_TIME = .25

    tries = 0
    #song_session = requests.Session()

    logging.debug('==================================================')
    logging.debug('Starting request loop for station: %s' % stationid)
    try:


        while len(song_names) < song_count and tries < max_tries:
            print 'Attempt: %s of %s\n' % (tries, max_tries)

            print '\nRequesting new song...',
            try:
                #song_response = song_session.get(next_song_url, **REQUEST_KWARGS)

                song_response = requests.get(next_song_url, **REQUEST_KWARGS)
                #for rate limiting
                #if song_response.status_code == 420 or 429:
                #    print 'Rate limit.. Destroying cookie'
                #    song_session.close() #close session to delete cookie
                #    song_session = requests.Session()
                #    song_response = song_session.get(next_song_url, **REQUEST_KWARGS)

                if song_response.status_code == 200:
                    song_json = song_response.json()
                    song_name = song_json['song']['title']
                    if song_name in song_names:
                        print 'Song already in list!\n'
                    else:
                        print 'Added \"%s\" to the list!\n' % (song_name,)
                        songs.append(song_json)
                        song_names.append(song_name)

                else:
                    print 'Not OK server response'
                    print 'Status: %s' % (song_reponse.status_code)
                    print 'Will retry..\n\n'
                    tries -= 1

                time.sleep(SLEEP_TIME)
                tries += 1
            except requests.Timeout as e:
                print 'Request timed out'
                print 'Retrying request...'
                print repr(e)
                continue

        print '\n=======================\n'
        print 'Finished with main loop...\n'
        print 'Returning list with %s songs of a possible %s\n' % (len(song_names), song_count)

    except Exception as e:
        print 'Ended loop prematurely because of error.\n'
        print 'Returning incomplete playlist'
        logging.debug('**************ERROR***************')
        logging.debug(repr(e))
        print e.value
        raise
    finally:
        complete = len(songs)==song_count
        return ( {'complete':complete, 'remaining':song_count-len(songs),
            'song_names':song_names, 'song_count':song_count, 'stationid':stationid, 'songs':songs}  )

def get_stations(stationids):
    """Gets the playlists specified in the stationids list, and saves them to file"""

    print 'Initializing queue with %s stations' % len(stationids)
    station_queue = PriorityQueue()

    song_list_counter = defaultdict(list) #keeps track of the songs currently in each song list
    station_info = defaultdict(int)
    song_list_store = {} #intermediate store of song lists while queue is still running

    temp_file_dict = {}


    for stationid in stationids:
        try:
            station_info[stationid] = get_station_info(stationid)['song_count']
        except HTTPError as e:
            print 'Error could not add station %s' % (stationid,)
            continue
    #initialize the queue and temp files
    for stationid, song_count in station_info.items():
        station_queue.put( (song_count, stationid) )
        tf = tempfile.NamedTemporaryFile(prefix=stationid, delete=False)
        temp_file_dict[stationid] = tf.name


    while not station_queue.empty():

        print '-----'
        remaining, stationid = station_queue.get()
        print '\nAttempting to get songs from station: %s\n' % (stationid,)
        current_station_status = get_songs(stationid,
                station_info[stationid],
                song_list_counter[stationid])
                #update tempfile

        with open(temp_file_dict[stationid], 'w+') as tf:
            tf.write(json.dumps(current_station_status))

    playlists = {}
    for stationid, temp in temp_file_dict.items():
        with open(temp) as tf:
            playlists[stationid] = json.loads(tf.read())

    #merge all playlists (stored in temp files) into a single file
    with open(stationid+'_station.json', 'w+') as f:
        json.dump(playlists, f)


    print '==============================='
    print 'Completed downloading %s stations' % len(playlists)
    for stationid, playlist in playlists.items():
        print '-----Station %s' % stationid
        print '\tCompletion: %s' % playlist['complete']
        print '\tSong Count: %s' % ( playlist['song_count']- playlist['remaining'], )
        print '\tEstimated Remaining: %s' % playlist['remaining']
        print '\tSong Count: %s' % playlist['song_count']
    #add return value summarizing the processed

def tests():
    """Not yet implemented"""

    test_stations = ['1724409', '1392809', '1391300', '1387704', '1501119']
    get_playlists(test_stations)

def main():

    GENRE_FILE = 'backend/genres.json'

    genre_id = sys.argv[1]

#    with open('backend/songza_browse_genres.json') as f:
#        genres = json.load(f)
#
#    genre_dict = {genre['id']:genre for genre in genres}
#
#    with open('backend/genres.json', 'w+') as f:
#        json.dump(genre_dict, f)
#


    if genre_id:

        if os.path.isfile(GENRE_FILE):
            try:
                genres = json.load(GENRE_FILE)
            except IOError as e:
                print(repr(e))
                print 'Could not open %s. Need a genres JSON \
                file to load genre station ids' % GENRE_FILE
                sys.exit(1)

            stationids = genres[genre_id]['station_ids']

        else:
            print 'Could not find %s' % GENRE_FILE

    else:
        print 'No args... exiting'
        sys.exit(1)

    print 'Attempting to download station: %s' % genre_id
    print '----------------------------------------------'
    station = get_stations(stationids)
    print '==========================================\n\nFinished'





if __name__ == '__main__':
    main()
    #tests()
