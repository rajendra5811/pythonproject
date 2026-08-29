from datetime import datetime, date, time, timedelta, timezone

day = datetime.date(2016,3,24)
print(d)
tday = datetime.date.today()
print(tday.day)
print(tday.weekday())
print(tday.isoweekday())
today = datetime.now()

print("Today:", today)
print("After 7 days:", today + timedelta(days=7))
dt_today = datetime.datetime.today()
dt_now = datetime.datetime.now()
dt_utcnow = datetime.datetime.utcnow()

print(dt_now, dt_today, dt_utcnow)