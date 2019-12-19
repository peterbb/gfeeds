from datetime import datetime
import pytz


# still not 100% perfect, but good enough, I got tired
def get_date_format(dt):
    now = datetime.now(pytz.utc)
    dtz = dt + (datetime.now()-datetime.utcnow())
    delta = now - dtz + (datetime.now()-datetime.utcnow())
    if dtz.year == now.year and dtz.month == now.month and dtz.day == now.day:
        return '%X'
    elif delta.total_seconds() < 6*24*60*60:
        return '%a %X'
    elif delta.total_seconds() < 365*60*60:
        return '%-e %b %X'
    else:
        return '%-e %b %Y %X'
