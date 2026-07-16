from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models import Clinic, Doctor, License
from schemas import ClinicCreate, DoctorCreate, DoctorUpdate



def find_clinic_by_id(db: Session, clinic_id: int) -> Optional[Clinic]:
    return db.query(Clinic).filter(Clinic.id == clinic_id).first()


def find_doctor_by_id(db: Session, doctor_id: int) -> Optional[Doctor]:
    return db.query(Doctor).filter(Doctor.id == doctor_id).first()


def find_license_by_id(db: Session, license_id: int) -> Optional[License]:
    return db.query(License).filter(License.id == license_id).first()


def doctor_code_exists(db: Session, doctor_code: str) -> bool:
    return db.query(Doctor).filter(Doctor.doctor_code == doctor_code).first() is not None



def create_clinic(db: Session, clinic_data: ClinicCreate) -> Clinic:
    new_clinic = Clinic(
        clinic_name=clinic_data.clinic_name,
        specialty=clinic_data.specialty,
    )
    try:
        db.add(new_clinic)
        db.commit()
        db.refresh(new_clinic)
        return new_clinic
    except SQLAlchemyError:
        db.rollback()
        raise


def get_clinic_by_id(db: Session, clinic_id: int) -> Optional[Clinic]:
    return find_clinic_by_id(db, clinic_id)


def get_clinics_paginated(
    db: Session, page: int = 1, limit: int = 10, search: Optional[str] = None
):
    query = db.query(Clinic)

    if search:
        query = query.filter(Clinic.clinic_name.ilike(f"%{search}%"))

    total = query.count()
    offset = (page - 1) * limit
    clinics = query.offset(offset).limit(limit).all()

    return clinics, total


def create_doctor(db: Session, doctor_data: DoctorCreate) -> Doctor:
    new_doctor = Doctor(
        doctor_code=doctor_data.doctor_code,
        salary=doctor_data.salary,
        clinic_id=doctor_data.clinic_id,
    )
    try:
        db.add(new_doctor)
        db.commit()
        db.refresh(new_doctor)
        return new_doctor
    except SQLAlchemyError:
        db.rollback()
        raise


def get_doctor_by_id(db: Session, doctor_id: int) -> Optional[Doctor]:
    return find_doctor_by_id(db, doctor_id)


def get_doctors_by_clinic(db: Session, clinic_id: int):
    return db.query(Doctor).filter(Doctor.clinic_id == clinic_id).all()


def update_doctor(
    db: Session, doctor_id: int, doctor_update: DoctorUpdate
) -> Optional[Doctor]:
    doctor = find_doctor_by_id(db, doctor_id)
    if not doctor:
        return None

    update_data = doctor_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doctor, field, value)

    try:
        db.commit()
        db.refresh(doctor)
        return doctor
    except SQLAlchemyError:
        db.rollback()
        raise


def delete_license(db: Session, license_id: int) -> bool:
    license_obj = find_license_by_id(db, license_id)
    if not license_obj:
        return False

    try:
        db.delete(license_obj)
        db.commit()
        return True
    except SQLAlchemyError:
        db.rollback()
        raise
