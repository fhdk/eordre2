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
