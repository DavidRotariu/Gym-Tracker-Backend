import os
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
import uuid

from app.api.routers.splits import get_current_user
from app.db.database import session_scope
from app.db.models.users import User
from app.core.supabase import supabase_client

qrcode_router = APIRouter(tags=["QR Codes"])

BUCKET_NAME = "qrcodes"  # The name of your Supabase storage bucket


@qrcode_router.post("/users/upload-qr")
async def upload_qrcode(
        file: UploadFile = File(...),
        current_user=Depends(get_current_user)
):
    """
    Upload a QR code image to Supabase Storage.

    Args:
        file: The QR code image file to upload
        current_user: The authenticated user

    Returns:
        The URL of the uploaded QR code
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG and PNG are allowed."
        )

    # Read file contents
    contents = await file.read()

    # Size validation (limit to 1MB)
    if len(contents) > 1 * 1024 * 1024:  # 1MB
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 1MB."
        )

    # Get user from database
    with session_scope() as session:
        db_user = session.query(User).filter_by(auth_id=str(current_user.id)).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create a folder structure: {user_id}/qrcode.{extension}
        file_extension = os.path.splitext(file.filename)[1].lower()
        if not file_extension:
            file_extension = ".png"  # Default extension if none is provided

        storage_path = f"{db_user.id}/qrcode{file_extension}"

        try:
            # Upload file to Supabase Storage
            supabase_client.storage.from_(BUCKET_NAME).upload(
                path=storage_path,
                file=contents,
                file_options={"contentType": file.content_type},
                # {"upsert": True}  # Overwrite if exists
            )

            # Get public URL of the uploaded file
            public_url = supabase_client.storage.from_(BUCKET_NAME).get_public_url(storage_path)

            # Update user record with QR code URL
            db_user.qr_code = public_url
            session.commit()

            return {
                "success": True,
                "message": "QR code uploaded successfully",
                "qr_code_url": public_url
            }

        except Exception as e:
            # Log the error details
            import traceback
            traceback.print_exc()

            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload QR code: {str(e)}"
            )


@qrcode_router.get("/users/get-qr")
def get_qrcode(current_user=Depends(get_current_user)):
    """
    Get the URL of the user's QR code.

    Args:
        current_user: The authenticated user

    Returns:
        The URL of the QR code
    """
    with session_scope() as session:
        db_user = session.query(User).filter_by(auth_id=str(current_user.id)).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        if not db_user.qr_code:
            raise HTTPException(status_code=404, detail="No QR code found for this user")

        return {
            "qr_code_url": db_user.qr_code
        }


@qrcode_router.delete("/users/delete-qr")
def delete_qrcode(current_user=Depends(get_current_user)):
    """
    Delete the user's QR code.

    Args:
        current_user: The authenticated user

    Returns:
        Success message
    """
    with session_scope() as session:
        db_user = session.query(User).filter_by(auth_id=str(current_user.id)).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        if not db_user.qr_code:
            raise HTTPException(status_code=404, detail="No QR code found for this user")

        try:
            # Extract storage path from URL
            # The URL format is typically: https://{project}.supabase.co/storage/v1/object/public/{bucket}/{path}
            url_parts = db_user.qr_code.split(f"{BUCKET_NAME}/")
            if len(url_parts) > 1:
                storage_path = url_parts[1]

                # Delete file from Supabase storage
                supabase_client.storage.from_(BUCKET_NAME).remove([storage_path])

            # Remove QR code reference from user record
            db_user.qr_code = None
            session.commit()

            return {
                "success": True,
                "message": "QR code deleted successfully"
            }

        except Exception as e:
            # If storage deletion fails, still update the database
            db_user.qr_code = None
            session.commit()

            import traceback
            traceback.print_exc()

            return {
                "success": False,
                "message": f"Failed to delete from storage, but database updated: {str(e)}"
            }
