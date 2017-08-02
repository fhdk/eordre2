def delete_query(model_def, where_list):
    d_name = model_def["name"]
    num_dw = len(where_list)
    str_dw = ""
    # where 'field' operator
    for idx, d_item in enumerate(where_list):
        field = d_item[0]
        operator = d_item[1].upper()
        andor = ""
        if len(d_item) == 3:
            andor = d_item[2].upper()
        if (idx + 1) == num_dw:
            str_dw = str_dw + " {} {} ?".format(field, operator)
        else:
            if andor:
                str_dw = str_dw + " {} {} ? {}".format(field, operator, andor)
            else:
                str_dw = str_dw + " {} {} ?".format(field, operator)

    return "DELETE FROM {} WHERE {};".format(d_name, str_dw)
