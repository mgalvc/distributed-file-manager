from flask import Flask, render_template, request, redirect, url_for
import node
import os
import sys
import json
import webbrowser
import ast
from datetime import date

app = Flask(__name__)


username = sys.argv[1]
file_manager = node.FileManager(username)

@app.route('/')
def index(message=None):
	files = file_manager.list_files()
	return render_template('/index.html', files=files, message=message)

@app.route('/search', methods=['POST'])
def search():
	files = file_manager.search(request.form['file_name'])

	if len(files) == 0:
		files = file_manager.send_multicast(json.dumps({
			"action": "search",
			"name": request.form['file_name']
		}))
		files = ast.literal_eval(files)

	if files == None:
		return redirect(url_for('index', message={'fail': 'not found'}))

	return render_template('/index.html', files=files)

@app.route('/download', methods=['GET'])
def download():
	content = file_manager.get(request.args.get('name'), request.args.get('from'), request.args.get('date'))
	with open('{}/{}'.format(node.downloads_path, request.args.get('name')), 'w') as downloaded:
		downloaded.write(content)
	webbrowser.open_new_tab('{}/{}'.format(node.downloads_path, request.args.get('name')))
	# webbrowser.get(using='google-chrome').open_new_tab('{}/{}'.format(node.downloads_path, request.args.get('name')))

	return redirect(url_for('index'))

@app.route('/share', methods=['POST'])
def share():
	file = request.files['file']
	print(type(file))
	file.save(os.path.join(node.files_path, '{}(-){}(-){}'.format(username, date.today(), file.filename)))
	file_manager.update_map(file.filename, username, str(date.today()))
	return redirect(url_for('index'))

if __name__ == '__main__':
	app.run()