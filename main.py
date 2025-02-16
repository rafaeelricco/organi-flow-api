from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from database import engine, Employee, Base
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from datetime import datetime, timezone

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    from sqlalchemy import select

    db = SessionLocal()
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    
        if not db.scalar(select(Employee.id)):
            from seed_data import sample_data
            unique_data = {item['id']: item for item in sample_data}.values()
            db.bulk_insert_mappings(Employee, unique_data)
            db.commit()
        yield
    finally:
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
    subordinates: list["EmployeeResponse"] = Field(default_factory=list)

    class Config:
        from_attributes = True

class ApiInfo(BaseModel):
    api: str
    version: str
    date_created: str
    database: Optional[str] = None

    class Config:
        from_attributes = True

@app.get("/employees", response_model=list[EmployeeResponse])
async def get_employees(db: Session = Depends(get_db)):
    try:
        employees = db.query(Employee).all()
        return [EmployeeResponse.model_validate(emp) for emp in employees]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-manager")
async def update_manager(req: UpdateManagerRequest, db: Session = Depends(get_db)):
    try:
        emp = db.query(Employee).get(req.employee_id)
        if not emp:
            return JSONResponse(
                status_code=404,
                content={"detail": "Employee not found", "code": 404}
            )
        
        if req.manager_id == req.employee_id:
            raise HTTPException(400, "Employee não pode ser manager de si mesmo")

        if req.manager_id is not None:
            manager_exists = db.query(Employee.id).filter_by(id=req.manager_id).first()
            if not manager_exists:
                raise HTTPException(422, "Novo manager_id não existe no sistema")

        emp.manager_id = req.manager_id
        db.commit()
        return JSONResponse(
            status_code=200,
            content={"status": "success", "code": 200, "message": "Manager updated successfully"}
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": "Update failed", "code": 500, "message": str(e)}
        )

@app.get("/", response_model=ApiInfo)
async def root():
    api_info = ApiInfo(
        api="organi-flow-api",
        version="1.0.0", 
        date_created=datetime.now(timezone.utc).strftime("%d-%m-%Y"),
        database="sqlite"
    )
    return api_info
