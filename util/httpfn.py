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
    """Download a file and return content"""
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    data = []
    uri = "{}/{}/{}{}{}".format(settings["http"], employee["country"],
                                settings["pf"], settings["fc"], settings["sf"])
    try:
        with urlopen(uri, timeout=maxwait, context=context) as response:
            data = response.read()
            data = sanitizedatafn.sanitize_customer_data(data, employee["salesrep"])
    except (HTTPException, timeout, URLError) as e:
        print("{}\n{}".format(uri, e))
    return data


def get_employee_data(settings, maxwait=2):
    """Download a file and return content"""
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    data = []
    uri = "{}/{}/{}{}{}".format(settings["http"], settings["usercountry"],
                                settings["pf"], settings["fe"], settings["sf"])
    try:
        with urlopen(uri, timeout=maxwait, context=context) as response:
            data = response.read()
            data = sanitizedatafn.sanitize_employee_data(data, settings["usermail"], settings["userpass"])
    except (HTTPException, timeout, URLError) as e:
        print("{}\n{}".format(uri, e))
    return data


def get_modified_data(settings, file, maxwait=2):
    """Download a file and return content"""
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    uri = "{}/{}/{}{}{}".format(settings["http"], settings["usercountry"],
                                settings["pd"], file, settings["sf"])
    try:
        with urlopen(uri, timeout=maxwait, context=context) as response:
            data = response.read().decode(config.DECODE)
            # return int(time.mktime(time.strptime(data, "%Y-%m-%d %H:%M:%S")))
            return data
    except (HTTPException, timeout, URLError) as e:
        print("{}\n{}".format(uri, e))
    return ""


def get_products(settings, maxwait=2):
    """Download a file and return content"""
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    productdata = []
    uri = "{}/{}/{}{}{}".format(settings["http"], settings["usercountry"],
                                settings["pf"], settings["fp"], settings["sf"])
    try:
        with urlopen(uri, timeout=maxwait, context=context) as response:
            data = response.read()
            productdata = sanitizedatafn.sanitize_product_data(data)
    except (HTTPException, timeout, URLError) as e:
        print("{}\n{}".format(uri, e))
    return productdata


def inet_conn_check(maxwait=2):
    """Check for internet connection"""
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
    """Get info about file status"""
    ac = get_modified_data(settings, settings["fc"])
    ap = get_modified_data(settings, settings["fp"])
    return [(settings["fc"], ac), (settings["fp"], ap)]
