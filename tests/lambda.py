f = lambda x, y=1: x + y
if f(2) != 3:
    raise ValueError
if f(2, 2) != 4:
    raise ValueError
