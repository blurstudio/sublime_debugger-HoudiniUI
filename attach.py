
"""

This script adds the the containing package as a valid debug adapter in the Debugger's settings

"""

from os.path import join, expanduser, exists
from shutil import copy
import sublime
import os

from .adapter.houdini_ui import HoudiniUI
from Debugger.modules.debugger.adapter.adapters import Adapters


if sublime.version() < '4000':
	raise Exception('This version of the Houdini UI adapter requires Sublime Text 4. Use the st3 branch instead.')

package_path = abspath(dirname(__file__))
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


def plugin_loaded():
    """ Show message on success or fail """

    Adapters.all.append(HoudiniUI())

    if first_setup:
        sublime.message_dialog(
            "Thanks for installing the Houdini debug adapter!\n"
            "Because this is your first time using the adapter, a one-time "
            "setup was performed. Please restart Houdini before continuing."
        )
    
    elif error:
        sublime.message_dialog(
            "There was a problem during the first-time setup of the Houdini debug adapter: \n"
            "A houdiniXX.X directory could not be found in the root of the Documents folder. "
            "Please make sure the directory exists and is set as the $HOUDINI_USER_PREF_DIR."
        )


def plugin_unloaded():
    """ This is done every unload just in case this adapter is being uninstalled """

    if exists(dst_srv):
        os.remove(dst_srv)
