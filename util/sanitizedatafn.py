#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Data Sanitize Functions"""

from configuration import config
from util.passwdfn import check_password


def sanitize_customer_data(rawdata, sr):
    """Sanitizing the raw data from http data file"""
    clist = []
    if not rawdata:
        return clist
    rawdata = rawdata.replace(bytes("\r\n|", "ascii"), bytes("|", "ascii"))
    cdata = rawdata.split(bytes("\r\n", "ascii"))
    for data in cdata:
        if not data:
            continue
        line = data.decode(config.DECODE_HTTP).split("|")
        if line[6].strip() == sr:
            cdata = [line[0].strip(), line[1].strip(), line[2].strip(),
                     line[3].strip(), line[4].strip(), line[5].strip(),
                     line[6].strip(), line[7].strip(), line[8].strip(),
                     line[9].strip(), line[10].strip(), line[11].strip()]
            clist.append(cdata)
    return clist


def sanitize_employee_data(rawdata, em, hp):
    """Sanitizing the raw data from http data file"""
    emp = []
    if not rawdata:
        return emp
    rawdata = rawdata.replace(bytes("\r\n|", "ascii"), bytes("|", "ascii"))
    employeedata = rawdata.split(bytes("\r\n", "ascii"))
    for data in employeedata:
        if not data:
            continue
        line = data.decode(config.DECODE_HTTP).split("|")
        if line[2].lower() == em.lower():
            if check_password(hp, line[4]):
                email_lower = line[2].lower()
                country_lower = line[3].lower()
                print(country_lower)
                emp = [line[0].strip(), line[1].strip(), email_lower.strip(),
                       country_lower.strip(), 0]
    return emp


def sanitize_product_data(rawdata):
    """Sanitizing the raw data from http data file"""
    plist = []
    if not rawdata:
        return plist
    rawdata = rawdata.replace(bytes("\r\n|", "ascii"), bytes("|", "ascii"))
    productdata = rawdata.split(bytes("\r\n", "ascii"))
    for data in productdata:
        if not data:
            continue
        line = data.decode(config.DECODE_HTTP).split("|")
        pdata = (line[0].strip(), line[1].strip(), line[2].strip(), line[3].strip(), line[4].strip(),
                 line[5], line[6], line[7], line[8], line[9], line[10],
                 line[11], line[12], line[13], line[14], line[15], line[16].strip())
        plist.append(pdata)
    return plist
