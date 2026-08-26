#datetime ``
from datetime import datetime
from zoneinfo import ZoneInfo

ts = datetime.now(ZoneInfo('Asia/Kolkata'))
now = datetime.now(ZoneInfo('UTC'))
local = now.astimezone(ZoneInfo('ap-south-1'))
utc = datetime.datetime.now(datetime.timezone.utc)
local_time = datetime.datetime.now()
g_date = datetime.datetime.fromisoformat('2026-08-28T09:00:00')
g_date1 = ts.strftime('%Y-%m-%d %H:%M')
t_add_7_days = ts + datetime.timedelta(days=7)

from datetime import date, time, datetime, timezone
from zoneinfo import ZoneInfo
#calling today() method
today = date.today()
print(f"Today (date): {today}")  # 2026-08-26
#Create date-only object
meeting_date = date(2026, 8, 28)
print(f"Meeting date: {meeting_date}")
#Create time-only object
meeting_time = time(14, 30, 0)  # 2:30 pm
print(f"Meeting time: {meeting_time}")
#changing date to iso format
parsed_date = date.fromisoformat('2026-08-28')
print(f"Parsed date: {parsed_date}")
# add parameter of milliseconds
precise_time = time(9, 15, 30, 500000)
print(f"Precise time: {precise_time}")
#combine date & time
meeting_dt = datetime.combine(meeting_date, meeting_time)
print(f"Meeting datetime: {meeting_dt}")

