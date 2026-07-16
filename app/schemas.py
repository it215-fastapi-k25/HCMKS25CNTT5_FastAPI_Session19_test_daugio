from typing import List, Optional
from pydantic import BaseModel


class ClinicCreate(BaseModel):
    clinic_name: str
    specialty: str


class ClinicResponse(BaseModel):
    id: int
    clinic_name: str
    specialty: str

    model_config = {"from_attributes": True}


class LicenseResponse(BaseModel):
    id: int
    license_number: str
    issue_by: str
    doctor_id: int

    model_config = {"from_attributes": True}



class DoctorCreate(BaseModel):
    doctor_code: str
    salary: float
    clinic_id: int


class DoctorUpdate(BaseModel):
    doctor_code: Optional[str] = None
    salary: Optional[float] = None
    clinic_id: Optional[int] = None


class DoctorResponse(BaseModel):
    id: int
    doctor_code: str
    salary: float
    clinic: ClinicResponse
    license: Optional[LicenseResponse] = None

    model_config = {"from_attributes": True}



class ClinicDetailResponse(ClinicResponse):
    doctors: List[DoctorResponse] = []

    model_config = {"from_attributes": True}



class ClinicPaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    data: List[ClinicResponse]

    model_config = {"from_attributes": True}
