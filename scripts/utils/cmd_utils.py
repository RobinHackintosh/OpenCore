import os.path
import subprocess
from constant import ROOT_DIR
import pyautogui


def git_clone(url, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)

    return subprocess.run(f"git clone {url}", cwd=dst)


def run_python_file(file_path, args):
    return os.popen(f"python {file_path} {args}")