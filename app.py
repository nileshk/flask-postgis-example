from flask import Flask, jsonify, render_template, Response, stream_with_context, json
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

pg_host = app.config['PG_DB_HOST']
pg_port = app.config['PG_DB_PORT']
pg_name = app.config['PG_DB_NAME']
pg_username = app.config['PG_DB_USERNAME']
pg_password = app.config['PG_DB_PASSWORD']

conn = psycopg2.connect(host=pg_host, port=pg_port, database=pg_name, user=pg_username, password=pg_password)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/points_of_interest')
def points_of_interest():
    return execute_json_sql("""
        SELECT row_to_json(fc)
          FROM ( SELECT 'FeatureCollection' AS type, array_to_json(array_agg(f)) AS features
                   FROM ( SELECT 'Feature' AS type,
                                 ST_AsGeoJSON(lg.the_geom)::JSON AS geometry,
                                 row_to_json((SELECT l FROM (SELECT name) AS l)) AS properties
                          FROM points_of_interest AS lg ) AS f )  AS fc
        """)

@app.route('/points_of_interest_streamed')
def points_of_interest_streamed():
    return execute_and_return_feature_collection("""
        SELECT row_to_json(f) FROM (
            SELECT 'Feature' AS type,
                   ST_AsGeoJSON(lg.the_geom)::JSON AS geometry,
                   row_to_json((SELECT l FROM (SELECT name) AS l)) AS properties
              FROM points_of_interest AS lg
            ) AS f
    """)


def execute_json_sql(sql):
    """
    Execute a JSON-returning SQL and return HTTP response
    :type sql: SQL statement that returns a single column and row that contains JSON
    """
    cur = get_cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    return jsonify(result=rows[0][0])


def execute_and_return_feature_collection(sql):
    """
    Execute a JSON-returning SQL and return HTTP response
    :type sql: SQL statement that returns a a GeoJSON Feature
    """
    cur = get_cursor()
    cur.execute(sql)

    def generate():
        yield '{ "result": { "type": "FeatureCollection", "features": ['
        for idx, row in enumerate(cur):
            if idx > 0:
                yield ','
            yield json.dumps(row[0])
        yield ']}}'
        cur.close()

    return Response(stream_with_context(generate()), mimetype='application/json')


def get_cursor():
    return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


if __name__ == '__main__':
    app.debug = True
    # app.run(host='0.0.0.0', port=2600)
    app.run(host='0.0.0.0', port=3600)
