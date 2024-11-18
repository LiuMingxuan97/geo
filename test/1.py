from datetime import datetime, timedelta, timezone



start_time = datetime(2021,1,1,0,0,0, tzinfo=timezone.utc)
end_time = start_time + timedelta(seconds=122014567)
sate_time = end_time
# print(sate_time)
date_str = sate_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

print(date_str)