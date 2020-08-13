from functools import wraps
from flask import (
    current_app,
    jsonify,
    request, 
    g
)
from werkzeug.exceptions import BadRequest

from app.models import User


def validate_json(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            request.json
        except BadRequest as e:
            msg = "payload must be a valid json"
            return jsonify({"error": msg}), 400
        return f(*args, **kwargs)
    return wrapper

def required_params(*args):
    """Decorator factory to check request data for POST requests and return
    an error if required parameters are missing."""
    required = list(args)
 
    def decorator(fn):
        """Decorator that checks for the required parameters"""
 
        @wraps(fn)
        def wrapper(*args, **kwargs):
            missing = [r for r in required if r not in request.get_json()]
            if missing:
                response = {
                    "status": "error",
                    "message": f"Request JSON is missing {', '.join(missing)}",
                    "missing": missing
                }
                return jsonify(response), 400
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        # if user is not logged in    
        if not request.headers.get("Authorization", None):
            return jsonify({"error": "access-token is required in headers."})
        
        user = User.query.filter(User.jwt==request.headers["Authorization"]).first()
        if not user:
            return jsonify({"error": "access-token is invalid."}), 400

        # make user available down the pipeline via flask.g
        g.user = user
        # finally call f. f() now haves access to g.user
        return f(*args, **kwargs)
   
    return wrap


