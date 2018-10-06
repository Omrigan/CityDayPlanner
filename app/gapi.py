from __future__ import print_function

import datetime
import re

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from datetime import datetime
import dateutil.parser
# if sys.version_info < (3, 7):
#     from backports.datetime_fromisoformat import MonkeyPatch
#     MonkeyPatch.patch_fromisoformat()

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'

from parser import make_request
def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    store = file.Storage('../token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('../data/credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    # Call the Calendar API
    now = datetime.now().utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='5ash6ru08ueesck6abulgt0vtk@group.calendar.google.com',
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    print()
    return parse_events(events_result['items'])

def get_location(txt):
    result = make_request('place/findplacefromtext', {
        "input": txt,
        "inputtype": "textquery",
        "locationbias": "ipbias",
        "fields": "geometry/location"
    })
    #print(result)
    return result['candidates'][0]['geometry']['location']


def parse_events(events):
    ordered_events = []
    for event in events:
        result = {

        }
        #print(event)
        sum = event['summary'].strip()

        descr = event.get('description') or ""

        if sum[0] == '?':
            sum = sum[1:].strip().lower()
            words = sum.split(" ")

            result['type'] = re.sub(r'[^\w]','',words[0])
            descr += " ".join(words[1:])

        else:
            result['type'] = 'fixed_place'
            result['name'] = sum
            result['location'] = get_location(event['location'])
        descr = descr.lower()
        start = event['start']['dateTime']
        end = event['end']['dateTime']
        start_time = dateutil.parser.parse(start)
        finish_time = dateutil.parser.parse(end)
        delay = (finish_time - start_time).seconds / 60
        result['delay'] = delay
        if '#flexible' not in descr:
            result['start_time'] = start_time.strftime('%H:%M')
            result['finish_time'] = finish_time.strftime('%H:%M')

        brands = re.findall("#[\w\s]+#", descr)
        if len(brands)>0:
            result['brand'] = brands[0][1:-1]
        ordered_events.append(result)
    return {"ordered_events": ordered_events}


if __name__ == '__main__':
    main()
