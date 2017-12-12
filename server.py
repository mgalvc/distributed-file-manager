import Pyro4

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class FileManager(object):
	def __init__(self):
		self.files = ['file1', 'file2']

	def list_files(self):
		return self.files

	def save_file(self, file):
		self.files.append(file)
		print("appended {} to files".format(file))

	def remove_file(self, file):
		self.files.remove(file)
		print("remove {} from files".format(file))


if __name__ == '__main__':
	Pyro4.Daemon.serveSimple({ FileManager: "server.filemanager" }, ns=True)