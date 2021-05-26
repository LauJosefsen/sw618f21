def build_dict(cursor, row):
    x = {}
    for key, col in enumerate(cursor.description):
        x[col[0]] = row[key]
    return x


class MinMaxXy:
    def __init__(self, min_x, min_y, max_x, max_y):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    @classmethod
    def from_coords(cls, coords):
        min_x = min(coords, key=lambda x: x[0])[0]
        min_y = min(coords, key=lambda x: x[1])[1]
        max_x = max(coords, key=lambda x: x[0])[0]
        max_y = max(coords, key=lambda x: x[1])[1]
        return cls(min_x, min_y, max_x, max_y)
