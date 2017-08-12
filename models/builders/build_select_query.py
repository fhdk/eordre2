#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


def build_select_query(model, aggregates=None, filters=None, orderby=None):
    """
    Builds a query for supplied model
    Args:
        model:
        aggregates: optional list of one or more valid aggregates
        filters: optional list of one or more fields to filter query
        orderby: optional sort_order

    Returns:
        valid sql statement for model
    """
    name = model["name"]
    fld_count = len(model["fields"])
    aggr_count = 0
    whr_count = 0
    s_orderby = ""
    s_order = ""
    str_sa = ""
    str_sw = ""
    str_sf = ""

    if aggregates:
        aggr_count = len(aggregates)
    if filters:
        whr_count = len(filters)
    if orderby:
        s_orderby = orderby[0]
        s_order = orderby[1]

    # aggregate list values
    if aggregates:
        for idx, aggregate in enumerate(aggregates):
            if (idx + 1) == aggr_count:
                str_sa = str_sa + "{}".format(aggregate)
            else:
                str_sa = str_sa + "{}, ".format(aggregate)
    # table selection
    # the field order cannot be guaranteed with * alias
    # add all fields
    else:
        for idx, field in enumerate(model["fields"]):
            if (idx + 1) == fld_count:
                str_sf = str_sf + "{} ".format(field)
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
                    str_sw = str_sw + " {} {} ? {} ".format(field, operator, andor)
                else:
                    str_sw = str_sw + " {} {} ? ".format(field, operator)

    # all aggregated values where
    if str_sa and str_sw:
        if s_orderby:
            result = "SELECT {} FROM {} WHERE {} ORDER BY {} {}}".format(str_sa, name, str_sw, s_orderby, s_order)
        else:
            result = "SELECT {} FROM {} WHERE {};".format(str_sa, name, str_sw)
    # all aggregated values
    elif str_sa and not str_sw:
        if s_orderby:
            result = "SELECT {} FROM {} ORDER BY {} {}".format(str_sa, name, s_orderby, s_order)
        else:
            result = "SELECT {} FROM {};".format(str_sa, name)
    # all everything where
    elif str_sw and not str_sa:
        if s_orderby:
            result = "SELECT {} FROM {} WHERE {} ORDER BY {} {}".format(str_sf, name, str_sw, s_orderby, s_order)
        else:
            result = "SELECT {} FROM {} WHERE {};".format(str_sf, name, str_sw)
    # all everything
    else:
        if s_orderby:
            result = "SELECT {} FROM {} ORDER BY {} {}".format(str_sf, name, s_orderby, s_order)
        else:
            result = "SELECT {} FROM {};".format(str_sf, name)
    return result.replace("  ", " ")
