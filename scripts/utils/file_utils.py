import logging
import os
import requests
import shutil
import zipfile
from tqdm.auto import tqdm
from constant import DOWNLOAD_DIR


def download_and_unzip(download_url):
    file_name = download_url.split("/")[-1]
    store_path = download_file(
        download_url, DOWNLOAD_DIR, file_name)

    basename = os.path.basename(store_path)
    file_name = basename[:basename.rindex('.')]
    unzip_to = os.path.join(DOWNLOAD_DIR, file_name)

    if not os.path.exists(unzip_to):
        os.makedirs(unzip_to)
    un_zip(store_path, unzip_to)
    return unzip_to


def download_file(url: str, dest_dir: str, file_name: str):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    store_path = os.path.join(dest_dir, file_name)
    logging.info(f"start downloading {file_name} to {dest_dir}")

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


def cp(src: str, dst: str):
    if os.path.isdir(src):
        # delete folder if exist in destination
        basename = os.path.basename(src)
        if os.path.exists(os.path.join(dst, basename)):
            shutil.rmtree(os.path.join(dst, basename))

        shutil.copytree(src, os.path.join(dst, basename))
    else:
        shutil.copy2(src, dst)
