#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


def build_drop_query(model):
    """
    Builds a query for supplied model
    Args:
        model:

    Returns:
        valid sql statement for model
    """
    name = model["name"]

    return "DROP TABLE IF EXISTS {};".format(name)
