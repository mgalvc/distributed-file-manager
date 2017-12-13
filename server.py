import Pyro4
import os

path = os.path.dirname(os.path.abspath(__file__))
files_path = path + '/files'

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class FileManager(object):
	def __init__(self):
		self.files = ['file1', 'file2']

	def list_files(self):
		return os.listdir(files_path)

	def save_file(self, file_name):
		open(files_path + '/' + file_name, 'w')
		print("appended {} to files".format(file_name))

	def remove_file(self, file_name):
		os.remove(files_path + '/' + file_name)
		print("remove {} from files".format(file_name))


if __name__ == '__main__':
	Pyro4.Daemon.serveSimple({ FileManager: "server.filemanager" },
		ns=True, host='192.168.15.9')