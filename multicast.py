import socket
import struct
import sys

multicast_group = ('224.3.29.71', 10000)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.2)

ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)


class Sender(object):
	def send(self, message):
		print('sending...')
		sock.sendto(message, multicast_group)

		print('waiting...')
		while True:
			try:
				response, server = sock.recvfrom(1024)
			except socket.timeout:
				print('timed out')
				break
			else:
				print('received {} from {}'.format(response, server))