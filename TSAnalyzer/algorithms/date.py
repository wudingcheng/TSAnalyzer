# encoding: utf-8
# author:      WU Dingcheng, IGG, Chinese Academy of Sciences
# email:       wudingcheng14@mails.ucas.ac.cn
# date:        20160802
# description: gps date conversion
from __future__ import division, print_function
from datetime import datetime, timedelta

STARTDATE = datetime(1980, 1, 6, 0)


def ymd2julday(year, month, day):
    """get julian day from year, month and day

    Args:
        year (int) : year input
        month (int) : month input
        day (int) : day input

    Return
        int : julday
"""
    for i in [year, month, day]:
        i = int(i)
        if not isinstance(i, int):
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
    """give a julday and return datetime object

    Args:
        jul (float) : julian day

    Return
        datetime : datetime
"""

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
    """Get julian day(JD) by modified julian day (MJD)

    Args:
        mjd (float) : modified julian day

    Return:
        int : julian day

"""
    try:
        return int(mjd + 2400000.5)
    except Exception as ex:
        raise ex


def yearfraction2date(yearfraction):
    """Convert fractional year to datetime object/list

    Args:
        yearfraction (float/list) : fractional year

    Return:
        float/list : datetime obejct/list
"""
    if isinstance(yearfraction, list):
        return list(map(yearfraction2date, yearfraction))
    else:
        mjd = yearfraction2mjd(yearfraction)
        return mjd2date(mjd)

def leap_year(y):
    if y % 400 == 0:
        return 366
    if y % 100 == 0:
        return 365
    if y % 4 == 0:
        return 366
    else:
        return 365

def fyear2date(fyear):
    """Convert fracation of year to datetime 
    """
    yr = int(fyear)
    date = datetime(yr, 1, 1, 0, 0, 0, 0)
    days = (fyear - yr) * leap_year(yr)
    date = date + timedelta(days=days)
    return date


def yearfraction2mjd(yearfraction):
    """give a fractional year and return mjd

    Args:
        yearfraction (float/list) : fractional year

    Return:
        float/list : datetime object/list
"""
    if isinstance(yearfraction, list):
        return list(map(yearfraction2mjd, yearfraction))
    else:
        return round(365.25 * (yearfraction - 1970.0) + 40587.0 + 0.1) - 0.5


def mjd2yearfraction(mjd):
    """give a mjd and return a fractional year

    Args:
        mjd (float) : modified julday day

    Returns:
        float : fractional year
"""
    try:
        return (mjd - 51544.5) / 365.25 + 2000.0
    except Exception as ex:
        raise ex


def julday2mjd(*args):
    """ julian day to modified julian day

    Args:
        julday (int) : julian day
        hour (int) : hour, optional
        minute (int) : minute, optional
        seconds (float) : seconds, optional

    Returns:
        float : modified julian day

"""
    julday = args[0]
    mjd = julday - 2400001.0
    hms = [24, 1440, 86400]
    for i, v in enumerate(args[1:]):
        mjd += v / hms[i]
    return mjd


def yr2year(yr):
    """convert two digital year to four digital year

    Args:
        yr (int) : two digital year

    Returns:
        int : four digital year

"""
    if isinstance(yr, int) and 0 <= yr <= 99:
        if 60 <= yr <= 99:
            return 1900 + yr
        if 0 <= yr <= 59:
            return 2000 + yr
    else:
        raise ValueError('yr2year error, yr is number and between 0 - 99')


def year2yr(year):
    """convert four digital year to two digital year

    Args:
        yr (int) : four digital year

    Returns:
        int : two digital year

"""
    if isinstance(year, int) and 1960 <= year <= 2059:
        if 1960 <= year <= 1999:
            return year - 1900
        if 2000 <= year <= 2059:
            return year - 2000
    else:
        raise 'year2yr error, year is number and between 1960 - 2059'


def year_doy2date(year, doy):
    """Get datetime object by year and day of year (doy)

    Args:
        year (int) : year
        doy (int) : day of year

    Returns:
        datetime: datetime of input year and doy
"""
    try:
        return datetime.strptime('%d-%d' % (year, doy), '%Y-%j')
    except Exception as ex:
        raise ex


def date2year_doy(date):
    """Get datetime's year and day

    Args:
        date (datetime) : datetime obejct

    Returns:
        tuple:
            * year (int) : year
            * doy (int) : day of year
"""
    try:
        return date.year, int(datetime.strftime(date, '%j'))
    except Exception as ex:
        raise ex


def date2yearfraction(date):
    """Get fractional year by datetime

    Args:
        date (datetime/list) : datetime object/list

    Returns:
        float/list: fractional year (/list)
"""
    if isinstance(date, list):
        return list(map(date2yearfraction, date))
    elif isinstance(date, datetime):
        return mjd2yearfraction(date2mjd(date))
    else:
        raise ValueError("date should be a datetime object or list!")


def date2mjd(date):
    """Get modified julian day by datetime obejct/list

    Args:
        datetime/list : datetime obejct/list

    Returns:
        float/list : modified julian day (/list)
"""
    if isinstance(date, list):
        return list(map(date2mjd, date))
    elif isinstance(date, datetime):
        return ymdhms2mjd(*list(date.timetuple())[:6])
    else:
        raise ValueError("date should be a datetime object or list!")


def ymdhms2mjd(*args):
    '''Convert year, month, day, hour, minute, seconds to modified julian day

    Args:
        year (int) : year
        month (int) : month
        day (int) : day
        hour (int) : hour
        minute (int) : minute
        second (float) : second

    Returns:
        float : modified julian day
    '''
    try:
        year, month, day, hour, minute, second = [int(i) for i in args]
    except Exception as ex:
        raise ex
    a = int((month - 14) / 12.0)
    mjd = int((1461 * (year + 4800 + a)) / 4.0)
    mjd += int((367 * (month - 2 - 12 * a)) / 12.0)
    x = int((year + 4900 + a) / 100.0)
    mjd -= int((3 * x) / 4.0)
    mjd += day - 2432075.5

    # mjd -= 0.5  # 0 hours; above JD is for midday, switch to midnight.
    mjd += hour / 24 + minute / 1440 + second / 86400
    return mjd


def mjd2date(mjd):
    '''Convert modified julian day to datetime obejct

    Args:
        mjd (float) : modified julian day

    Returns:
        datetime : datetime obejct
    '''
    # if not isinstance(int(mjd), int):
    #     raise 'mjd2date, mjd should be a number'
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
    """ Convert GPS Week to datetime object

    Args:
        gpsweek (int) : GPS Week

    Returns:
        datetime : datetime object
    """
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
    """ Convert datetime obejct to GPS Week

    Args:
        date (datetime) : datetime obejct

    Return:
        int : GPS Week
    """
    if not isinstance(date, datetime):
        raise ValueError("date should be datetime object")
    days = (date - STARTDATE).days
    weeks = int(days / 7)
    return weeks * 10 + date.isoweekday()
