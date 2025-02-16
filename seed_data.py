from sqlalchemy.orm import sessionmaker
from database import engine, Employee

Session = sessionmaker(bind=engine)
db = Session()

sample_data = [
    {"name": "Ada Lovelace", "title": "CEO", "manager_id": None},
    {"name": "Alan Turing", "title": "CTO", "manager_id": 1},
    {"name": "Katherine Johnson", "title": "CFO", "manager_id": 1},
    {"name": "Tim Berners-Lee", "title": "Senior Developer", "manager_id": 2},
    {"name": "Grace Hopper", "title": "Accounting Lead", "manager_id": 3}
]