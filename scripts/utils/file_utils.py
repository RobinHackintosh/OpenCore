import os
import requests
import shutil
import zipfile
from tqdm.auto import tqdm


def download_file(url: str, dest_dir: str, file_name: str):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    store_path = os.path.join(dest_dir, file_name)

    with requests.get(url, stream=True) as r:
        # check header to get content length, in bytes
        total_length = int(r.headers.get("Content-Length"))

        # implement progress bar via tqdm
        with tqdm.wrapattr(r.raw, "read", total=total_length, desc="") as raw:
            # save the output to a file
            with open(store_path, 'wb') as output:
                # with open(f"{os.path.basename(r.url)}", 'wb') as output:
                shutil.copyfileobj(raw, output)
                print(f"{file_name} download complete, store at: {store_path}")
                return store_path


def un_zip(file_name: str, dest_location: str):
    if not file_name.endswith(".zip"):
        print("file extend is not zip, error occur!")
    else:
        if not os.path.exists(dest_location):
            os.makedirs(dest_location)

        zip_file = zipfile.ZipFile(file_name)
        for name in zip_file.namelist():
            zip_file.extract(name, dest_location)

        zip_file.close()


def _test():
    _url = "https://github.com/acidanthera/OpenCorePkg/releases/download/0.8.0/OpenCore-0.8.0-DEBUG.zip"
    from constant import DOWNLOAD_PATH
    store_path = download_file(_url, DOWNLOAD_PATH, _url.split("/")[-1])

    basename = os.path.basename(store_path)
    file_name = basename[:basename.rindex('.')]
    unzip_to = os.path.join(DOWNLOAD_PATH, file_name)
    if not os.path.exists(unzip_to):
        os.makedirs(unzip_to)

    un_zip(store_path, unzip_to)


# _test()
