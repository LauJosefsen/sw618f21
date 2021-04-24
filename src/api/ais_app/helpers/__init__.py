def build_dict(cursor, row):
    x = {}
    for key, col in enumerate(cursor.description):
        x[col[0]] = row[key]
    return x
