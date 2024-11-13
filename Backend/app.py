from db.queries import *
from flask import Flask, jsonify, request
from Errors import *
from Errors.custom_exceptions import *
from Util.util import *

app = Flask(__name__)
register_error_handlers(app)

"""
    Get total cases by country within a window of time

    Params:
        - country: name of country (or location in general)
        - start: start date for window of time
        - end: end date for window of time

    Returns:
        - list of tuples (date and total cases value)
"""
@app.route('/api/cases-by-country', methods=['GET'])
def cases_by_country():
    accepted_params = ['country', 'end', 'start']
    unknown_params = [key for key in request.args.keys() if key not in accepted_params]

    if unknown_params:
        raise UnknownParameterError(f"Unknown parameters: {', '.join(unknown_params)}")

    country = request.args.get('country')
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    missing_vars = find_missing_variables(country=country, start_date=start_date, end_date=end_date)

    if missing_vars:
        raise MissingParameterError(f"Missing required parameters: {', '.join(missing_vars)}")

    try:
        params = (country, start_date, end_date)
        query = """SELECT TO_CHAR(c_date, 'YYYY-MM-DD') AS formatted_date, c_cases FROM cases JOIN location ON 
                    l_nationkey = c_nationkey WHERE l_nationname = %s AND c_date BETWEEN %s AND %s;"""
        data = execute_query(query, params, True)
        
        if data:
            return jsonify(data)
        else:
            raise EmptyQueryOutputError(f"Query returned no rows. Query: '{query}' with parameters: {params}")
    except Exception as e:
        return jsonify({"error": str(e)}), e.status_code

   
"""
    Get total deaths by country within a window of time

    Params:
        - country: name of country (or location in general)
        - start: start date for window of time
        - end: end date for window of time

    Returns:
        - list of tuples (date and total deaths value)
"""
@app.route('/api/deaths-by-country', methods=['GET'])
def deaths_by_country():
    accepted_params = ['country', 'end', 'start']
    unknown_params = [key for key in request.args.keys() if key not in accepted_params]

    if unknown_params:
        raise UnknownParameterError(f"Unknown parameters: {', '.join(unknown_params)}")

    country = request.args.get('country')
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    missing_vars = find_missing_variables(country=country, start_date=start_date, end_date=end_date)

    if missing_vars:
        raise MissingParameterError(f"Missing required parameters: {', '.join(missing_vars)}")

    try:
        params = (country, start_date, end_date)
        query = """SELECT TO_CHAR(d_date, 'YYYY-MM-DD') AS formatted_date, d_death FROM deaths JOIN location ON 
                    l_nationkey = d_nationkey WHERE l_nationname = %s AND d_date BETWEEN %s AND %s;"""
        data = execute_query(query, params, True)
        
        if data:
            return jsonify(data)
        else:
            raise EmptyQueryOutputError(f"Query returned no rows. Query: '{query}' with parameters: {params}")
    except Exception as e:
        return jsonify({"error": str(e)}), e.status_code
    

"""
    Get testing metric by country within a window of time

    Params:
        - country: name of country (or location in general)
        - start: start date for window of time
        - end: end date for window of time
        - metric: testing metric of choice

    Returns:
        - list of tuples (date and total testing metric value)
"""
@app.route('/api/testing-by-country', methods=['GET'])
def testing_by_country():
    accepted_params = ['country', 'end', 'start', 'metric']
    accepted_metrics = ['t_cumulative_total', 't_daily_change_ct', 't_ct_per_thousand', 't_daily_change_ct_per_thousand', 
                        't_short_term_positive_rate', 't_short_term_tests_per_case']
    unknown_params = [key for key in request.args.keys() if key not in accepted_params]

    if unknown_params:
        raise UnknownParameterError(f"Unknown parameters: {', '.join(unknown_params)}")

    country = request.args.get('country')
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    metric = request.args.get('metric')
    missing_vars = find_missing_variables(country=country, start_date=start_date, end_date=end_date, metric=metric)

    if missing_vars:
        raise MissingParameterError(f"Missing required parameters: {', '.join(missing_vars)}")

    if metric not in accepted_metrics:
        raise ValueError(f"Invalid metric name: {metric}")

    try:
        params = (country, start_date, end_date)
        query = f"""SELECT TO_CHAR(t_date, 'YYYY-MM-DD') AS formatted_date, split_part(t_entity, ' - ', 2) AS metric_value, 
                    {metric} FROM testing JOIN location ON l_nationkey = t_nationkey WHERE l_nationname = %s AND t_date BETWEEN %s AND %s;"""
        data = execute_query(query, params, True)
        
        if data:
            return jsonify(data)
        else:
            raise EmptyQueryOutputError(f"Query returned no rows. Query: '{query}' with parameters: {params}")
    except Exception as e:
        return jsonify({"error": str(e)}), e.status_code


"""
    Get total hospitalizations by country within a window of time

    Params:
        - country: name of country (or location in general)
        - start: start date for window of time
        - end: end date for window of time
        - indicator: hospitalization metric
        - per_million: boolean

    Returns:
        - list of tuples (date and total hospitalizations value)
"""
@app.route('/api/hospitalizations-by-country', methods=['GET'])
def hospitalizations_by_country():
    accepted_params = ['country', 'end', 'start', 'indicator', 'per_million']
    accepted_indicators = ['Daily hospital occupancy', 'Daily ICU occupancy', 'Weekly new hospital admissions', 
                           'Weekly new ICU admissions']
    unknown_params = [key for key in request.args.keys() if key not in accepted_params]

    if unknown_params:
        raise UnknownParameterError(f"Unknown parameters: {', '.join(unknown_params)}")

    country = request.args.get('country')
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    indicator = request.args.get('indicator')
    per_million = request.args.get('per_million')
    missing_vars = find_missing_variables(country=country, start_date=start_date, end_date=end_date)

    if missing_vars:
        raise MissingParameterError(f"Missing required parameters: {', '.join(missing_vars)}")
    
    if indicator not in accepted_indicators:
        raise ValueError(f"Invalid indicator name: {indicator}")
    
    if per_million.lower() not in ['true', 'false']:
        raise ValueError("per_million must be a boolean value")
    
    full_indicator = indicator
    if per_million.lower() == 'true':
        full_indicator += " per million"
    
    try:
        params = (country, full_indicator, start_date, end_date)
        query = """SELECT TO_CHAR(h_date, 'YYYY-MM-DD') AS formatted_date, h_indicator, h_value FROM hospitalizations 
                    WHERE h_nationname = %s AND h_indicator = %s AND h_date BETWEEN %s AND %s;"""
        data = execute_query(query, params, True)
        
        if data:
            return jsonify(data)
        else:
            raise EmptyQueryOutputError(f"Query returned no rows. Query: '{query}' with parameters: {params}")
    except Exception as e:
        return jsonify({"error": str(e)}), e.status_code


if __name__ == "__main__":
    app.run()