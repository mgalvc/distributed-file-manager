from flask import Flask, render_template, request
import node

app = Flask(__name__)

file_manager = node.FileManager()

@app.route('/')
def index():
	files = file_manager.list_files()
	return render_template('/index.html', files=files)

@app.route('/search', methods=['POST'])
def search():
	files = file_manager.search(request.form['file_name'])
	return render_template('/index.html', files=files)


