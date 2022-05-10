import logging
import os.path
from open_core import OpenCore
from constant import ROOT_DIR, CONFIG_DIR

logging.basicConfig(level=logging.INFO)

package_file_path = os.path.join(CONFIG_DIR, "packages.toml")
smbios_config_file_path = os.path.join(CONFIG_DIR, "smbios.toml")

opencore = OpenCore(package_file_path, smbios_config_file_path)
opencore.update()
