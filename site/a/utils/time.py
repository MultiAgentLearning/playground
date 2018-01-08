import datetime

start_date = datetime.datetime(year=1970,month=1,day=1)

def get_time():
    return datetime.datetime.utcnow()

def get_unixtime(_datetime=None):
    if _datetime:
        return (_datetime - start_date).total_seconds()
    return (datetime.datetime.utcnow() - start_date).total_seconds()

def get_datetime(timestamp):
    if not timestamp:
        return None
    return datetime.datetime.fromtimestamp(float(timestamp))

def strptime(strtime, format):
    try:
        return datetime.datetime.strptime(strtime, format)
    except Exception, e:
        return None

def get_pretty_time(dt, strf_format=None):
    if not dt:
        return None
    if strf_format:
        return dt.strftime(strf_format)
    return dt.isoformat()
