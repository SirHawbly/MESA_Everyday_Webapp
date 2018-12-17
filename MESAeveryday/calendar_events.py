# # modified from google dev
# https://developers.google.com/calendar/quickstart/python 

# # here is the first line
# # this file is for a Google
# # Calendar Bridge

from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime as d
import json

# --


# --

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'

today = d.datetime.today()
MAX_DAYS = 30
max_delta = d.timedelta(days=MAX_DAYS)

MONTHS = ['None', 'January', 'February', 'March', 
          'April', 'May', 'June', 'July', 
          'August', 'September', 'October', 'November',
          'December']

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
    tokens = date_str.split('T')

	  # pull the first half with the date info
	  # parse it by hyphens
    date_obj = tokens[0].split('-')
    t['yr'] = int(date_obj[0])
    t['mt'] = int(date_obj[1])
    t['dy'] = int(date_obj[2]) 

    # pull the second half of the date 
    # parse it by hyphens then by colons
    time_obj = tokens[1].split('-')
    time_obj = time_obj[0].split(':')
    t['hr'] = int(time_obj[0])
    t['mn'] = int(time_obj[1])

		# return the dict obj
    # print("passed obj:", json_obj, '\nparsed obj:',t)
    return t 

# --


# --

def add_time_tuples(event):
    """
      parses the time values in an event and 
      creates a tuple with the month(mt), 
      day(dy), year(yr), hour(hr) and minute(mn) 
      for the start and end times of the event.

      input:
        event['start'] = 
          '2018-11-18T18:30:00-08:00' 

      output:
        event['start_tuple'] =
            {'yr':2018,'mt':11,'dy':18,'hr':18,'mn':30}
    """

    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))
    start_tuple = parse_time_string(start)
    end_tuple = parse_time_string(end)

    event['start_tuple'] = start_tuple
    event['end_tuple'] = end_tuple
    # print(start_tuple,end_tuple,"\n")

# --

def add_time_strings(event):
    """
      adds the date as a string to an event using
      its time tuple value

      input:
        event['start_tuple'] =
            {'yr':2018,'mt':11,'dy':18,'hr':18,'mn':30} 

      output:
        event['start_string'] =
            "November-18-2018 18:30" 

    """

    start_tuple = event['start_tuple']
    end_tuple = event['end_tuple']

    start_string = MONTHS[start_tuple['mt']] \
                   + "-" + str(start_tuple['dy']) \
                   + "-" + str(start_tuple['yr']) \
                   + " " + str(start_tuple['hr']) \
                   + ":" + str(start_tuple['mn']).zfill(2)

    end_string = MONTHS[end_tuple['mt']] \
                 + "-" + str(end_tuple['dy']) \
                 + "-" + str(end_tuple['yr']) \
                 + " " + str(end_tuple['hr']) \
                 + ":" + str(end_tuple['mn']).zfill(2)

    event['start_string'] = start_string
    event['end_string'] = end_string

# --


# --
def add_remain_days(event):
    """
      parses an events time tuple for its
      starting time, and calculates the 
      remaining days until it starts.

      input:
        event['start_tuple'] =
            {'y':2018,'t':11,'d':18,'h':18,'m':30}

      output:
        event['remain_days'] = 18
    """

    # parse the date_time string and get a dict back
    t = event['start_tuple']
		
		# create a datetime obj with the data from dict
    event_day = d.datetime(hour=t['hr'], minute=t['mn'], day=t['dy'], month=t['mt'], year=t['yr'])

    # pull the current day
    today = d.datetime.today()

    # convert todays date to be midnight
    today = d.datetime.combine(today, d.datetime.min.time())

    # print(event_day)
    # print(today)
    event['remain_days'] = (event_day - today).days

# --


# --

def get_event_list():
    """
      Shows basic usage of the Google Calendar API.
      Prints the start and name of the next 10 events on the user's calendar.

      Prints the next 10 events after today, and adds them to a list of the 
      next 30 days.
    """

    # grab the users token (has user's access and refresh tokens)
		# if they dont exist then they are created upon autorization
    store = file.Storage('MESAeveryday/credentials/token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('MESAeveryday/credentials/cal-client-cred.json', SCOPES)
        creds = tools.run_flow(flow, store)

    # get a HTTP connection to googles calendar
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    # Call the Calendar API
    now = d.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=30, singleEvents=True,
                                        orderBy='startTime').execute()
    # grab the results
    events = events_result.get('items', [])
    
    for event in events:
        add_time_tuples(event)
        add_time_strings(event)
        add_remain_days(event)

    # if we have not found any events print
    # failure.
    if not events:
        print('No upcoming events found.')

    return events

# --


# --

def main():
    """
      Shows basic usage of get_event_list.
    """

    events = get_event_list()

    for event in events[:3]:
        print(events.index(event))
        print(event['summary'])
        print(event['location'])
        print(event['start_string'],'to',event['end_string'])
        print(event['remain_days'],'\n')

# --


# --

if __name__ == '__main__':
    main()

# --




















