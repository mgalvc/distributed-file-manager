import sys
import Pyro4

filemanager = Pyro4.Proxy('PYRONAME:server.filemanager')

print(filemanager.list_files())
filemanager.save_file('other.txt')
print(filemanager.list_files())
filemanager.remove_file('file.txt')
print(filemanager.list_files())
