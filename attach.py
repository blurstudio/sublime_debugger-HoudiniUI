
"""

This script adds the the containing package as a valid debug adapter in the Debugger's settings

"""

from os.path import join, abspath, dirname, expanduser, exists
from Debugger.modules.debugger.debugger import Debugger
from threading import Timer
from shutil import copy
import sublime
import time
import sys
import os


adapter_type = "Houdini"  # NOTE: type name must be unique to each adapter
package_path = dirname(abspath(__file__))
adapter_path = join(package_path, "adapter")


# The version is only used for display in the GUI
version = "1.0"

# You can have several configurations here depending on your adapter's offered functionalities,
# but they all need a "label", "description", and "body"
config_snippets = [
    {
        "label": "Houdini: Custom UI Debugging",
        "description": "Debug Custom UI Components/Functions in Houdini",
        "body": {
            "name": "Houdini: Custom UI Debugging",
            "type": adapter_type,
            "program": "\${file\}",
            "request": "attach",  # can only be attach or launch
            "interpreter": sys.executable,
            "debugpy":  # The host/port used to communicate with debugpy in Houdini
            {
                "host": "localhost",
                "port": 7005
            },
        }
    },
]

# The settings used by the Debugger to run the adapter.
settings = {
    "type": adapter_type,
    "command": [sys.executable, adapter_path]
}

# Instantiate variables needed for checking thread
running = False
check_speed = 3  # number of seconds to wait between checks for adapter presence in debugger instances

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

first_setup = False
error = False

if p27l_path:

    src_srv = join(adapter_path, 'resources', 'ui_debug_server.py')

    dst_srv = join(p27l_path, "ui_debug_server.py")
    rc_file = join(p27l_path, "pythonrc.py")

    if not exists(dst_srv):
        copy(src_srv, dst_srv)
        first_setup = True

    if not exists(rc_file):
        with open(rc_file, 'w') as f:
            f.write('import ui_debug_server')
    else:
        with open(rc_file, 'r+') as f:
            contents = f.read()
            if "import ui_debug_server" not in contents:
                f.write("\nimport ui_debug_server")

else:
    error = True


def check_for_adapter():
    """
    Gets run in a thread to inject configuration snippets and version information 
    into adapter objects of type adapter_type in each debugger instance found
    """

    while running:

        for instance in Debugger.instances.values():
            adapter = getattr(instance, "adapters", {}).get(adapter_type, None)
            
            if adapter and not adapter.version:
                adapter.version = version
                adapter.snippets = config_snippets
        
        time.sleep(check_speed)


def plugin_loaded():
    """ Add adapter to debugger settings for it to be recognized """

    # Add entry to debugger settings
    debugger_settings = sublime.load_settings('debugger.sublime-settings')
    adapters_custom = debugger_settings.get('adapters_custom', {})

    adapters_custom[adapter_type] = settings

    debugger_settings.set('adapters_custom', adapters_custom)
    sublime.save_settings('debugger.sublime-settings')

    if first_setup:
        
        # Start checking thread
        global running
        running = True
        Timer(1, check_for_adapter).start()

        sublime.message_dialog(
            "Thanks for installing the Houdini debug adapter!\n"
            "Because this is your first time using the adapter, a one-time "
            "setup was performed. Please restart Houdini before continuing."
        )
    
    elif error:
        sublime.message_dialog(
            "There was a problem during the first-time setup of the Houdini debug adapter: \n"
            "A houdiniXX.X directory could not be found in the root of the Documents folder, "
            "please make sure the directory exists and is set as the $HOUDINI_USER_PREF_DIR."
        )


def plugin_unloaded():
    """ This is done every unload just in case this adapter is being uninstalled """

    # Wait for checking thread to finish
    global running
    running = False
    time.sleep(check_speed + .1)

    # Remove entry from debugger settings
    debugger_settings = sublime.load_settings('debugger.sublime-settings')
    adapters_custom = debugger_settings.get('adapters_custom', {})

    adapters_custom.pop(adapter_type, "")

    debugger_settings.set('adapters_custom', adapters_custom)
    sublime.save_settings('debugger.sublime-settings')

    if exists(dst_srv):
        os.remove(dst_srv)
