from flask import Flask, render_template, send_from_directory
import os
app = Flask(__name__)

# this part is used to find file path based on their url path
@app.route('/<path:path>')
def relation(path):
	# get the current app location
	app_root = os.path.dirname(os.path.abspath(__file__))
	# redirect path for html files
	if path.endswith('.html'):
		filename = path.rsplit('/',1)[1]
		return send_from_directory(app_root + '/templates/' + filename)

@app.route('/')
def index_page():
	return render_template("index.html")

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')