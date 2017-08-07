#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Http functions"""

import ssl
from http.client import HTTPException
from socket import timeout
from urllib.error import URLError
from urllib.request import urlopen

from configuration import config
from . import sanitizedatafn


def get_customers(settings, employee, maxwait=2):
    """
    Download a file and return content
    Args:
        settings:
        employee:
        maxwait:

    Returns:
        customers list
    """
    s = settings.current
    e = employee.current
    f = "".join([s["pd"], s["fc"], s["sf"]])
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    data = []
    uri = "{}/{}/{}".format(s["http"], s["usercountry"], f)
    try:
        with urlopen(uri, timeout=maxwait, context=context) as response:
            data = response.read()
            data = sanitizedatafn.sanitize_customer_data(data, e["salesrep"])
    except (HTTPException, timeout, URLError) as e:
        print("HTTP ERROR: {}".format(e))

    return data


def get_employee_data(settings, maxwait=2):
    """
    Download a file and return content
    Args:
        settings:
        maxwait:

    Returns:
        current data
    """
    s = settings.current
    f = "".join([s["pd"], s["fe"], s["sf"]])
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    data = []
    uri = "{}/{}/{}".format(s["http"], s["usercountry"], f)
    try:
        with urlopen(uri, timeout=maxwait, context=context) as response:
            data = response.read()
            data = sanitizedatafn.sanitize_employee_data(data, s["usermail"], s["userpass"])
    except (HTTPException, timeout, URLError) as e:
        print("HTTP ERROR: {}".format(e))
    return data


def get_modified_date(server, country, file, maxwait=2):
    """
    Download a file and return content

    Args:
        server
        country:
        file:
        maxwait:

    Returns:
        string with date and time
    """
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    uri = "{}/{}/{}".format(server, country, file)
    try:
        with urlopen(uri, timeout=maxwait, context=context) as response:
            data = response.read().decode(config.DECODE_HTTP)
            return data
    except (HTTPException, timeout, URLError) as e:
        print("HTTP ERROR: {}".format(e))
    return ""


def get_products(settings, maxwait=2):
    """
    Download a file and return content

    Args:
        settings:
        maxwait:

    Returns:
        products list
    """
    s = settings.current
    f = "".join([s["pd"], s["fp"], s["sf"]])
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    data = []
    uri = "{}/{}/{}".format(s["http"], s["usercountry"], f)
    try:
        with urlopen(uri, timeout=maxwait, context=context) as response:
            data = response.read()
            data = sanitizedatafn.sanitize_product_data(data)
    except (HTTPException, timeout, URLError) as e:
        print("HTTP ERROR: {}".format(e))
    return data


def inet_conn_check(maxwait=2):
    """
    Check for internet connection
    Args:
        maxwait:
    Returns:
        bool indicating if internet is available
    """
    data = None
    hosts = config.CONN_CHECK
    for host in hosts:
        # noinspection PyBroadException
        try:
            data = urlopen(host, timeout=maxwait)
            break
        except:
            pass
    return bool(data)


def update_last_sync_info(settings):
    """
    Get info about file status
    Args:
        settings:
    Returns:
        Two tuples with target and date time values
    """
    s = settings.current
    f = "".join([s["pd"], s["fc"], s["sf"]])
    s["sac"] = get_modified_date(s["http"], s["usercountry"], f)
    f = "".join([s["pd"], s["fc"], s["sf"]])
    s["sap"] = get_modified_date(s["http"], s["usercountry"], f)
    return [(settings["fc"], settings["sac"]), (settings["fp"], settings["sap"])]
