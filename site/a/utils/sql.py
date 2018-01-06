import a

def commit_decorator(f):
    def wrap(*args, **kwargs):
        obj = f(*args, **kwargs)
        if obj != False:
            a.db.session.commit()
        return obj
    return wrap

def create_decorator(f):
    def wrap(*args, **kwargs):
        obj = f(*args, **kwargs)
        if obj:
            a.db.session.add(obj)
        return obj
    return wrap
