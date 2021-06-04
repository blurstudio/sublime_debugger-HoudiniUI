
from Debugger.modules.typecheck import *
import Debugger.modules.debugger.adapter as adapter

from os.path import abspath, join, dirname
from . import common
import shutil
import socket
import time

from .util import debugpy_path, ATTACH_TEMPLATE, log as custom_log

import sublime


class HoudiniUI(adapter.AdapterConfiguration):

	@property
	def type(self): return 'HoudiniUI'

	async def start(self, log, configuration):

		# Start by finding the python installation on the system
		python = configuration.get("pythonPath")

		if not python:
			if shutil.which("python3"):
				python = "python3"
			elif not (python := shutil.which("python")):
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

	async def install(self, log): ...

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
					"type": "HoudiniUI",
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
