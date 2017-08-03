#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Validation rules"""


def validate_fields():
    """
    Validates the QLineEdits based on RegEx
    """
    print("TODO: Create validation rules")


def check_settings(settings):
    """
    Check the vital settings

    Args:
        settings: dict

    Returns:
        bool indicating if settings is missing
    """
    try:
        return bool(
            settings["usermail"] and
            settings["userpass"] and
            settings["usercountry"] and
            settings["http"] and
            settings["smtp"] and
            settings["port"] and
            settings["mailto"])
    except KeyError:
        return False
