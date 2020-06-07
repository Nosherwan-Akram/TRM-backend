
import json
import os
import subprocess
import pandas as pd
import numpy as np
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_pymongo import PyMongo
import jwt

from werkzeug.utils import secure_filename

from flask_cors import CORS
import pymongo


UPLOAD_FOLDER = './HTR'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

JWT_SECRET = 'JDFKLDSJFKDSJFMFLI})(RKD'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
mongoDB = mongoClient["TableDigitizer"]

CORS(app)
api = Api(app)


def checkAuthHeader(request):
    try:
        encoded_jwt = request.headers.get('Authorization').split(' ')[1]
        payload = jwt.decode(
            encoded_jwt, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        print("Verification ID")
        print(user_id)
        return user_id

    except Exception:
        return -1


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = mongoDB['users'].find_one({"username": username})

    if user is not None:
        print("user found")
        if (password == user['password']):
            # create JWT and return
            print("creating token")
            token = jwt.encode(
                {'user_id': json.dumps(user['_id'], default=str)}, JWT_SECRET, algorithm='HS256').decode('utf-8')
            print("token", token)
            return jsonify({"access_token": token})
        else:
            return "Incorrect password", 403

    else:
        return "User does not exist", 404


@app.route('/signup', methods=['POST'])
def signup():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')

    user = mongoDB['users'].find_one({"username": username})

    if user is not None:
        return "User already exists", 409

    else:
        # create user
        user = mongoDB['users'].insert_one(
            {'username': username, 'password': password, 'email': email})
        token = jwt.encode(
            {'user_id': json.dumps(user.inserted_id, default=str)}, JWT_SECRET, algorithm='HS256').decode('utf-8')
        print("token", token)
        return jsonify({"access_token": token})


@app.route('/verify', methods=['GET'])
def verify_token():
    user_id = checkAuthHeader(request)
    if user_id == -1:
        return "Unauthorized", 403
    return "Success", 200


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class upload_file(Resource):
    def post(self):
        if 'Image' not in request.files:
            return jsonify({"status": "404"})
        file = request.files['Image']
        if file.filename == '':
            return jsonify({"status": "301"})
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify({"status": "200"})


class TR(Resource):
    def post(self):
        process = subprocess.Popen('python3 ./HTR/src/main.py', shell=True)
        ret = process.communicate()[0]
        process.wait()

        process2 = subprocess.Popen('python3 ./piping.py', shell=True)
        ret2 = process2.communicate([0])
        process2.wait()
        df = pd.read_excel('output.xlsx', header=None)
        print(json.dumps(json.loads(df.to_json(orient='values'))))

        return jsonify(json.dumps(json.loads(df.to_json(orient='values'))))


class TR_RESULTS(Resource):
    def get(self):
        df = pd.read_excel('output.xlsx')
        print(json.dumps(json.loads(df.to_json(orient='values'))))

        return jsonify(json.dumps(json.loads(df.to_json(orient='values'))))
#stdout=subprocess.PIPE, stderr=subprocess.STDOUT,


api.add_resource(upload_file, '/uploads')
api.add_resource(TR, '/tr')
api.add_resource(TR_RESULTS, '/tr_results')
# api.add_resource(Login, '/login')
# api.add_resource(Signup, '/signup')
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
