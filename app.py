from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import sqlalchemy as db

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['JSON_AS_ASCII'] = False

engine = db.create_engine(app.config['DB_URL'], encoding='utf-8')

CORS(app, resources={r'*': {'origins': ['http://localhost:3000', 'http://127.0.0.1:3000']}})

connection = engine.connect()
metadata = db.MetaData()
table = db.Table('items', metadata, autoload=True, autoload_with=engine)


@app.route('/hello_world')
def hello_world():
    return 'Hello, World!'


@app.route('/')
def home_page():
    return 'Home Page!'


@app.route('/items/search')
def item_search():
    order = request.args.get('keyword')
    if order:
        query = f"SELECT * FROM items WHERE name LIKE '%{order}%';"
        result_proxy = connection.execute(query)
        result_set = result_proxy.fetchall()

        result_list = []
        for result in result_set:
            result_list.append({
                'name': result.name,
                'code': result.code
            })
        return jsonify(result_list)


@app.route('/echo_call/<param>')
def get_echo_call(param):
    return jsonify({"param": param})


@app.route('/echo_call', methods=['POST'])
def post_echo_call():
    param = request.get_json()
    return jsonify(param)


if __name__ == "__main__":
    app.run()
