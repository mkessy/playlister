import time
import requests
import simplejson as json
import pprint
import pickle

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


#BEGIN UTILITY FUNCTIONS
HTTPError = requests.exceptions.HTTPError

def get_station_info(stationid):
    """Returns a dictionary with relevant station info"""

    station_url = BASE_STATION % (stationid,)
    res = requests.get(station_url, **REQUEST_KWARGS)

    if res.status_code != 200:
        raise HTTPError('Status: %s\nUrl: %s' % (res.status_code, res.url))

    station_info = res.json()
    return station_info


def get_songs(stationid):
    """Attempts to track all songs from the given stationid"""

    next_song_url = BASE_SONG % (stationid,)

    try:
        station_info = get_station_info(stationid)
    except HTTPError as e:
        print 'Error opening stationid: %s' % stationid
        raise

    songs = []
    song_names = []
    song_count = station_info['song_count']
#    max_tries = song_count + 10
    max_tries = 5
    SLEEP_TIME = 5

    tries = 0
    while len(songs) < song_count and tries < max_tries:
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

        time.sleep(3)
        tries += 1
    print '\n=======================\n'
    print 'Finished with main loop...\n'
    print 'Returning list with %s songs of a possible %s\n' % (len(songs), song_count)
    return {'complete':True, 'songs':songs} if len(songs)==song_count else {'complete':False, 'songs':songs}

def main():

    songs = get_songs('1724409')

    pprint.pprint(songs['songs'])

    with open('1724409.json', 'w') as f:
        json.dump(songs['songs'], f)

    with open('1724409.txt', 'w') as f:
        pickle.dump(songs['songs'], f)


if __name__ == '__main__':
    main()
