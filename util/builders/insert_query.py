def insert_query(model_def):
    i_name = model_def["name"]
    num_sf = len(model_def["fields"])
    str_if = ""
    for idx, field in enumerate(model_def["fields"]):
        if (idx + 1) == num_sf:
            str_if = str_if + "?"
        else:
            str_if = str_if + "?,"
    return "INSERT INTO {} VALUES ({});".format(i_name, str_if)
