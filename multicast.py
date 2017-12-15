import socket
import struct
import sys
import json
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

multicast_group = ('224.3.29.71', 10000)
is_supernode = False


class Sender(object):
	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.settimeout(5)

		ttl = struct.pack('b', 3)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

	def send(self, message):
		print('sending...')
		self.sock.sendto(message, multicast_group)

		print('waiting...')
		while True:
			try:
				response, server = self.sock.recvfrom(1024)
			except socket.timeout:
				return 'eita barril, n tem ngm'
			else:
				print('sender received {} from {}'.format(response, server))
				return response


class Receiver(DatagramProtocol):
	def startProtocol(self):
		self.transport.setTTL(2)
		self.transport.joinGroup(multicast_group[0])

		print('waiting for messages...')

	def datagramReceived(self, datagram, address):
		
		print('receiver received {} from {}'.format(datagram, address))
		self.transport.write(b'ack', address)

def run_receiver():
	reactor.listenMulticast(multicast_group[1], Receiver(), listenMultiple=True)
	reactor.run(installSignalHandlers=False)
