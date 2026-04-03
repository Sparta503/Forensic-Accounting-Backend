from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str
    role: str
    first_name: str
    last_name: str
    company_name: str
    company_address: str
    company_city: str
    company_country: str
    company_phone_number: str

class UserUpdate(BaseModel):
    email: Optional[str]
    password: Optional[str]
    role: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    company_name: Optional[str]
    company_address: Optional[str]
    company_city: Optional[str]
    company_country: Optional[str]
    company_phone_number: Optional[str]

class UserOut(BaseModel):
    id: str
    email: str
    role: str
    first_name: str
    last_name: str
    company_name: str
    company_address: str
    company_city: str
    company_country: str
    company_phone_number: str

class UserInDB(UserOut):
    password: str