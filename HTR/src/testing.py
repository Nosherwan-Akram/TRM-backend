import subprocess
from flask import Flask, jsonify, request
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

class HTR(Resource):
	def post(self):
		process = subprocess.Popen('python3 main.py', stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
		ret1 = process.communicate()[0]
		process.wait()
		print("done")


api.add_resource(HTR,'/htr')


if __name__ == "__main__":
	app.run(debug=True)