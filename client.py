import sys
import Pyro4

filemanager = Pyro4.Proxy('PYRONAME:server.filemanager')

print(filemanager.list_files())
filemanager.save_file('added file')
print(filemanager.list_files())
filemanager.remove_file('file1')
print(filemanager.list_files())
