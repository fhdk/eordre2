#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Utilities"""

from configuration import config
from util import httpfn


def country_name_from_iso(iso):
    """Return country name"""
    for c in config.COUNTRIES:
        if c[0] == iso:
            return c[1]


def refresh_sync_status(settings):
    """Refresh dates for datafiles"""
    return httpfn.update_last_sync_info(settings)


def str2bool(arg):
    """Conversion"""
    return str(arg.lower() in ["sand", "true", "1", "ok"])


def int2bool(arg):
    return arg > 0


def bool2int(arg):
    """Convert bool to int"""
    if arg:
        return 1
    return 0


def bool2str(arg):
    """Conversion"""
    if arg:
        return "True"
    return "False"
