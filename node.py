import Pyro4
import os
import multicast
import sys
import threading
import json
import struct
import socket
import time
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

path = os.path.dirname(os.path.abspath(__file__))
files_path = path + '/files'

file_manager = None


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

		self.files_map = [
			{
				'name': 'relatorio_2017.pdf',
				'from': 'Matheus',
				'date': '17/12/2017'
			},
			{
				'name': 'lista_confra.pdf',
				'from': 'Juliana',
				'date': '02/12/2017'
			},
			{
				'name': 'projetos_2018.pptx',
				'from': 'Michelle',
				'date': '10/12/2017'
			},
			{
				'name': 'financeiro_12_2017.xlsx',
				'from': 'Marcos',
				'date': '15/12/2017'
			}
		]

	def list_files(self):
		return self.files_map

	def search(self, file_name):
		response = []

		for file in self.files_map:
			if file['name'] == file_name:
				response.append(file)

		if len(response) == 0:
			response = self.send_multicast(json.dumps({
				'action': 'search',
				'name': file_name
			}))

		return response

	def start_server(self):
		Pyro4.Daemon.serveSimple({ RemoteFileManager: "remote.filemanager" },
			ns=True, host='192.168.15.9')

	def send_multicast(self, message):
		self.sock.sendto(message.encode(), self.multicast_group)

		while True:
			try:
				response, server = self.sock.recvfrom(1024)
			except socket.timeout:
				print('timed out')
				break
			else:
				return response
		

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
	