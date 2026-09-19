from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator

class UserRequest(BaseModel):
    user_name : str = Field(min_length=3)
    email : EmailStr
    password : str = Field(min_length=3)

    @field_validator("user_name","password","email")
    @classmethod
    def validate_strings(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("Field cannot contain only whitespace")
        return value

class UserResponse(BaseModel):
    user_id : int
    user_name : str 
    email : EmailStr
    role : str
 
    model_config = ConfigDict(from_attributes=True)