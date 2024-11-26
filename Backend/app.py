from db.queries import *
from flask import Flask, jsonify, request
from Errors import *
from Errors.custom_exceptions import *
from Util.util import *

app = Flask(__name__)
register_error_handlers(app)


# Retrieve all country names for populating dropdown menu
"""
    Get all country names

    Params: None

    Returns:
        - List of country names
"""
@app.route('/api/get-countries', methods=['GET'])
def get_countries():
    try:
        query = 'SELECT l_nationname FROM location;'
        data = execute_query(query, fetch_results=True)

        if data:
            flattened_data = [item for sublist in data for item in sublist]
            return jsonify(flattened_data)
        else:
            raise EmptyQueryOutputError(f"Query returned no rows. Query: '{query}'")
    except Exception as e:
        return jsonify({"error": str(e)}), e.status_code


# Single country queries
"""
    Get total cases for a country within a window of time

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
    
    if not is_valid_date(start_date) or not is_valid_date(end_date):
        raise IncorrectParameterFormError("Dates must be of the form YYYY-MM-DD")

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
    Get total deaths for a country within a window of time

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
    
    if not is_valid_date(start_date) or not is_valid_date(end_date):
        raise IncorrectParameterFormError("Dates must be of the form YYYY-MM-DD")

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
    Get testing metric for a country within a window of time

    Params:
        - country: name of country (or location in general)
        - start: start date for window of time
        - end: end date for window of time
        - metric: testing metric of choice

    Returns:
        - list of tuples (date, indicator (how the country got metric values), and testing metric value)
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
    
    if not is_valid_date(start_date) or not is_valid_date(end_date):
        raise IncorrectParameterFormError("Dates must be of the form YYYY-MM-DD")

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
    Get total hospitalizations for a country within a window of time

    Params:
        - country: name of country (or location in general)
        - start: start date for window of time
        - end: end date for window of time
        - indicator: hospitalization metric
        - per_million: boolean

    Returns:
        - list of tuples (date, indicator, and hospitalizations value)
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
    missing_vars = find_missing_variables(country=country, start_date=start_date, end_date=end_date, indicator=indicator, per_million=per_million)

    if missing_vars:
        raise MissingParameterError(f"Missing required parameters: {', '.join(missing_vars)}")
    
    if indicator not in accepted_indicators:
        raise ValueError(f"Invalid indicator name: {indicator}")
    
    if per_million.lower() not in ['true', 'false']:
        raise ValueError("per_million must be a boolean value")

    if not is_valid_date(start_date) or not is_valid_date(end_date):
        raise IncorrectParameterFormError("Dates must be of the form YYYY-MM-DD")

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
    

"""
    Get vaccinations metric for a country within a window of time

    Params:
        - country: name of country (or location in general)
        - start: start date for window of time
        - end: end date for window of time
        - metric: vaccinations metric of choice

    Returns:
        - list of tuples (date and vaccinations metric value)
"""
@app.route('/api/vaccinations-by-country', methods=['GET'])
def vaccinations_by_country():
    accepted_params = ['country', 'end', 'start', 'metric']
    accepted_metrics = ['v_total_vaccinations', 'v_people_fully_vaccinated', 'v_total_boosters', 
                        'v_daily_vaccinations', 'v_people_fully_vaccinated_per_hundred', 'v_total_boosters_per_hundred']
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
    
    if not is_valid_date(start_date) or not is_valid_date(end_date):
        raise IncorrectParameterFormError("Dates must be of the form YYYY-MM-DD")

    try:
        params = (country, start_date, end_date)
        query = f"""SELECT TO_CHAR(v_date, 'YYYY-MM-DD') AS formatted_date, {metric} FROM vaccinations 
                    WHERE v_nationname = %s AND v_date BETWEEN %s AND %s;"""
        data = execute_query(query, params, True)
        
        if data:
            return jsonify(data)
        else:
            raise EmptyQueryOutputError(f"Query returned no rows. Query: '{query}' with parameters: {params}")
    except Exception as e:
        return jsonify({"error": str(e)}), e.status_code


# Multi-country queries (for comparison)
"""
    Compare total cases between 2+ countries within a window of time

    Params:
        - countries: name of countries (or location in general) REQUIRES: 2+
        - start: start date for window of time
        - end: end date for window of time

    Returns:
        - list of tuples (date, country, and total cases value)
"""
@app.route('/api/compare-cases-by-country', methods=['GET'])
def compare_cases_by_country():
    accepted_params = ['countries', 'end', 'start']
    unknown_params = [key for key in request.args.keys() if key not in accepted_params]

    if unknown_params:
        raise UnknownParameterError(f"Unknown parameters: {', '.join(unknown_params)}")
    
    countries = request.args.getlist('countries')
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    missing_vars = find_missing_variables(countries=countries, start_date=start_date, end_date=end_date)

    if missing_vars:
        raise MissingParameterError(f"Missing required parameters: {', '.join(missing_vars)}")

    if len(countries) < 2:
        raise IncorrectParameterFormError("At least 2 countries must be provided for parameter: countries")
    
    if not is_valid_date(start_date) or not is_valid_date(end_date):
        raise IncorrectParameterFormError("Dates must be of the form YYYY-MM-DD")
    
    try:
        # Dynamically create placeholders for the IN clause
        placeholders = ', '.join(['%s'] * len(countries))
        params = countries + [start_date, end_date]
        query = f"""SELECT TO_CHAR(c_date, 'YYYY-MM-DD') AS formatted_date, l_nationname, c_cases FROM cases
                    JOIN location ON l_nationkey = c_nationkey WHERE l_nationname IN ({placeholders}) AND 
                    c_date BETWEEN %s AND %s ORDER BY l_nationname, formatted_date;"""
        data = execute_query(query, params, True)

        if data:
            json_result = {}

            for row in data:
                country = row[1]
                row_cleaned = [row[0], row[2]]

                if country not in json_result:
                    json_result[country] = []
                
                json_result[country].append(row_cleaned)
            
            return jsonify(json_result)
        else:
            raise EmptyQueryOutputError(f"Query returned no rows. Query: '{query}' with parameters: {params}")
    except Exception as e:
        return jsonify({"error": str(e)}), e.status_code


"""
    Compare total deaths between 2+ countries within a window of time

    Params:
        - countries: name of countries (or location in general) REQUIRES: 2+
        - start: start date for window of time
        - end: end date for window of time

    Returns:
        - list of tuples (date, country, and total deaths value)
"""
@app.route('/api/compare-deaths-by-country', methods=['GET'])
def compare_deaths_by_country():
    accepted_params = ['countries', 'end', 'start']
    unknown_params = [key for key in request.args.keys() if key not in accepted_params]

    if unknown_params:
        raise UnknownParameterError(f"Unknown parameters: {', '.join(unknown_params)}")
    
    countries = request.args.getlist('countries')
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    missing_vars = find_missing_variables(countries=countries, start_date=start_date, end_date=end_date)

    if missing_vars:
        raise MissingParameterError(f"Missing required parameters: {', '.join(missing_vars)}")

    if len(countries) < 2:
        raise IncorrectParameterFormError("At least 2 countries must be provided for parameter: countries")
    
    if not is_valid_date(start_date) or not is_valid_date(end_date):
        raise IncorrectParameterFormError("Dates must be of the form YYYY-MM-DD")
    
    try:
        # Dynamically create placeholders for the IN clause
        placeholders = ', '.join(['%s'] * len(countries))
        params = countries + [start_date, end_date]
        query = f"""SELECT TO_CHAR(d_date, 'YYYY-MM-DD') AS formatted_date, l_nationname, d_death FROM deaths
                    JOIN location ON l_nationkey = d_nationkey WHERE l_nationname IN ({placeholders}) AND 
                    d_date BETWEEN %s AND %s ORDER BY l_nationname, formatted_date;"""
        data = execute_query(query, params, True)

        if data:
            json_result = {}

            for row in data:
                country = row[1]
                row_cleaned = [row[0], row[2]]

                if country not in json_result:
                    json_result[country] = []
                
                json_result[country].append(row_cleaned)
            
            return jsonify(json_result)
        else:
            raise EmptyQueryOutputError(f"Query returned no rows. Query: '{query}' with parameters: {params}")
    except Exception as e:
        return jsonify({"error": str(e)}), e.status_code


"""
    Compare testing metrics between 2+ countries within a window of time

    Params:
        - countries: name of countries (or location in general) REQUIRES: 2+
        - start: start date for window of time
        - end: end date for window of time
        - metric: testing metric of choice

    Returns:
        - list of tuples (date, country, indicator, and testing metric value)
"""
@app.route('/api/compare-testing-by-country', methods=['GET'])
def compare_testing_by_country():
    accepted_params = ['countries', 'end', 'start', 'metric']
    accepted_metrics = ['t_cumulative_total', 't_daily_change_ct', 't_ct_per_thousand', 't_daily_change_ct_per_thousand', 
                        't_short_term_positive_rate', 't_short_term_tests_per_case']
    unknown_params = [key for key in request.args.keys() if key not in accepted_params]

    if unknown_params:
        raise UnknownParameterError(f"Unknown parameters: {', '.join(unknown_params)}")

    countries = request.args.getlist('countries')
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    metric = request.args.get('metric')
    missing_vars = find_missing_variables(countries=countries, start_date=start_date, end_date=end_date, metric=metric)

    if missing_vars:
        raise MissingParameterError(f"Missing required parameters: {', '.join(missing_vars)}")

    if len(countries) < 2:
        raise IncorrectParameterFormError("At least 2 countries must be provided for parameter: countries")

    if metric not in accepted_metrics:
        raise ValueError(f"Invalid metric name: {metric}")
    
    if not is_valid_date(start_date) or not is_valid_date(end_date):
        raise IncorrectParameterFormError("Dates must be of the form YYYY-MM-DD")

    try:
        # Dynamically create placeholders for the IN clause
        placeholders = ', '.join(['%s'] * len(countries))
        params = countries + [start_date, end_date]
        query = f"""SELECT TO_CHAR(t_date, 'YYYY-MM-DD') AS formatted_date, l_nationname, split_part(t_entity, ' - ', 2) AS metric_value, 
                    {metric} FROM testing JOIN location ON l_nationkey = t_nationkey WHERE l_nationname IN ({placeholders}) AND t_date BETWEEN %s AND %s
                    ORDER BY l_nationname, formatted_date;"""
        data = execute_query(query, params, True)
        
        if data:
            json_result = {}

            for row in data:
                country = row[1]
                row_cleaned = [row[0], row[2], row[3]]

                if country not in json_result:
                    json_result[country] = []
                
                json_result[country].append(row_cleaned)
            
            return jsonify(json_result)
        else:
            raise EmptyQueryOutputError(f"Query returned no rows. Query: '{query}' with parameters: {params}")
    except Exception as e:
        return jsonify({"error": str(e)}), e.status_code


"""
    Compare hospitalizations between 2+ countries within a window of time

    Params:
        - countries: name of countries (or location in general) REQUIRES: 2+
        - start: start date for window of time
        - end: end date for window of time
        - indicator: hospitalization metric
        - per_million: boolean

    Returns:
        - list of tuples (date, country, indicator, and hospitalizations value)
"""     
@app.route('/api/compare-hospitalizations-by-country', methods=['GET'])
def compare_hospitalizations_by_country():
    accepted_params = ['countries', 'end', 'start', 'indicator', 'per_million']
    accepted_indicators = ['Daily hospital occupancy', 'Daily ICU occupancy', 'Weekly new hospital admissions', 
                           'Weekly new ICU admissions']
    unknown_params = [key for key in request.args.keys() if key not in accepted_params]

    if unknown_params:
        raise UnknownParameterError(f"Unknown parameters: {', '.join(unknown_params)}")

    countries = request.args.getlist('countries')
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    indicator = request.args.get('indicator')
    per_million = request.args.get('per_million')
    missing_vars = find_missing_variables(countries=countries, start_date=start_date, end_date=end_date, indicator=indicator, per_million=per_million)

    if missing_vars:
        raise MissingParameterError(f"Missing required parameters: {', '.join(missing_vars)}")

    if len(countries) < 2:
        raise IncorrectParameterFormError("At least 2 countries must be provided for parameter: countries")
    
    if indicator not in accepted_indicators:
        raise ValueError(f"Invalid indicator name: {indicator}")
    
    if per_million.lower() not in ['true', 'false']:
        raise ValueError("per_million must be a boolean value")

    if not is_valid_date(start_date) or not is_valid_date(end_date):
        raise IncorrectParameterFormError("Dates must be of the form YYYY-MM-DD")

    full_indicator = indicator
    if per_million.lower() == 'true':
        full_indicator += " per million"
    
    try:
        # Dynamically create placeholders for the IN clause
        placeholders = ', '.join(['%s'] * len(countries))
        params = countries + [full_indicator, start_date, end_date]
        query = f"""SELECT TO_CHAR(h_date, 'YYYY-MM-DD') AS formatted_date, h_nationname, h_indicator, h_value FROM hospitalizations 
                    WHERE h_nationname IN ({placeholders})  AND h_indicator = %s AND h_date BETWEEN %s AND %s ORDER BY h_nationname, formatted_date;"""
        data = execute_query(query, params, True)
        
        if data:
            json_result = {}

            for row in data:
                country = row[1]
                row_cleaned = [row[0], row[2], row[3]]

                if country not in json_result:
                    json_result[country] = []
                
                json_result[country].append(row_cleaned)
            
            return jsonify(json_result)
        else:
            raise EmptyQueryOutputError(f"Query returned no rows. Query: '{query}' with parameters: {params}")
    except Exception as e:
        return jsonify({"error": str(e)}), e.status_code


"""
    Compare vaccinations between 2+ countries within a window of time

    Params:
        - country: name of country (or location in general)
        - start: start date for window of time
        - end: end date for window of time
        - metric: vaccinations metric of choice

    Returns:
        - list of tuples (date, country, and vaccinations metric value)
"""
@app.route('/api/compare-vaccinations-by-country', methods=['GET'])
def compare_vaccinations_by_country():
    accepted_params = ['countries', 'end', 'start', 'metric']
    accepted_metrics = ['v_total_vaccinations', 'v_people_fully_vaccinated', 'v_total_boosters', 
                        'v_daily_vaccinations', 'v_people_fully_vaccinated_per_hundred', 'v_total_boosters_per_hundred']
    unknown_params = [key for key in request.args.keys() if key not in accepted_params]

    if unknown_params:
        raise UnknownParameterError(f"Unknown parameters: {', '.join(unknown_params)}")

    countries = request.args.getlist('countries')
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    metric = request.args.get('metric')
    missing_vars = find_missing_variables(countries=countries, start_date=start_date, end_date=end_date, metric=metric)

    if missing_vars:
        raise MissingParameterError(f"Missing required parameters: {', '.join(missing_vars)}")

    if len(countries) < 2:
        raise IncorrectParameterFormError("At least 2 countries must be provided for parameter: countries")

    if metric not in accepted_metrics:
        raise ValueError(f"Invalid metric name: {metric}")
    
    if not is_valid_date(start_date) or not is_valid_date(end_date):
        raise IncorrectParameterFormError("Dates must be of the form YYYY-MM-DD")

    try:
        # Dynamically create placeholders for the IN clause
        placeholders = ', '.join(['%s'] * len(countries))
        params = countries + [start_date, end_date]
        query = f"""SELECT TO_CHAR(v_date, 'YYYY-MM-DD') AS formatted_date, v_nationname, {metric} FROM vaccinations 
                    WHERE v_nationname IN ({placeholders}) AND v_date BETWEEN %s AND %s ORDER BY v_nationname, formatted_date;"""
        data = execute_query(query, params, True)
        
        if data:
            json_result = {}

            for row in data:
                country = row[1]
                row_cleaned = [row[0], row[2]]

                if country not in json_result:
                    json_result[country] = []
                
                json_result[country].append(row_cleaned)
            
            return jsonify(json_result)
        else:
            raise EmptyQueryOutputError(f"Query returned no rows. Query: '{query}' with parameters: {params}")
    except Exception as e:
        return jsonify({"error": str(e)}), e.status_code


if __name__ == "__main__":
    app.run()