import os.path

from open_core import OpenCore

open_core = OpenCore("packages.toml")
open_core.update_apple_mce_reporter_disabler()
