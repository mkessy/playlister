import time
import requests
import simplejson as json
import pprint
import pickle
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

TEST_STATIONIDS = ['1724409', '1392809'] #some stationids used for testing methods

HEADER = {'User-Agent':
          "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)"}

REQUEST_KWARGS = {'headers':HEADER, 'timeout':5.0, 'allow_redirects':False}

HTTPError = requests.exceptions.HTTPError
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
    if :
        song_names = []
    #max_tries = 10
    max_tries = expected_tries(song_count)
    SLEEP_TIME = 5

    tries = 0
    try:
        while len(song_names) < song_count and tries < max_tries:
            print 'Attempt: %s of %s\n' % (tries, max_tries)

            print '\nRequesting new song...'
            song_res = requests.get(next_song_url, **REQUEST_KWARGS)
            if song_res.status_code == 200:
                song_json = song_res.json()
                song_name = song_json['song']['title']
                if song_name in song_names:
                    print 'Song already in list!\n\n'
                else:
                    print 'Added \"%s\" to the list!\n\n' % (song_name,)
                    songs.append(song_json)
                    song_names.append(song_name)

            else:
                print 'Not OK server response\n'
                print 'Status: %s\n' % (song_res.status_code)
                print 'Will retry..\n\n'
                tries -= 1

            time.sleep(1)
            tries += 1
        print '\n=======================\n'
        print 'Finished with main loop...\n'
        print 'Returning list with %s songs of a possible %s\n' % (len(song_names), song_count)

    except Exception as e:
        print 'Ended loop prematurely because of error.\n'
        print 'Returning incomplete playlist'
        raise
    finally:
        return ( {'complete':True, 'remaining':(song_count-len(song_names)),
            'song_names':song_names, 'stationid':stationid, 'songs':songs}
                if len(songs)==song_count else
                {'complete':False, 'remaining':(song_count-len(song_names)),
                    'song_names':song_names, 'stationid':stationid, 'songs':songs} )


def get_playlists(stationids):
    """Gets the playlists specified in the stationids list, and saves them to file"""

    #initialize the queue, priority will be maintained by songs remaining in playlist
    # (remaining, stationid)
    print 'Initializing queue with %s stations' % len(stationids)
    station_queue = PriorityQueue()

    song_list_counter = defaultdict(list)
    station_info = defaultdict(int)

    for stationid in stationids:
        try:
            station_info[stationid] = get_station_info(stationid)['song_count']
        except HTTPError as e:
            print 'Error could not add station %s' % (stationid,)
            continue

    for stationid, song_count in station_info.items():
        station_queue.put( (song_count, stationid) )


    while !station_queue.empty():

        print '-----'
        remaining, stationid = station_queue.get()
        current_station_status = get_songs(stationid,
                station_info[stationid],
                song_list_counter[stationid])
        #RESUME CODING HERE
        if !current_station_status['complete']:
            song_list_counter[stationid] = current_station_status['song_names']





def main():

    songs = get_songs('1724409')
    pprint.pprint(songs['songs'])

if __name__ == '__main__':
    main()
