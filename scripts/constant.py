import os.path

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DOWNLOAD_DIR = os.path.join(ROOT_DIR, "tmp")

CONFIG_DIR = os.path.join(ROOT_DIR, "config")
COMMON_CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, "config_common.plist")
DEBUG_CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, "config_debug.plist")

THIRD_PART_DIR = os.path.join(ROOT_DIR, "third_part")
