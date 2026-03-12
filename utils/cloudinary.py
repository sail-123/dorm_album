import cloudinary
import cloudinary.uploader
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def _get_secret(key: str) -> str | None:
    """Streamlit Secrets → 環境変数の順で値を返す。"""
    try:
        val = st.secrets.get(key)
        if val:
            return str(val)
    except Exception:
        pass
    return os.getenv(key)


def _init():
    cloudinary.config(
        cloud_name=_get_secret("CLOUDINARY_CLOUD_NAME"),
        api_key=_get_secret("CLOUDINARY_API_KEY"),
        api_secret=_get_secret("CLOUDINARY_API_SECRET"),
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


def upload_member_photo(file) -> str:
    _init()
    result = cloudinary.uploader.upload(
        file,
        folder="dorm_album/members",
        resource_type="image",
        transformation=[
            {"width": 400, "height": 400, "crop": "fill", "gravity": "face"},
            {"quality": "auto:good"},
        ],
    )
    return result["secure_url"]


def delete_member_photo(photo_url: str) -> None:
    """CloudinaryからメンバーのURLで指定した顔写真を削除する。"""
    import re
    _init()
    # URL から public_id を抽出
    # 例: https://res.cloudinary.com/xxx/image/upload/v123/dorm_album/members/abc.jpg
    match = re.search(r'/upload/(?:v\d+/)?(.+?)(?:\.\w+)?$', photo_url)
    if match:
        public_id = match.group(1)
        cloudinary.uploader.destroy(public_id)
