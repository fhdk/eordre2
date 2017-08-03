#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


def update_query(model_def, update_list, where_list):
    str_uf = ""
    str_uw = ""
    name = model_def["name"]
    fld_count = len(update_list)
    whr_count = len(where_list)

    # field=value part
    for idx, field in enumerate(update_list):
        if (idx + 1) == fld_count:
            str_uf = str_uf + "{}=?".format(field)
        else:
            str_uf = str_uf + "{}=? , ".format(field)

    # where 'field' operator
    for idx, u_item in enumerate(where_list):
        field = u_item[0]
        operator = u_item[1].upper()
        andor = ""
        if len(u_item) == 3:
            andor = u_item[2].upper()
        if (idx + 1) == whr_count:
            str_uw = str_uw + " {} {} ?".format(field, operator)
        else:
            if len(u_item) == 3:
                str_uw = str_uw + " {} {} ? {}".format(field, operator, andor)
            else:
                str_uw = str_uw + " {} {} ?".format(field, operator)

    return "UPDATE {} SET {} WHERE {};".format(name, str_uf, str_uw)
