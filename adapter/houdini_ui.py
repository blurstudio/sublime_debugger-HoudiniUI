
from Debugger.modules.typecheck import *

# This import moves around based on the Debugger version being used
try:
	import Debugger.modules.debugger.adapter as adapter
except:
	import Debugger.modules.adapters.adapter as adapter

from os.path import abspath, join, dirname, expanduser, exists
from shutil import copy, which
import socket
import os

from .util import debugpy_path, ATTACH_TEMPLATE, log as custom_log

import sublime

adapter_type = 'HoudiniUI'


class HoudiniUI(adapter.AdapterConfiguration):

	@property
	def type(self): return adapter_type

	async def start(self, log, configuration):

		# Start by finding the python installation on the system
		python = configuration.get("pythonPath")

		if not python:
			if which("python3"):
				python = "python3"
			elif not (python := which("python")):
				raise Exception('No python installation found')
		
		custom_log(f"Found python install: {python}")
		
		# Get host/port from config
		host = configuration['debugpy']['host']
		if host == 'localhost':
			host = '127.0.0.1'
		port = int(configuration['debugpy']['port'])
		
		# Format the attach code with the config information
		attach_code = ATTACH_TEMPLATE.format(
			debugpy_path=debugpy_path,
			hostname=host,
			port=port,
			interpreter="python",
			log_dir=abspath(join(dirname(__file__), 'python', 'logs')),
		)

		# Create a socket and connect to server in Houdini
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client.connect(("localhost", 8887))

		# Send the code directly to the server and close the socket
		client.send(attach_code.encode("UTF-8"))
		client.close()

		custom_log(f"Sent attach code:\n\n {attach_code}")

		custom_log(f"Connecting to {host}:{str(port)}")
		
		return adapter.SocketTransport(log, host, port)

	@property
	def installed_version(self) -> Optional[str]:
		# The version is only used for display in the UI
		return '0.0.1'

	@property
	def configuration_snippets(self) -> Optional[list]:
		# You can have several configurations here depending on your adapter's offered functionalities,
		# but they all need a "label", "description", and "body"
		return [
			{
				"label": "Houdini: Custom UI Debugging",
				"description": "Debug Custom UI Components/Functions in Houdini",
				"body": {
					"name": "Houdini: Custom UI Debugging",
					"type": adapter_type,
					"request": "attach",  # can only be attach or launch
					"pythonPath": "",
					"debugpy":  # The host/port used to communicate with debugpy in Houdini
					{
						"host": "localhost",
						"port": 7005
					},
				}
			},
		]

	@property
	def configuration_schema(self) -> Optional[dict]:
		return None

	async def configuration_resolve(self, configuration):
		return configuration

	async def install(self, log): 
		package_path = abspath(join(dirname(__file__), '..'))
		adapter_path = join(package_path, "adapter")

		# Add debugpy injector to pythonrc file if not present
		# TODO: Support various OS's, not just Windows
		doc_path = join(expanduser("~"), "Documents")
		p27l_path = None

		# Find (or create) the python2.7libs directory
		for name in os.listdir(doc_path):
			if name.startswith('houdini'):
				if 'houdini.env' in os.listdir(join(doc_path, name)):
					p27l_path = join(doc_path, name, 'python2.7libs')
					
					if not exists(p27l_path):
						os.mkdir(p27l_path)
					
					break
		
		if p27l_path:

			src_srv = join(adapter_path, 'resources', 'ui_debug_server.py')

			dst_srv = join(p27l_path, "ui_debug_server.py")
			rc_file = join(p27l_path, "pythonrc.py")

			if not exists(dst_srv):
				copy(src_srv, dst_srv)

			if not exists(rc_file):
				with open(rc_file, 'w') as f:
					f.write('import ui_debug_server')
			else:
				with open(rc_file, 'r+') as f:
					contents = f.read()
					if "import ui_debug_server" not in contents:
						f.write("\nimport ui_debug_server")

		else:
			raise Exception("A Houdini folder could not be found in the Documents folder. Aborting install.")
