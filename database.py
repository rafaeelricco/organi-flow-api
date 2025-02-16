from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    title = Column(String(50))
    manager_id = Column(Integer, ForeignKey('employees.id'))
    
    subordinates = relationship(
        "Employee", 
        backref="manager",
        remote_side=[id],
        lazy='joined'
    )

engine = create_engine('sqlite:///orgchart.db', echo=False)
Base.metadata.create_all(bind=engine)
