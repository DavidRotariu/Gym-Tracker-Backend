import os
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.api.routers.splits import get_current_user
from app.db.database import session_scope
from app.db.models.users import User

users_router = APIRouter(tags=["Users"])

UPLOAD_FOLDER = "uploads/qrcodes"

# ✅ Ensure the uploads directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@users_router.post("/users/upload-qr")
def upload_qr_code(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    """Upload a QR code image for the authenticated user"""
    with session_scope() as session:
        db_user = session.query(User).filter_by(auth_id=str(current_user.id)).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # ✅ Generate a unique filename
        file_extension = file.filename.split(".")[-1]
        qr_filename = f"{db_user.id}.{file_extension}"

        # ✅ Save the file
        file_path = os.path.join(UPLOAD_FOLDER, qr_filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # ✅ Update the user's QR code filename
        db_user.qr_code = qr_filename
        session.commit()

        return {"message": "QR code uploaded successfully", "qr_code": qr_filename}


@users_router.get("/users/get-qr")
def get_qr_code(current_user=Depends(get_current_user)):
    """Retrieve the authenticated user's QR code"""
    with session_scope() as session:
        db_user = session.query(User).filter_by(auth_id=str(current_user.id)).first()
        if not db_user or not db_user.qr_code:
            raise HTTPException(status_code=404, detail="No QR code found")

        return {"qr_code": db_user.qr_code}
