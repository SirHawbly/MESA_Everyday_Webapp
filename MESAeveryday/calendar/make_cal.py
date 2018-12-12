
from datetime import date, timedelta, datetime

# --


# --

MAX_DAYS = 30
today = datetime.today()
max_delta = timedelta(days=MAX_DAYS)
WEEK_DAYS = ['Monday','Tuesday','Wednesday','Thursday',
							'Friday','Saturday','Sunday']

# --


# --

def get_days():

  days = []

  for i in range(max_delta.days):

    temp_datetime = today + timedelta(i)

    temp_date = {}
    temp_date['day']     = temp_datetime.day
    temp_date['month']   = temp_datetime.month
    temp_date['year']    = temp_datetime.year
    temp_date['weekday'] = temp_datetime.weekday()
    temp_date['events'] = []
    days.append(temp_date)

  return days

# --


# --

def print_calendar(cal_days):

	# print the weekday headers (first three chars) then a newline
  for day in WEEK_DAYS:
    print(' ' + day[0:3] + '  ', end='')
  print()

	# add padding to the cal, so if the first day
	# is thursday, itll show under thursday
  day = cal_days[0]
  for i in range(day['weekday']):
  # print('mm-dd ', end='')
    print('      ', end='')

	# go through all days printing mm-dd, print newlines on sunday and 
	# at the end of the loop
  for day in cal_days:
    print(str(day['month']).zfill(2) + '-' + 
            str(day['day']).zfill(2) + ' ', end='')
    if (day['weekday'] == 6):
       print()
  print()

  return
# --


# --

def main():
  cal_days = get_days()
  # print (cal_days)

  # print the calenday using the cal_days variable we have
  print_calendar(cal_days)

# --


# --

if __name__ == '__main__':
    main()

# --
