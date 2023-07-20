import json
import os.path
import shlex
import subprocess
from enum import Enum

from setup_tools.os import is_windows

extension_states = os.path.join('data', 'extensions.json')
ext_folder = os.path.join('extensions')


def git_ready():
    cmd = 'git -v'
    cmd = cmd if is_windows() else shlex.split(cmd)
    result = subprocess.run(cmd).returncode
    return result == 0


class UpdateStatus(Enum):
    no_git = -1
    unmanaged = 0
    updated = 1
    outdated = 2


class Extension:
    def __init__(self, ext_name, load_states):
        self.enabled = (ext_name not in load_states.keys()) or load_states[ext_name]
        self.extname = ext_name
        self.path = os.path.join(ext_folder, ext_name)
        self.main_file = os.path.join(self.path, 'main.py')
        self.req_file = os.path.join(self.path, 'requirements.py')  # Optional
        self.style_file = os.path.join(self.path, 'style.py')
        self.js_file = os.path.join(self.path, 'scripts', 'script.js')
        self.git_dir = os.path.join(self.path, '.git')
        extinfo = os.path.join(self.path, 'extension.json')
        if os.path.isfile(extinfo):
            with open(extinfo, 'r', encoding='utf8') as info_file:
                self.info = json.load(info_file)
        else:
            raise FileNotFoundError(f'No extension.json file for {ext_name} extension.')

    def activate(self):
        if self.enabled and os.path.isfile(self.main_file):
            pass

    def get_style_rules(self):
        if self.enabled and os.path.isfile(self.style_file):
            __import__(self.style_file.replace(os.path.sep, '.'))

    def get_requirements(self):
        if self.enabled and os.path.isfile(self.req_file):
            return __import__(self.req_file.replace(os.path.sep, '.')).requirements()
        return []

    def get_javascript(self) -> str | bool:
        if self.enabled and os.path.isfile(self.js_file):
            return self.js_file
        return False

    def set_enabled(self, new):
        self.enabled = new
        set_load_states()

    def check_updates(self) -> UpdateStatus:
        if not os.path.isdir(self.git_dir):
            return UpdateStatus.unmanaged
        return UpdateStatus.updated  # No check yet, TODO: add check


def get_valid_extensions():
    return [e for e in os.listdir(ext_folder)
            if os.path.isdir(os.path.join(ext_folder, e))
            and os.path.isfile(os.path.join(ext_folder, e, 'extension.json'))]


states: dict[str, Extension] = {}


def set_load_states():
    s = {k: v.enabled for k, v in zip(states.keys(), states.values())}
    json.dump(s, open(extension_states, 'w', encoding='utf8'))


def get_load_states():
    return json.load(open(extension_states, 'r', encoding='utf8'))


def init_extensions():
    s = get_load_states()
    for ext in get_valid_extensions():
        states[ext] = Extension(ext, s)
