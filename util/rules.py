#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <echo "ZmhAdWV4LmRrCg==" | base64 -d>
# Copyright: Frede Hundewadt <echo "ZmhAdWV4LmRrCg==" | base64 -d>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Validation rules"""


def validate_fields():
    """
    Validates the QLineEdits based on RegEx
    """
    print("TODO: Create validation rules")


def check_settings(settings):
    """
    Check the vital current

    Args:
        settings: dict

    Returns:
        bool indicating if current is missing
    """
    s = settings
    try:
        return bool(s["usermail"] and s["userpass"] and s["usercountry"] and
                    s["http"] and s["smtp"] and s["port"] and s["mailto"])
    except KeyError:
        return False
