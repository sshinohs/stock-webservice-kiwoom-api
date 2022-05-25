from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import sqlalchemy as db

app = Flask(__name__)
app.config.from_pyfile('config.py')

engine = db.create_engine(app.config['DB_URL'], encoding='utf-8')

CORS(app, resources={r'*': {'origins': ['http://localhost:3000', 'http://127.0.0.1:3000']}})

connection = engine.connect()
metadata = db.MetaData()
table = db.Table('items', metadata, autoload=True, autoload_with=engine)

query = db.select([table])

print('query')
print(query)

result_proxy = connection.execute(query)
result_set = result_proxy.fetchall()

print('테이블 내용 (result_set[:10]')
print(result_set[:10])

query = db.select([table]).where(table.columns.name == '삼성전자')
result_proxy = connection.execute(query)
result_set = result_proxy.fetchall()

print('삼성전자 찾기')
print(result_set[:10])

query = db.select([table]).where(table.columns.name == '삼성전자')

print('삼성전자 찾기의 query')
print(query)
result_proxy = connection.execute(query)
result_set = result_proxy.fetchall()

print('삼성전자 찾기')
print(result_set[:10])

print(table.columns.keys())


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
        return order + ' zzang!'


@app.route('/echo_call/<param>')
def get_echo_call(param):
    return jsonify({"param": param})


@app.route('/echo_call', methods=['POST'])
def post_echo_call():
    param = request.get_json()
    return jsonify(param)


if __name__ == "__main__":
    app.run()
