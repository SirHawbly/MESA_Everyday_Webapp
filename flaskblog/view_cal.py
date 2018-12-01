# # modified from google dev
# https://developers.google.com/calendar/quickstart/python 

# # here is the first line
# # this file is for a Google
# # Calendar Bridge

from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime as d
from make_cal import get_days,print_calendar
import json

# --

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'

# --


# --

def parse_time_string(date_str):
    """
        input:
        '2018-11-18T18:30:00-08:00' 

        output:
        {'y':2018,'t':11,'d':18,'h':18,'m':30}
    """

    t = {}

    # print(json_obj)
    tokens = date_str.split("T")

	  # pull the first half with the date info
	  # parse it by hyphens
    date_obj = tokens[0].split("-")
    t['y'] = int(date_obj[0])
    t['t'] = int(date_obj[1])
    t['d'] = int(date_obj[2]) 

    # pull the second half of the date 
    # parse it by hyphens then by colons
    time_obj = tokens[1].split("-")
    time_obj = time_obj[0].split(":")
    t['h'] = int(time_obj[0])
    t['m'] = int(time_obj[1])

		# return the dict obj
    # print("passed obj:", json_obj, '\nparsed obj:',t)
    return t 

# --


# --

def get_remain_days(json_event_time):
    """input:
				{'dateTime': '2018-11-18T18:30:00-08:00', 
        'timeZone': 'America/Los_Angeles'}

			 output:
				time delta from 0:00am today to provided 
				datetime time. (0:00am today -> 6:30pm 11-18-2018)
    """

    # print (json_event_time)
		# pull out the date_time of the json obj
    date_time = json_event_time['dateTime']

    # parse the date_time string and get a dict back
    t = parse_time_string(date_time)
		
		# create a datetime obj with the data from dict
    event_day = d.datetime(hour=t['h'], minute=t['m'], day=t['d'], month=t['t'], year=t['y'])

    # pull the current day
    today = d.datetime.today()

    # convert todays date to be midnight
    today = d.datetime.combine(today, d.datetime.min.time())

    # print(event_day)
    # print(today)
    return event_day - today

# --


# --

def main():
    """
      Shows basic usage of the Google Calendar API.
      Prints the start and name of the next 10 events on the user's calendar.

      Prints the next 10 events after today, and adds them to a list of the 
      next 30 days.
    """

    # grab the users token (has user's access and refresh tokens)
		# if they dont exist then they are created upon autorization
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('event-client-cred.json', SCOPES)
        creds = tools.run_flow(flow, store)

    # get a HTTP connection to googles calendar
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    # grab the results
    events = events_result.get('items', [])

    # if we have not found any events print
    # failure.
    if not events:
        print('No upcoming events found.')

    print('event format and queries')
    print('\nGetting the upcoming 10 events...\n')
    print('first event:', json.dumps(events[0], indent=4, sort_keys=True))
    start = events[0]['start'].get('dateTime', events[0]['start'].get('date'))
    print ('\nstart time:', start, '\nevent summary:', events[0]['summary'])
    print ('remaining days:', get_remain_days(events[0]['start']).days)

    input('\nwaiting....\n')
    
    # put all events in their corresponding dates
    # using the json parsing on the event's time
    # value (T = '2018-11-24T08:00-14:00-800')
    month = get_days()

    print('\nmonth day formatting')
    print('\nGetting the next 30 days...\n', month)
    print('\nPrinting it prettier...\n')
    print_calendar(month) 
		
    input('\nwaiting....\n')

    print('\nAdding events to the day they correspond to')
		
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        start = parse_time_string(start)
        # print(event, start)
        for day in month:
            # print(day)
            if (start['d'] == day['day'] and start['t'] == day['month']):
                 day['events'] += [event,]


    print('\nPrinting all of the Days (within 30 of today) that have events')

    # go through all of the days and see if they 
    # have an event, and print that one out
    for day in month:
        if (len(day['events']) != 0):
            print('Day that has Events:', day['month'], day['day'])
            for event in day['events']:
                print(day['events'].index(event), '\tevent timestamp:', event['start'])
                print('\tevent summary:', event['summary'], '\n')

    print('\nDone.\n')

    return events

# --


# --

if __name__ == '__main__':
    main()

# --
