import os

from fastapi import HTTPException, UploadFile

from app.core.supabase import supabase_client
from app.repositories.qr_repository import QRRepository

BUCKET_NAME = "qrcodes"


class QRService:
    def __init__(self, repo: QRRepository) -> None:
        self.repo = repo

    async def upload_qr(self, auth_id: str, file: UploadFile):
        allowed_types = ["image/jpeg", "image/png"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are allowed.")

        contents = await file.read()
        if len(contents) > 1 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 1MB.")

        user = self.repo.get_user_by_auth_id(auth_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        file_extension = os.path.splitext(file.filename)[1].lower() if file.filename else ".png"
        if not file_extension:
            file_extension = ".png"

        storage_path = f"{user.id}/qrcode{file_extension}"

        try:
            supabase_client.storage.from_(BUCKET_NAME).upload(
                path=storage_path,
                file=contents,
                file_options={"contentType": file.content_type},
            )
            public_url = supabase_client.storage.from_(BUCKET_NAME).get_public_url(storage_path)
            user.qr_code = public_url
            self.repo.save(user)
            return {
                "success": True,
                "message": "QR code uploaded successfully",
                "qr_code_url": public_url,
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to upload QR code: {str(exc)}")

    async def get_qr(self, auth_id: str):
        user = self.repo.get_user_by_auth_id(auth_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.qr_code:
            raise HTTPException(status_code=404, detail="No QR code found for this user")
        return {"qr_code_url": user.qr_code}

    async def delete_qr(self, auth_id: str):
        user = self.repo.get_user_by_auth_id(auth_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.qr_code:
            raise HTTPException(status_code=404, detail="No QR code found for this user")

        try:
            url_parts = user.qr_code.split(f"{BUCKET_NAME}/")
            if len(url_parts) > 1:
                storage_path = url_parts[1]
                supabase_client.storage.from_(BUCKET_NAME).remove([storage_path])

            user.qr_code = None
            self.repo.save(user)
            return {"success": True, "message": "QR code deleted successfully"}
        except Exception as exc:
            user.qr_code = None
            self.repo.save(user)
            return {
                "success": False,
                "message": f"Failed to delete from storage, but database updated: {str(exc)}",
            }
