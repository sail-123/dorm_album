import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()


def _init():
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )


def upload_image(file) -> str:
    _init()
    result = cloudinary.uploader.upload(
        file,
        folder="dorm_album",
        resource_type="image",
        transformation=[
            {"width": 1200, "crop": "limit"},
            {"quality": "auto:good"},
        ],
    )
    return result["secure_url"]
