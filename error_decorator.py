from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from conf.db import session


def db_error_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            session.rollback()
            return f"Database error: {str(e)}"
        except AttributeError as e:
            return f"Attribute error: {str(e)}"
        except KeyError as e:
            return f"Key error: '{e}' not found in model dictionary."
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    return wrapper
