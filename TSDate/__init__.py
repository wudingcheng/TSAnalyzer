# encoding: utf-8
# author:      WU Dingcheng, IGG, Chinese Academy of Sciences
# email:       wudingcheng14@mails.ucas.ac.cn
# date:        20160802
# description: gps date conversion
from __future__ import division
from datetime import datetime, timedelta

STARTDATE = datetime(1980, 1, 6, 0)


def ymd2julday(year, month, day):
    '''give year, month, day and return julday'''
    for i in [year, month, day]:
        i = int(i)
        if type(i) is not int:
            raise 'input is not number'
    if year < 1801 or year > 2099:
        raise "Year is out of range"

    a = int((14 - month) / 12)
    y = year + 4800 - a
    m = month + 12 * a - 3
    jul = day + int((153 * m + 2) / 5) + 365 * y + \
        int(y / 4) - int(y / 100) + int(y / 400) - \
        32045
    return int(jul)


def julday2date(jul):
    '''give a julday and return datetime object'''
    if not isinstance(jul, int):
        raise 'julday is an int number'
    l = jul + 68569
    n = int((4 * l) / 146097.0)
    l -= int(((146097 * n) + 3) / 4.0)
    i = int((4000 * (l + 1)) / 1461001)
    l -= int((1461 * i) / 4.0) - 31
    j = int((80 * l) / 2447.0)
    day = l - int((2447 * j) / 80.0)
    l = int(j / 11.0)
    month = j + 2 - (12 * l)
    year = 100 * (n - 49) + i + l
    return datetime(year, month, day)


def mjd2julday(mjd):
    '''give a mjd and return julday'''
    try:
        return int(mjd + 2400000.5)
    except Exception, ex:
        raise ex


def yearfraction2date(yearfraction):
    mjd = yearfraction2mjd(yearfraction)
    return mjd2date(mjd)


def yearfraction2mjd(yearfraction):
    '''give a fractional year and return mjd'''
    try:
        return round(365.25 * (yearfraction - 1970.0) + 40587.0 + 0.1) - 0.5
    except Exception, ex:
        raise ex

    # return (yearfraction - 2000) * 365.25 + 51544.5


def mjd2yearfraction(mjd):
    '''give a mjd and return a fractional year'''
    try:
        return (mjd - 51544.5) / 365.25 + 2000.0
    except Exception, ex:
        raise ex


def julday2mjd(*args):
    '''args: julday, (hour, minute, second) optional'''
    julday = args[0]
    mjd = julday - 2400001.0
    hms = [24, 1440, 86400]
    for i, v in enumerate(args[1:]):
        mjd += v / hms[i]
    return mjd


def yr2year(yr):
    if type(yr) is int and 0 <= yr <= 99:
        if 60 <= yr <= 99:
            return 1900 + yr
        if 0 <= yr <= 59:
            return 2000 + yr
    else:
        raise 'yr2year error, yr is number and between 0 - 99'


def year2yr(year):
    if type(year) is int and 1960 <= year <= 2059:
        if 1960 <= year <= 1999:
            return year - 1900
        if 2000 <= year <= 2059:
            return year - 2000
    else:
        raise 'year2yr error, year is number and between 1960 - 2059'


def year_doy2date(year, doy):
    ''' give year and doy, return date object'''
    try:
        return datetime.strptime('%d-%d' % (year, doy), '%Y-%j')
    except Exception, ex:
        raise ex


def date2year_doy(date):
    ''' give a date object and return year and doy'''
    try:
        return date.year, int(datetime.strftime(date, '%j'))
    except Exception, ex:
        raise ex


def date2yearfraction(date):
    return mjd2yearfraction(date2mjd(date))


def date2mjd(date):
    return ymdhms2mjd(*list(date.timetuple())[:6])


def ymdhms2mjd(*args):
    ''' args: year, month, day, hour, minute, second;
        give args and return mjd
    '''
    try:
        year, month, day, hour, minute, second = [int(i) for i in args]
    except Exception, ex:
        raise ex
    a = int((month - 14) / 12.0)
    mjd = int((1461 * (year + 4800 + a)) / 4.0)
    mjd += int((367 * (month - 2 - 12 * a)) / 12.0)
    x = int((year + 4900 + a) / 100.0)
    mjd -= int((3 * x) / 4.0)
    mjd += day - 2432075.5

    mjd -= 0.5  # 0 hours; above JD is for midday, switch to midnight.
    mjd += hour / 24 + minute / 1440 + second / 86400
    return mjd


def mjd2date(mjd):
    ''' give mjd and return date object'''
    if not isinstance(int(mjd), int):
        raise 'mjd2date, mjd should be a number'
    j = int(mjd + 2400001.0)
    date = julday2date(j).timetuple()
    f = 24.0 * (mjd - int(mjd))
    hour = int(f)
    f = 60.0 * (f - hour)
    minute = int(f)
    second = int(60.0 * (f - minute))
    return datetime(date.tm_year, date.tm_mon, date.tm_mday,
                    hour, minute, second)


def gpsweek2date(gpsweek):
    if 10000 <= gpsweek <= 99999:
        week = int(gpsweek / 10)
        day = gpsweek % 10
    elif 1000 <= gpsweek <= 9999:
        week = gpsweek
        day = 0
    else:
        raise ValueError("GPS Week Error Input")
    if 0 <= day <= 6:
        return STARTDATE + timedelta(week * 7 + day)
    elif day == 7:
        return None
    else:
        raise ValueError('GPS Week Error Input')


def date2gpsweek(date):
    if not isinstance(date, datetime):
        raise ValueError("date should be datetime object")
    days = (date - STARTDATE).days
    weeks = int(days / 7)
    return weeks * 10 + date.isoweekday()


# if __name__ == '__main__':
#     d = datetime(2016, 8, 24, 12)
#     print date2year_doy(d)
#     print mjd2julday(51544.5)
