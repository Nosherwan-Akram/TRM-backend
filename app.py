
import json
import os
import subprocess
import pandas as pd
import numpy as np
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_pymongo import PyMongo

from werkzeug.utils import secure_filename

from flask_cors import CORS




UPLOAD_FOLDER = './HTR'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["MONGO_DBNAME"] = "fyp"
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/fyp"
mongo = PyMongo(app)

CORS(app)
api = Api(app)


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Login(Resource):
	def post(self):
		data = request.get_json(force = True)
		user = mongo.db.user.find_one_or_404({"username":data['username']})
		if(user['password'] != data['password']):
			return jsonify({"status":"400","message":"incorrect password"})
		return jsonify({"status":"200","message":user["username"]})
class Signup(Resource):
	def post(self):
		data = request.get_json(force=True)
		user = mongo.db.user.find_one({"username":data["username"]})
		if(user == None):
			mongo.db.get_collection('user').insert_one(request.json).inserted_id
			return jsonify({"status":"200","message":"signup successful"})
		return jsonify({"status":"400","message":"username not available"})
			

class upload_file(Resource):
	def post(self):
		if 'Image' not in request.files:
			return jsonify({"status":"404"})
		file = request.files['Image']
		if file.filename == '':
			return jsonify({"status":"301"})
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return jsonify({"status":"200"})

class TR(Resource):
	def post(self):
		process = subprocess.Popen('python3 ./HTR/src/main.py',shell=True)
		ret = process.communicate()[0]
		process.wait()

		process2 = subprocess.Popen('python3 ./piping.py', shell=True)
		ret2 = process2.communicate([0])
		process2.wait()
		df = pd.read_excel('output.xlsx',header=None)
		print(json.dumps(json.loads(df.to_json(orient='values'))))

		return jsonify(json.dumps(json.loads(df.to_json(orient='values'))))

class TR_RESULTS(Resource):
	def get(self):
		df = pd.read_excel('output.xlsx')
		print(json.dumps(json.loads(df.to_json(orient='values'))))

		return jsonify(json.dumps(json.loads(df.to_json(orient='values'))))
#stdout=subprocess.PIPE, stderr=subprocess.STDOUT,

api.add_resource(upload_file,'/uploads')
api.add_resource(TR,'/tr')
api.add_resource(TR_RESULTS,'/tr_results')
api.add_resource(Login,'/login')
api.add_resource(Signup,'/signup')
if __name__ == "__main__":
	app.run(debug=True,host='0.0.0.0',port=5000)
