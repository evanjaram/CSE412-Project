from db.queries import *
from flask import Flask, jsonify, request
from Errors import *
from Errors.custom_exceptions import *
from Util.util import *

app = Flask(__name__)
register_error_handlers(app)

@app.route('/api/cases-by-country', methods=['GET'])
def test():
    country = request.args.get('country')
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    missing_vars = find_missing_variables(country=country, start_date=start_date, end_date=end_date)

    if missing_vars:
        raise MissingParameterError(f"Missing required parameters: {', '.join(missing_vars)}")

    try:
        params = (country, start_date, end_date)
        query = "SELECT TO_CHAR(c_date, 'YYYY-MM-DD') AS formatted_date, c_cases FROM cases JOIN location ON l_nationkey = c_nationkey WHERE l_nationname = %s AND c_date BETWEEN %s AND %s;"
        data = execute_query(query, params, True)
        
        if data:
            return jsonify(data)
        else:
            raise EmptyQueryOutputError(f"Query returned no rows. Query: '{query}' with parameters: {params}")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    app.run()