import math
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import service
from database import get_db, engine
from models import Base
from schemas import (
    ClinicCreate,
    ClinicResponse,
    ClinicDetailResponse,
    ClinicPaginatedResponse,
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Clinic Management API")


# ==================== GLOBAL EXCEPTION HANDLER (Yêu cầu bổ sung 2) ====================

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """
    Xử lý lỗi toàn cục cho các vi phạm ràng buộc CSDL
    (UNIQUE, FOREIGN KEY, NOT NULL...). Chuyển đổi thành phản hồi JSON
    với mã 400 kèm chi tiết lỗi thay vì để lộ lỗi 500 ra ngoài.
    """
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Vi phạm ràng buộc dữ liệu (trùng lặp hoặc khóa ngoại không hợp lệ).",
            "error": str(exc.orig) if exc.orig else str(exc),
        },
    )


# ==================== CLINIC ENDPOINTS ====================

@app.post("/clinics", response_model=ClinicResponse, status_code=201)
def create_clinic_endpoint(clinic_data: ClinicCreate, db: Session = Depends(get_db)):
    """Tạo mới một Clinic"""
    return service.create_clinic(db, clinic_data)


@app.get("/clinics", response_model=ClinicPaginatedResponse)
def list_clinics_endpoint(
    page: int = Query(1, ge=1, description="Số trang, mặc định 1"),
    limit: int = Query(10, ge=1, description="Số bản ghi mỗi trang, mặc định 10"),
    search: str = Query(None, description="Tìm kiếm gần đúng theo clinic_name"),
    db: Session = Depends(get_db),
):
    """Lấy danh sách Clinic có phân trang và lọc theo tên (Yêu cầu bổ sung 1)"""
    clinics, total = service.get_clinics_paginated(db, page=page, limit=limit, search=search)
    total_pages = math.ceil(total / limit) if limit > 0 else 0

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "data": clinics,
    }


@app.get("/clinics/{clinic_id}", response_model=ClinicDetailResponse)
def get_clinic_endpoint(clinic_id: int, db: Session = Depends(get_db)):
    """Lấy chi tiết Clinic kèm danh sách bác sĩ"""
    clinic = service.get_clinic_by_id(db, clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="Không tìm thấy Clinic")
    return clinic


# ==================== DOCTOR ENDPOINTS ====================

@app.post("/doctors", response_model=DoctorResponse, status_code=201)
def create_doctor_endpoint(doctor_data: DoctorCreate, db: Session = Depends(get_db)):
    """
    Tạo mới một Doctor.
    - clinic_id không tồn tại -> 400 Bad Request
    - doctor_code đã tồn tại -> 409 Conflict
    """
    clinic = service.find_clinic_by_id(db, doctor_data.clinic_id)
    if not clinic:
        raise HTTPException(status_code=400, detail="clinic_id không tồn tại")

    if service.doctor_code_exists(db, doctor_data.doctor_code):
        raise HTTPException(status_code=409, detail="doctor_code đã tồn tại")

    return service.create_doctor(db, doctor_data)


@app.get("/doctors", response_model=list[DoctorResponse])
def list_doctors_by_clinic_endpoint(
    clinic_id: int = Query(..., description="Lọc danh sách bác sĩ theo phòng khám"),
    db: Session = Depends(get_db),
):
    """Lấy danh sách bác sĩ theo phòng khám (Yêu cầu bổ sung 2)"""
    clinic = service.find_clinic_by_id(db, clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="Không tìm thấy Clinic")
    return service.get_doctors_by_clinic(db, clinic_id)


@app.get("/doctors/{doctor_id}", response_model=DoctorResponse)
def get_doctor_endpoint(doctor_id: int, db: Session = Depends(get_db)):
    """Lấy chi tiết Doctor kèm thông tin Clinic và License"""
    doctor = service.get_doctor_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy Doctor")
    return doctor


@app.patch("/doctors/{doctor_id}", response_model=DoctorResponse)
def update_doctor_endpoint(
    doctor_id: int, doctor_update: DoctorUpdate, db: Session = Depends(get_db)
):
    """Cập nhật động thông tin Doctor"""
    doctor = service.update_doctor(db, doctor_id, doctor_update)
    if not doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy Doctor")
    return doctor


# ==================== LICENSE ENDPOINTS ====================

@app.delete("/licenses/{license_id}")
def delete_license_endpoint(license_id: int, db: Session = Depends(get_db)):
    """Xóa vĩnh viễn License"""
    deleted = service.delete_license(db, license_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Không tìm thấy License")
    return {"message": "Deleted"}
