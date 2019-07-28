import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from bottle import get, run, response, request
import json
import threading
import time



apiVersion = 'v3'
apiServiceName = 'youtube'
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
credentials = '4/hQGeXnB2GlNgO9Clhc4pHMNOGUyDz1P3zSK9gkaXQ3XvmswTzA8I_f4'
apiKey = 'AIzaSyCyg5Mnl8ANxANLGW7tB009V6sRVJE7KgY'
videos = {}



youtube = googleapiclient.discovery.build(apiServiceName, apiVersion, developerKey=apiKey) 


def updateVideos(username):
    print('Updating {}'.format(username))
    user = None
    if not username in videos:
        user = videos[username] = {}
    else:
        user = videos[username]

    request = youtube.channels().list(part='snippet', forUsername=username)
    response = request.execute()
    for channel in response['items']:
        # c.append(i['id'])
        request = youtube.playlists().list(part="contentDetails",channelId=channel['id'])
        response = request.execute()
        
    # for playlist in response
        for playlist in response['items']:
            request = youtube.playlistItems().list(part='snippet', playlistId= playlist['id'] )
            response = request.execute()
            
            for playlistItem in response['items']:
                if not playlistItem['id'] in user:
                    user[playlistItem['id']] = {
                        'uploaded': playlistItem['snippet']['publishedAt'],
                        'title': playlistItem['snippet']['title'],
                        'url': 'https://www.youtube.com/watch?v='+playlistItem['snippet']['resourceId']['videoId']
                    }
                    return 
                



def updater():
    while True:
        for user in videos.keys():
            updateVideos(user)       
        time.sleep(300)


def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors



@get('/videos/<username>')
@enable_cors
def getVideos(username):
    if username not in videos.keys():
        updateVideos(username)

    return json.dumps(videos[username])


if __name__ == '__main__':
    t = threading.Thread(target=updater)
    t.start()

    run(host = '0.0.0.0', port= 8000)
