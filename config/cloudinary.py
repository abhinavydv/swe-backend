import dotenv

dotenv.load_dotenv()

from cloudinary import uploader
from cloudinary import CloudinaryResource


def upload_file(file_path: str, public_id=None):
    res = uploader.upload(file_path)
    return res["secure_url"]


def delete_file(file_url: str):
    public_id = file_url.split("/")[-1].split(".")[0]
    res = uploader.destroy(public_id)
    return res["result"] == "ok"
