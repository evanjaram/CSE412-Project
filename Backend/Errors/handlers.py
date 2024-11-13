from flask import jsonify
from .custom_exceptions import *

def handle_missing_parameter_error(e):
    response = jsonify({"error": e.message})
    response.status_code = 400  # Bad Request
    return response

def handle_unknown_parameter_error(e):
    response = jsonify({"error": e.message})
    response.status_code = 400  # Bad Request
    return response

def handle_empty_query_output_error(e):
    response = jsonify({"error": e.message})
    response.status_code = 404  # Not Found
    return response