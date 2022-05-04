import os.path
import shutil
import string
import toml
import github
from datetime import datetime
from utils import file_utils
from constant import ROOT_DIR, DOWNLOAD_PATH


class OpenCore:
    def __init__(self, config_file: string) -> None:
        self.download_folder = "tmp"
        self.config_file = config_file
        self.config = toml.load(config_file)
        pass

    def update(self):
        pass

    def check_opencore(self) -> (bool, dict):
        publish_date = self.config["OpenCore"]["publish_date"]
        owner = self.config["OpenCore"]["owner"]
        repo = self.config["OpenCore"]["repo"]

        return github.has_new_release(publish_date, owner, repo)

    def update_opencore(self, remote_publish_date, assets: dict):
        self.mkdirs()

        for asset in assets:
            download_url: str = asset["browser_download_url"]
            file_name = download_url.split("/")[-1]
            store_path = file_utils.download_file(download_url, DOWNLOAD_PATH, file_name)

            basename = os.path.basename(store_path)
            file_name = basename[:basename.rindex('.')]
            unzip_to = os.path.join(DOWNLOAD_PATH, file_name)
            if not os.path.exists(unzip_to):
                os.makedirs(unzip_to)
            file_utils.un_zip(store_path, unzip_to)

            dbg_or_release = "DEBUG" if "DEBUG" in file_name.upper() else "RELEASE"

            src = os.path.join(unzip_to, "X64/EFI/BOOT/BOOTx64.efi")
            shutil.copy(src, self.efi_boot_dir(dbg_or_release))

            src = os.path.join(unzip_to, "X64/EFI/OC/Drivers/OpenRuntime.efi")
            shutil.copy(src, self.efi_drivers_dir(dbg_or_release))

            src = os.path.join(unzip_to, "X64/EFI/OC/Tools/OpenShell.efi")
            shutil.copy(src, self.efi_tools_dir(dbg_or_release))

            src = os.path.join(unzip_to, "X64/EFI/OC/OpenCore.efi")
            shutil.copy(src, self.efi_oc_dir(dbg_or_release))

            self.config["OpenCore"]["publish_date"] = datetime.strptime(remote_publish_date,
                                                                        "%Y-%m-%dT%H:%M:%SZ")
            toml.dump(self.config, open(self.config_file, 'w', encoding="utf-8"))

    def mkdirs(self):
        for _dir in self.config["EFI_DIR"].values():
            full_dbg_dir = os.path.join(ROOT_DIR, "EFI_DEBUG", _dir)
            if not os.path.exists(full_dbg_dir):
                os.makedirs(full_dbg_dir)

            full_release_dir = os.path.join(ROOT_DIR, "EFI_RELEASE", _dir)
            if not os.path.exists(full_release_dir):
                os.makedirs(full_release_dir)

    def efi_boot_dir(self, dbg_or_release: str) -> str:
        return os.path.join(ROOT_DIR, "EFI_" + dbg_or_release.upper(), self.config["EFI_DIR"]["boot"])

    def efi_oc_dir(self, dbg_or_release: str) -> str:
        _dir = os.path.join(ROOT_DIR, "EFI_" + dbg_or_release.upper(), self.config["EFI_DIR"]["oc"])
        if not os.path.exists(_dir):
            os.makedirs(_dir)

        return _dir

    def efi_acpi_dir(self, dbg_or_release: str) -> str:
        _dir = os.path.join(ROOT_DIR, "EFI_" + dbg_or_release.upper(), self.config["EFI_DIR"]["acpi"])
        if not os.path.exists(_dir):
            os.makedirs(_dir)

        return _dir

    def efi_drivers_dir(self, dbg_or_release: str) -> str:
        _dir = os.path.join(ROOT_DIR, "EFI_" + dbg_or_release.upper(), self.config["EFI_DIR"]["drivers"])
        if not os.path.exists(_dir):
            os.makedirs(_dir)

        return _dir

    def efi_kexts_dir(self, dbg_or_release: str) -> str:
        _dir = os.path.join(ROOT_DIR, "EFI_" + dbg_or_release.upper(), self.config["EFI_DIR"]["kexts"])
        if not os.path.exists(_dir):
            os.makedirs(_dir)

        return _dir

    def efi_tools_dir(self, dbg_or_release: str) -> str:
        _dir = os.path.join(ROOT_DIR, "EFI_" + dbg_or_release.upper(), self.config["EFI_DIR"]["tools"])
        if not os.path.exists(_dir):
            os.makedirs(_dir)

        return _dir

    def check_firmware_version(self):
        pass

    def update_firmware(self):
        pass

    def check_kext_version(self):
        pass

    def update_kext(self):
        pass


def _test():
    opencore = OpenCore("packages.toml")
    opencore.update_opencore()

# _test()
