def select_query(model_def, aggregate_list, where_list, sort_order):
    s_name = model_def["name"]
    num_sf = len(model_def["fields"])
    num_sa = 0
    num_sw = 0
    s_orderby = ""
    str_sa = ""
    str_sw = ""
    str_sf = ""

    if aggregate_list:
        num_sa = len(aggregate_list)
    if where_list:
        num_sw = len(where_list)
    if sort_order:
        s_orderby = sort_order

    # aggregate list values
    if aggregate_list:
        for idx, aggregate in enumerate(aggregate_list):
            if (idx + 1) == num_sa:
                str_sa = str_sa + "{}".format(aggregate)
            else:
                str_sa = str_sa + "{},".format(aggregate)
    # table selection
    # the field order cannot be guaranteed with * alias
    # add a select field list with all fields
    else:
        for idx, field in enumerate(model_def["fields"]):
            if (idx + 1) == num_sf:
                print("fields {} == idx {} ".format(num_sf, idx))
                str_sf = str_sf + "{}".format(field)
            else:
                str_sf = str_sf + "{},".format(field)

    # where 'field' operator 'value'
    if where_list:
        for idx, s_item in enumerate(where_list):
            field = s_item[0]
            operator = s_item[1].upper()
            andor = ""
            if len(s_item) == 3:
                andor = s_item[2]
            if (idx + 1) == num_sw:
                str_sw = str_sw + " {} {} ?".format(field, operator)
            else:
                if andor:
                    str_sw = str_sw + " {} {} ? {}".format(field, operator, andor)
                else:
                    str_sw = str_sw + " {} {} ?".format(field, operator)

    # select aggregated values where
    if str_sa and str_sw:
        if s_orderby:
            return "SELECT {} FROM {} WHERE {} ORDER BY {}".format(str_sa, s_name, str_sw, s_orderby)
        else:
            return "SELECT {} FROM {} WHERE {};".format(str_sa, s_name, str_sw)
    # select aggregated values
    elif str_sa and not str_sw:
        if s_orderby:
            return "SELECT {} FROM {} ORDER BY {}".format(str_sa, s_name, s_orderby)
        else:
            return "SELECT {} FROM {};".format(str_sa, s_name)
    # select everything where
    elif str_sw and not str_sa:
        if s_orderby:
            return "SELECT {} FROM {} WHERE {} ORDER BY {}".format(str_sf, s_name, str_sw, s_orderby)
        else:
            return "SELECT {} FROM {} WHERE {};".format(str_sf, s_name, str_sw)
    # select everything
    else:
        if s_orderby:
            return "SELECT {} FROM {} ORDER BY {}".format(str_sf, s_name, s_orderby)
        else:
            return "SELECT {} FROM {};".format(str_sf, s_name)
