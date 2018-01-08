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

def drop_schema():
    """Don't do this lightly! It drops everything. For cascading key issues.2"""
    a.db.engine.execute("drop schema if exists public cascade")
    a.db.engine.execute("create schema public")
