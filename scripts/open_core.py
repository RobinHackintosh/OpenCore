import logging
import os.path
import string
import toml
import github
from typing import Tuple, Any
from datetime import datetime
from utils import file_utils
from constant import ROOT_DIR, DOWNLOAD_PATH


class OpenCore:
    def __init__(self, config_file: string) -> None:
        self.download_folder = "tmp"
        self.config_file = config_file
        self.config = toml.load(config_file)
        self.fresh_update = self.config["Basic"]["fresh_update"]
        self.mkdirs()

    def update(self):
        if self.fresh_update:
            logging.info("fresh update begin.")
        # opencore core file
        self.update_opencore()

        # firmware drivers
        self.update_firmware()

        # kexts and some other files like small config applications.
        self.update_kext()

    def check_opencore(self) -> Tuple[bool, str, dict]:
        publish_date = self.config["OpenCore"]["publish_date"]
        owner = self.config["OpenCore"]["owner"]
        repo = self.config["OpenCore"]["repo"]

        return github.has_new_release(publish_date, owner, repo)

    def update_opencore(self):
        need_update, remote_publish_date, assets = self.check_opencore()
        if self.fresh_update or need_update:
            logging.info("begin updating oc core files.")
            for asset in assets:
                download_url: str = asset["browser_download_url"]

                dbg_or_release = "DEBUG" if "DEBUG" in download_url.upper() else "RELEASE"

                src_relative = "X64/EFI/BOOT/BOOTx64.efi"
                dst = self.efi_boot_dir(dbg_or_release)
                src_dst_set = {(src_relative, dst)}

                src_relative = "X64/EFI/OC/Drivers/OpenRuntime.efi"
                dst = self.efi_drivers_dir(dbg_or_release)
                src_dst_set.add((src_relative, dst))

                src_relative = "X64/EFI/OC/Tools/OpenShell.efi"
                dst = self.efi_tools_dir(dbg_or_release)
                src_dst_set.add((src_relative, dst))

                src_relative = "X64/EFI/OC/OpenCore.efi"
                dst = self.efi_oc_dir(dbg_or_release)
                src_dst_set.add((src_relative, dst))

                self.deal_asset(download_url, src_dst_set)

            self.config["OpenCore"]["publish_date"] = datetime.strptime(remote_publish_date,
                                                                        "%Y-%m-%dT%H:%M:%SZ")
            toml.dump(self.config, open(
                self.config_file, 'w', encoding="utf-8"))
            logging.info("opencore core files update complete.")
        else:
            logging.info("oc core is up to date.")

    def mkdirs(self):
        for _dir in self.config["EFI_DIR"].values():
            full_dbg_dir = os.path.join(ROOT_DIR, "EFI_DEBUG", _dir)
            if not os.path.exists(full_dbg_dir):
                os.makedirs(full_dbg_dir)

            full_release_dir = os.path.join(ROOT_DIR, "EFI_RELEASE", _dir)
            if not os.path.exists(full_release_dir):
                os.makedirs(full_release_dir)

    def efi_boot_dir(self, dbg_or_release: str) -> str:
        _dir = os.path.join(
            ROOT_DIR, "EFI_" + dbg_or_release.upper(), self.config["EFI_DIR"]["boot"])
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        return _dir

    def efi_oc_dir(self, dbg_or_release: str) -> str:
        _dir = os.path.join(
            ROOT_DIR, "EFI_" + dbg_or_release.upper(), self.config["EFI_DIR"]["oc"])
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        return _dir

    def efi_acpi_dir(self, dbg_or_release: str) -> str:
        _dir = os.path.join(
            ROOT_DIR, "EFI_" + dbg_or_release.upper(), self.config["EFI_DIR"]["acpi"])
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        return _dir

    def efi_drivers_dir(self, dbg_or_release: str) -> str:
        _dir = os.path.join(
            ROOT_DIR, "EFI_" + dbg_or_release.upper(), self.config["EFI_DIR"]["drivers"])
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        return _dir

    def efi_kexts_dir(self, dbg_or_release: str) -> str:
        _dir = os.path.join(
            ROOT_DIR, "EFI_" + dbg_or_release.upper(), self.config["EFI_DIR"]["kexts"])
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        return _dir

    def efi_tools_dir(self, dbg_or_release: str) -> str:
        _dir = os.path.join(
            ROOT_DIR, "EFI_" + dbg_or_release.upper(), self.config["EFI_DIR"]["tools"])
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        return _dir

    @staticmethod
    def app_dir() -> str:
        _dir = os.path.join(ROOT_DIR, "Applications")
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        return _dir

    def update_firmware(self):
        for index, driver in enumerate(self.config["FirmwareDrivers"]):
            if driver["update_strategy"] == "by_file_commit_history":
                owner = driver['owner']
                repo = driver['repo']
                path = driver['path']
                has_new_commit, latest_commit_date = github.has_new_commit(
                    owner, repo, path, driver['commit_date'])
                if self.fresh_update or has_new_commit:
                    file_url = f"https://github.com/{owner}/{repo}/blob/master/{path}?raw=true"
                    file_name = path.split("/")[-1]
                    store_path = file_utils.download_file(
                        file_url, DOWNLOAD_PATH, file_name)
                    file_utils.cp(store_path, self.efi_drivers_dir("DEBUG"))
                    file_utils.cp(store_path, self.efi_drivers_dir("RELEASE"))
                    self.config["FirmwareDrivers"][index]["commit_date"] = latest_commit_date
                    toml.dump(self.config, open(
                        self.config_file, 'w', encoding="utf-8"))
                else:
                    logging.info(f"driver {driver['name']} is up to date")
            elif driver["update_strategy"] == "in_oc_release":
                logging.info(
                    f"driver {driver['name']}'s update strategy is follow the opencore core, so just leave it alone")
            else:
                logging.error(
                    f"error, invalid update strategy: {driver['update_strategy']} in driver {driver['name']}")

    def update_kext(self):
        self._update_virtual_smc()
        self._update_lilu()
        self._update_whatever_green()
        self._update_apple_alc()
        self._update_small_tree_intel82576()
        self._update_lucy_rtl8125_ethernet()
        self._update_airport_itlwm()
        self._update_intel_bluetooth_firmware()
        self._update_apple_mce_reporter_disabler()
        self._update_nvme_fix()
        self._update_restrict_events()
        self._update_smc_amd_processor()

    def _update_virtual_smc(self):
        owner = self.config["Kexts"]["VirtualSMC"]["owner"]
        repo = self.config["Kexts"]["VirtualSMC"]["repo"]
        publish_date = self.config["Kexts"]["VirtualSMC"]["publish_date"]
        file_rel_path = "Kexts/VirtualSMC.kext"
        is_updated, remote_publish_date = self._deal_normal_kexts(
            owner, repo, publish_date, file_rel_path)
        if is_updated:
            self.config["Kexts"]["VirtualSMC"]["publish_date"] = datetime.strptime(remote_publish_date,
                                                                                   "%Y-%m-%dT%H:%M:%SZ")
            toml.dump(self.config, open(
                self.config_file, 'w', encoding="utf-8"))

    def _update_lilu(self):
        owner = self.config["Kexts"]["Lilu"]["owner"]
        repo = self.config["Kexts"]["Lilu"]["repo"]
        publish_date = self.config["Kexts"]["Lilu"]["publish_date"]
        file_rel_path = "Lilu.kext"

        is_updated, remote_publish_date = self._deal_normal_kexts(
            owner, repo, publish_date, file_rel_path)
        if is_updated:
            self.config["Kexts"]["Lilu"]["publish_date"] = datetime.strptime(remote_publish_date,
                                                                             "%Y-%m-%dT%H:%M:%SZ")
            toml.dump(self.config, open(
                self.config_file, 'w', encoding="utf-8"))

    def _update_whatever_green(self):
        owner = self.config["Kexts"]["WhateverGreen"]["owner"]
        repo = self.config["Kexts"]["WhateverGreen"]["repo"]
        publish_date = self.config["Kexts"]["WhateverGreen"]["publish_date"]
        file_rel_path = "WhateverGreen.kext"

        is_updated, remote_publish_date = self._deal_normal_kexts(
            owner, repo, publish_date, file_rel_path)
        if is_updated:
            self.config["Kexts"]["WhateverGreen"]["publish_date"] = datetime.strptime(remote_publish_date,
                                                                                      "%Y-%m-%dT%H:%M:%SZ")
            toml.dump(self.config, open(
                self.config_file, 'w', encoding="utf-8"))

    def _update_apple_alc(self):
        owner = self.config["Kexts"]["AppleALC"]["owner"]
        repo = self.config["Kexts"]["AppleALC"]["repo"]
        publish_date = self.config["Kexts"]["AppleALC"]["publish_date"]
        file_rel_path = "AppleALC.kext"

        is_updated, remote_publish_date = self._deal_normal_kexts(
            owner, repo, publish_date, file_rel_path)
        if is_updated:
            self.config["Kexts"]["AppleALC"]["publish_date"] = datetime.strptime(remote_publish_date,
                                                                                 "%Y-%m-%dT%H:%M:%SZ")
            toml.dump(self.config, open(
                self.config_file, 'w', encoding="utf-8"))

    def _update_small_tree_intel82576(self):
        is_enable = self.config["Kexts"]["SmallTreeIntel82576"]["enable"]

        if is_enable:
            owner = self.config["Kexts"]["SmallTreeIntel82576"]["owner"]
            repo = self.config["Kexts"]["SmallTreeIntel82576"]["repo"]
            publish_date = self.config["Kexts"]["SmallTreeIntel82576"]["publish_date"]
            file_rel_path = "SmallTreeIntel82576.kext"

            is_updated, remote_publish_date = self._deal_normal_kexts(
                owner, repo, publish_date, file_rel_path)
            if is_updated:
                self.config["Kexts"]["SmallTreeIntel82576"]["publish_date"] = datetime.strptime(remote_publish_date,
                                                                                                "%Y-%m-%dT%H:%M:%SZ")
                toml.dump(self.config, open(
                    self.config_file, 'w', encoding="utf-8"))

    def _update_lucy_rtl8125_ethernet(self):
        owner = self.config["Kexts"]["LucyRTL8125Ethernet"]["owner"]
        repo = self.config["Kexts"]["LucyRTL8125Ethernet"]["repo"]
        publish_date = self.config["Kexts"]["LucyRTL8125Ethernet"]["publish_date"]

        need_update, remote_publish_date, assets = github.has_new_release(
            publish_date, owner, repo)

        if self.fresh_update or need_update:
            for asset in assets:
                download_url: str = asset["browser_download_url"]

                dst_dir = self.efi_kexts_dir("DEBUG")
                basename = os.path.basename(download_url)
                src_dst_set = {
                    (f"{basename[:basename.rindex('.')]}\\Debug\\LucyRTL8125Ethernet.kext", dst_dir)}

                dst_dir = self.efi_kexts_dir("RELEASE")
                src_dst_set.add(
                    (f"{basename[:basename.rindex('.')]}\\Release\\LucyRTL8125Ethernet.kext", dst_dir))

                self.deal_asset(download_url, src_dst_set)

            self.config["Kexts"]["LucyRTL8125Ethernet"]["publish_date"] = datetime.strptime(remote_publish_date,
                                                                                            "%Y-%m-%dT%H:%M:%SZ")
            toml.dump(self.config, open(
                self.config_file, 'w', encoding="utf-8"))

    def _update_airport_itlwm(self):
        owner = self.config["Kexts"]["AirportItlwm"]["owner"]
        repo = self.config["Kexts"]["AirportItlwm"]["repo"]
        publish_date = self.config["Kexts"]["AirportItlwm"]["publish_date"]

        need_update, remote_publish_date, assets = github.has_new_release(
            publish_date, owner, repo)

        if self.fresh_update or need_update:
            for asset in assets:
                if "itlwm" in asset["name"]:
                    download_url: str = asset["browser_download_url"]
                    dst_dir = self.efi_kexts_dir("DEBUG")
                    src_dst_set = {("itlwm.kext", dst_dir)}

                    dst_dir = self.efi_kexts_dir("RELEASE")
                    src_dst_set.add(("itlwm.kext", dst_dir))

                    self.deal_asset(download_url, src_dst_set)
                elif self.config["OpenCore"]["macVersion"] in asset["name"]:
                    download_url: str = asset["browser_download_url"]
                    dst_dir = self.efi_kexts_dir("DEBUG")
                    src_dst_set = {
                        (f"{self.config['OpenCore']['macVersion']}/AirportItlwm.kext", dst_dir)}

                    dst_dir = self.efi_kexts_dir("RELEASE")
                    src_dst_set.add(
                        (f"{self.config['OpenCore']['macVersion']}/AirportItlwm.kext", dst_dir))

                    self.deal_asset(download_url, src_dst_set)

            self.config["Kexts"]["AirportItlwm"]["publish_date"] = datetime.strptime(remote_publish_date,
                                                                                     "%Y-%m-%dT%H:%M:%SZ")
            toml.dump(self.config, open(
                self.config_file, 'w', encoding="utf-8"))

    def _update_intel_bluetooth_firmware(self):
        owner = self.config["Kexts"]["IntelBluetoothFirmware"]["owner"]
        repo = self.config["Kexts"]["IntelBluetoothFirmware"]["repo"]
        publish_date = self.config["Kexts"]["IntelBluetoothFirmware"]["publish_date"]
        file_rel_path = "IntelBluetoothFirmware.kext"

        self._deal_normal_kexts(owner, repo, publish_date, file_rel_path)

        owner = self.config["Kexts"]["BrcmPatchRAM"]["owner"]
        repo = self.config["Kexts"]["BrcmPatchRAM"]["repo"]
        publish_date = self.config["Kexts"]["BrcmPatchRAM"]["publish_date"]
        file_rel_path = "BlueToolFixup.kext"

        self._deal_normal_kexts(owner, repo, publish_date, file_rel_path)

    def _update_apple_mce_reporter_disabler(self):
        browser_download_url = self.config["Kexts"]["AppleMCEReporterDisabler"]["browserDownloadUrl"]
        basename = os.path.basename(browser_download_url)
        store_path = file_utils.download_file(
            browser_download_url, DOWNLOAD_PATH, basename)

        file_name = basename[:basename.rindex('.')]
        unzip_to = os.path.join(DOWNLOAD_PATH, file_name)

        if not os.path.exists(unzip_to):
            os.makedirs(unzip_to)
        file_utils.un_zip(store_path, unzip_to)

        file_utils.cp(os.path.join(
            unzip_to, "AppleMCEReporterDisabler.kext"), self.efi_kexts_dir("DEBUG"))
        file_utils.cp(os.path.join(
            unzip_to, "AppleMCEReporterDisabler.kext"), self.efi_kexts_dir("RELEASE"))
        pass

    def _update_nvme_fix(self):
        owner = self.config["Kexts"]["NVMeFix"]["owner"]
        repo = self.config["Kexts"]["NVMeFix"]["repo"]
        publish_date = self.config["Kexts"]["NVMeFix"]["publish_date"]
        file_rel_path = "NVMeFix.kext"

        self._deal_normal_kexts(owner, repo, publish_date, file_rel_path)

    def _update_restrict_events(self):
        owner = self.config["Kexts"]["RestrictEvents"]["owner"]
        repo = self.config["Kexts"]["RestrictEvents"]["repo"]
        publish_date = self.config["Kexts"]["RestrictEvents"]["publish_date"]
        file_rel_path = "RestrictEvents.kext"

        self._deal_normal_kexts(owner, repo, publish_date, file_rel_path)

    def _update_smc_amd_processor(self):
        owner = self.config["Kexts"]["SMCAMDProcessor"]["owner"]
        repo = self.config["Kexts"]["SMCAMDProcessor"]["repo"]
        publish_date = self.config["Kexts"]["SMCAMDProcessor"]["publish_date"]
        need_update, remote_publish_date, assets = github.has_new_release(
            publish_date, owner, repo)
        if self.fresh_update or need_update:
            for asset in assets:
                if "AMD.Power.Gadget.app" in asset["name"]:
                    unzip_to = self.download_and_unzip(
                        asset["browser_download_url"])
                    src = os.path.join(unzip_to, "AMD Power Gadget.app")
                    file_utils.cp(src, self.app_dir())
                elif "AMDRyzenCPUPowerManagement.kext" in asset["name"]:
                    unzip_to = self.download_and_unzip(
                        asset["browser_download_url"])
                    src = os.path.join(
                        unzip_to, "AMDRyzenCPUPowerManagement.kext")
                    file_utils.cp(src, self.efi_kexts_dir("DEBUG"))
                    file_utils.cp(src, self.efi_kexts_dir("RELEASE"))
                    pass
                elif "SMCAMDProcessor.kext" in asset["name"]:
                    unzip_to = self.download_and_unzip(
                        asset["browser_download_url"])
                    src = os.path.join(unzip_to, "SMCAMDProcessor.kext")
                    file_utils.cp(src, self.efi_kexts_dir("DEBUG"))
                    file_utils.cp(src, self.efi_kexts_dir("RELEASE"))
                    pass
                else:
                    print("Known asset in smc amd processor")

            self.config["Kexts"]["SMCAMDProcessor"]["publish_date"] = datetime.strptime(remote_publish_date,
                                                                                        "%Y-%m-%dT%H:%M:%SZ")
            toml.dump(self.config, open(
                self.config_file, 'w', encoding="utf-8"))

    def _deal_normal_kexts(self, owner, repo, publish_date, file_rel_path) -> Tuple[bool, Any]:
        need_update, remote_publish_date, assets = github.has_new_release(
            publish_date, owner, repo)

        if self.fresh_update or need_update:
            for asset in assets:
                download_url: str = asset["browser_download_url"]
                if "DEBUG" not in download_url and "RELEASE" not in download_url:
                    dst_dir = self.efi_kexts_dir("DEBUG")
                    src_dst_set = {(file_rel_path, dst_dir)}

                    dst_dir = self.efi_kexts_dir("RELEASE")
                    src_dst_set.add((file_rel_path, dst_dir))
                else:
                    dbg_or_release = "DEBUG" if "DEBUG" in download_url.upper() else "RELEASE"
                    dst_dir = self.efi_kexts_dir(dbg_or_release)
                    src_dst_set = {(file_rel_path, dst_dir)}

                self.deal_asset(download_url, src_dst_set)

            return need_update, remote_publish_date
        else:
            return False, None

    def deal_asset(self, download_url, src_dst_set):
        unzip_to = self.download_and_unzip(download_url)

        for src_dst in src_dst_set:
            src = os.path.join(unzip_to, src_dst[0])
            file_utils.cp(src, src_dst[1])

    @staticmethod
    def download_and_unzip(download_url):
        file_name = download_url.split("/")[-1]
        store_path = file_utils.download_file(
            download_url, DOWNLOAD_PATH, file_name)

        basename = os.path.basename(store_path)
        file_name = basename[:basename.rindex('.')]
        unzip_to = os.path.join(DOWNLOAD_PATH, file_name)

        if not os.path.exists(unzip_to):
            os.makedirs(unzip_to)
        file_utils.un_zip(store_path, unzip_to)
        return unzip_to
