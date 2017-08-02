def update_query(model_def, update_list, where_list):
    str_uf = ""
    str_uw = ""
    name = model_def["name"]
    u_fields = len(update_list)
    u_wheres = len(where_list)

    # field=value part
    for idx, field in enumerate(update_list):
        if (idx + 1) == u_fields:
            str_uf = str_uf + "{}=?".format(field)
        else:
            str_uf = str_uf + "{}=?, ".format(field)

    # where 'field' operator
    for idx, u_item in enumerate(where_list):
        field = u_item[0]
        operator = u_item[1].upper()
        andor = ""
        if len(u_item) == 3:
            andor = u_item[2].upper()
        if (idx + 1) == u_wheres:
            str_uw = str_uw + " {} {} ?".format(field, operator)
        else:
            if len(u_item) == 3:
                str_uw = str_uw + " {} {} ? {}".format(field, operator, andor)
            else:
                str_uw = str_uw + " {} {} ?".format(field, operator)

    return "UPDATE {} SET {} WHERE {};".format(name, str_uf, str_uw)