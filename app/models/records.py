from dataclasses import dataclass


@dataclass
class PropertyRecord:
    id: int | None
    name: str
    address: str
    notes: str = ""


@dataclass
class UnitRecord:
    id: int | None
    property_id: int
    unit_number: str
    bedrooms: int
    bathrooms: int
    status: str = "Vacant"


@dataclass
class TenantRecord:
    id: int | None
    full_name: str
    phone: str
    email: str
    unit_id: int | None
    rent_amount: float
    lease_start: str
    lease_end: str
    is_active: bool = True
