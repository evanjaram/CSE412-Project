from .handlers import *
from .custom_exceptions import *

def register_error_handlers(app):
    app.register_error_handler(MissingParameterError, handle_missing_parameter_error)
    app.register_error_handler(UnknownParameterError, handle_unknown_parameter_error)
    app.register_error_handler(EmptyQueryOutputError, handle_empty_query_output_error)
    app.register_error_handler(IncorrectParameterFormError, handle_incorrect_parameter_form_error)