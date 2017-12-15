import Pyro4
import os
import multicast
import sys
import threading
import json
import time

path = os.path.dirname(os.path.abspath(__file__))
files_path = path + '/files'

sender = None

def start_server():
	Pyro4.Daemon.serveSimple({ FileManager: "server.filemanager" },
		ns=True, host='192.168.15.9')

def start_multicast_listener(server):
	receiver = multicast.Receiver(server)
	receiver_thread = threading.Thread(target=receiver.start)
	receiver_thread.start()

def seek_supernode():
	message = {
		'action': 'seek_supernode'
	}
	sender.send(json.dumps(message).encode())


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
	pyro_thread = threading.Thread(target=start_server)
	pyro_thread.start()

	multicast_receiver_thread = threading.Thread(target=multicast.run_receiver)
	multicast_receiver_thread.start()

	time.sleep(5)

	sender = multicast.Sender()
	seek_supernode()