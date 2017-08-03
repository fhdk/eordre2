#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


def build_select_query(model_def, aggregates=None, filters=None, sort_order=None):
    """
    Builds a query for supplied model
    Args:
        model_def:
        aggregates: optional list of one or more valid aggregates
        filters: optional list of one or more fields to filter query
        sort_order: optional sort_order

    Returns:
        valid sql statement for model
    """
    name = model_def["name"]
    fld_count = len(model_def["fields"])
    aggr_count = 0
    whr_count = 0
    s_orderby = ""
    str_sa = ""
    str_sw = ""
    str_sf = ""

    if aggregates:
        aggr_count = len(aggregates)
    if filters:
        whr_count = len(filters)
    if sort_order:
        s_orderby = sort_order

    # aggregate list values
    if aggregates:
        for idx, aggregate in enumerate(aggregates):
            if (idx + 1) == aggr_count:
                str_sa = str_sa + "{}".format(aggregate)
            else:
                str_sa = str_sa + "{}, ".format(aggregate)
    # table selection
    # the field order cannot be guaranteed with * alias
    # add a select field list with all fields
    else:
        for idx, field in enumerate(model_def["fields"]):
            if (idx + 1) == fld_count:
                str_sf = str_sf + "{}".format(field)
            else:
                str_sf = str_sf + "{}, ".format(field)

    # where 'field' operator 'value'
    if filters:
        for idx, s_item in enumerate(filters):
            field = s_item[0]
            operator = s_item[1].upper()
            andor = ""
            if len(s_item) == 3:
                andor = s_item[2]
            if (idx + 1) == whr_count:
                str_sw = str_sw + " {} {} ?".format(field, operator)
            else:
                if andor:
                    str_sw = str_sw + " {} {} ? {}".format(field, operator, andor)
                else:
                    str_sw = str_sw + " {} {} ?".format(field, operator)

    # select aggregated values where
    if str_sa and str_sw:
        if s_orderby:
            return "SELECT {} FROM {} WHERE {} ORDER BY {}".format(str_sa, name, str_sw, s_orderby)
        else:
            return "SELECT {} FROM {} WHERE {};".format(str_sa, name, str_sw)
    # select aggregated values
    elif str_sa and not str_sw:
        if s_orderby:
            return "SELECT {} FROM {} ORDER BY {}".format(str_sa, name, s_orderby)
        else:
            return "SELECT {} FROM {};".format(str_sa, name)
    # select everything where
    elif str_sw and not str_sa:
        if s_orderby:
            return "SELECT {} FROM {} WHERE {} ORDER BY {}".format(str_sf, name, str_sw, s_orderby)
        else:
            return "SELECT {} FROM {} WHERE {};".format(str_sf, name, str_sw)
    # select everything
    else:
        if s_orderby:
            return "SELECT {} FROM {} ORDER BY {}".format(str_sf, name, s_orderby)
        else:
            return "SELECT {} FROM {};".format(str_sf, name)
