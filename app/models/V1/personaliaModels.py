import re

from pydantic import BaseModel, validator


class BirthdayModel(BaseModel):
    name: str
    date: str


class ProfileUpdate(BaseModel):
    email_penabur: str
    nama_ayah: str
    nama_ibu: str
    no_telp_ortu: str
    alamat_lengkap: str
    nama_lengkap: str
    nama_panggilan: str
    agama: str
    anggota_gereja_id: str
    golongan_darah: str
    tinggi_badan: int
    berat_badan: int
    telp_kantor: str
    telp_pribadi: str
    no_ktp: str
    instagram: str
    twitter: str
    npwp: str
    kode_pos: str

    @validator("no_telp_ortu", "telp_kantor", "telp_pribadi")
    def validate_phone_number(cls, v):
        if not re.match(r"^\+\d{1,3}\d{8,12}$", v):
            raise ValueError(
                "Invalid phone number format. Must be like +6281234567890."
            )
        return v


class EmergencyContact(BaseModel):
    id: str
    nama_kondar: str
    telp_darurat: str
    hubungan_kondar: str

    @validator("telp_darurat")
    def validate_tel_darurat(cls, v):
        if not re.match(r"^\+\d{1,3}\d{8,12}$", v):
            raise ValueError(
                "Invalid phone number format. Must be like +6281234567890."
            )
        return v
