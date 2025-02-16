from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from database import engine, Employee
from sqlalchemy.orm import sessionmaker
from typing import Optional
from contextlib import asynccontextmanager

Session = sessionmaker(bind=engine)
db = Session()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    from database import Employee
    from sqlalchemy import select
    
    if not db.scalar(select(Employee.id)):
        from seed_data import sample_data
        db.bulk_insert_mappings(Employee, sample_data)
        db.commit()
    yield
    # Shutdown code (optional)
    db.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class UpdateManagerRequest(BaseModel):
    employee_id: int
    manager_id: Optional[int] = None

class EmployeeResponse(BaseModel):
    id: int
    name: str
    title: str
    manager_id: Optional[int]
    subordinates: list = Field(default_factory=list)

    class Config:
        from_attributes = True

@app.get("/employees", response_model=list[EmployeeResponse])
async def get_hierarchy():
    try:
        # Get all employees and let SQLAlchemy handle the relationships
        employees = db.query(Employee).filter(Employee.manager_id.is_(None)).all()
        
        # Ensure subordinates is always a list
        result = []
        for emp in employees:
            emp_dict = {
                "id": emp.id,
                "name": emp.name,
                "title": emp.title,
                "manager_id": emp.manager_id,
                "subordinates": emp.subordinates or []  # Garante que seja uma lista vazia se for None
            }
            result.append(emp_dict)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-manager")
async def update_manager(req: UpdateManagerRequest):
    try:
        emp = db.query(Employee).get(req.employee_id)
        if not emp:
            raise HTTPException(404, "Employee not found")
            
        emp.manager_id = req.manager_id
        db.commit()
        return {"status": "success"}
        
    except HTTPException as he:
        raise he
    except:
        db.rollback()
        raise HTTPException(500, "Update failed")
