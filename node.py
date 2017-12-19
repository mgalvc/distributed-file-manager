import Pyro4
import os
import sys
import threading
import json
import struct
import socket
import time
import ast
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

path = os.path.dirname(os.path.abspath(__file__))
files_path = path + '/files'
downloads_path = path + '/downloads'

my_address = '192.168.15.9'

file_manager = None
multicast_group = ('224.3.29.71', 10000)

def run_multicast():
	reactor.listenMulticast(10000, MulticastListener(), listenMultiple=True)
	reactor.run(installSignalHandlers=False)


class FileManager(object):
	def __init__(self):
		file_manager = self

		print('running ' + str(file_manager))

		pyro_thread = threading.Thread(target=self.start_server)
		pyro_thread.start()
		
		self.multicast_group = ('224.3.29.71', 10000)

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.settimeout(5)

		ttl = struct.pack('b', 3)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

		# reactor.listenMulticast(10000, MulticastListener(), listenMultiple=True)
		multicast_thread = threading.Thread(target=self.listen_multicast)
		multicast_thread.start()

		self.files_map = set()

		# self.init_map()

	def init_map(self):
		files = os.listdir(files_path)
		for file in files:
			user, date, filename = file.split('(-)')
			self.files_map.append({
				"name": filename,
				"from": user,
				"date": date,
				"path": files_path
			})

	def get(self, name, user, date):
		with open('{}/{}(-){}(-){}'.format(files_path, user, date, name)) as f:
			return f.read()

	def list_files(self):
		request = {
				'action': 'get_files_list'
		}

		response = self.send_multicast(json.dumps(request))
		
		if response:
			files = ast.literal_eval(response)
			self.files_map.update(files)

		print(self.files_map)
		return self.files_map

	def search(self, file_name):
		response = []

		for file in self.files_map:
			if file['name'] == file_name:
				response.append(file)

		return response

	def update_map(self, file_name, user, date):
		self.files_map.append({
			"name": file_name,
			"from": user,
			"date": date,
			"path": files_path
		})

	def start_server(self):
		Pyro4.Daemon.serveSimple({ RemoteFileManager: "remote.filemanager" },
			ns=True, host='192.168.15.9')

	def send_multicast(self, message):
		self.sock.sendto(message.encode(), self.multicast_group)

		while True:
			try:
				response, server = self.sock.recvfrom(1024)
				print('{} said {}'.format(server, response))
			except socket.timeout:
				print('timed out')
				break
			else:
				return response.decode()

	def listen_multicast(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(multicast_group)

		group = socket.inet_aton(multicast_group[0])
		mreq = struct.pack('4sL', group, socket.INADDR_ANY)
		sock.setsockopt(
		    socket.IPPROTO_IP,
		    socket.IP_ADD_MEMBERSHIP,
		    mreq)

		print('listening...')
		while True:
			data, address = sock.recvfrom(1024)
			data = json.loads(data.decode())

			if address[0] == my_address:
				continue

			if data.get('action') == 'search':
				response = self.search(data.get('name'))

			if data.get('action') == 'get_files_list':
				response = self.files_map

			sock.sendto(json.dumps(response).encode(), address)
	

class MulticastListener(DatagramProtocol):
	def startProtocol(self):
		self.transport.setTTL(3)
		self.transport.joinGroup(multicast_group[0])

	def datagramReceiver(self, datagram, address):
		print(datagram)
		self.transport.write(b'ack', address)

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class RemoteFileManager(object):
	def list_files(self):
		return os.listdir(files_path)

	def save_file(self, file_name):
		open(files_path + '/' + file_name, 'w')
		print("appended {} to files".format(file_name))

	def remove_file(self, file_name):
		os.remove(files_path + '/' + file_name)
		print("remove {} from files".format(file_name))
	