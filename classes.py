from pydantic import BaseModel, Field
from typing import Optional

class TreeNode(BaseModel):
    name: str
    attributes: dict
    children: list["TreeNode"]

class ApiInfo(BaseModel):
    api: str
    version: str
    date_created: str
    database: Optional[str] = None

    class Config:
        from_attributes = True

class SwapPositionsRequest(BaseModel):
    employee1_id: int
    employee2_id: int
    new_manager1_id: Optional[int]
    new_manager2_id: Optional[int]

class EmployeeUpdateItem(BaseModel):
    id: int
    name: str
    title: str
    manager_id: Optional[int] = None

class BatchUpdateRequest(BaseModel):
    employees: list[EmployeeUpdateItem]

class EmployeeManagerUpdate(BaseModel):
    employee_id: int 
    target_id: int   