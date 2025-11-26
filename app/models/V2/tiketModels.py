from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TiketingTransactionResponse(BaseModel):
    uuid: Optional[str] = None
    topic: Optional[str] = None
    laporan: Optional[str] = None
    pelaporan_date: Optional[datetime] = None
    pelapor_email: Optional[str] = None
    pelapor_unitkerja: Optional[str] = None
    pict_email: Optional[str] = None
    pic_unitkerja: Optional[str] = None
    status_ticket: Optional[str] = None
    status_date_proses: Optional[datetime] = None
    helpdesk_date_proses: Optional[datetime] = None
    helpdesk_proses: Optional[str] = None
    status_date_close: Optional[datetime] = None
    status_user_close: Optional[str] = None
    files_lampiran: Optional[str] = None
    files_pic: Optional[str] = None
    memo: Optional[str] = None

    class Config:
        from_attributes = True
