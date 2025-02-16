from sqlalchemy.orm import sessionmaker
from database import engine

Session = sessionmaker(bind=engine)
db = Session()

sample_data = [
    {"id": 1, "name": "John Smith", "title": "CEO", "manager_id": None},
    {"id": 2, "name": "David Wilson", "title": "Product Director", "manager_id": 1},
    {"id": 3, "name": "Peter Anderson", "title": "Product Manager", "manager_id": 5},
    {"id": 4, "name": "Michael Chen", "title": "Engineering Director", "manager_id": 2},
    {"id": 5, "name": "Emily Davis", "title": "Senior Developer", "manager_id": 3},
    {"id": 6, "name": "Sarah Johnson", "title": "CTO", "manager_id": 1},
    {"id": 7, "name": "Lisa Brown", "title": "HR Director", "manager_id": 1},
    {"id": 8, "name": "Jessica Miller", "title": "HR Manager", "manager_id": 6},
    {"id": 9, "name": "Emily Davis", "title": "Senior Developer", "manager_id": 3},
    {"id": 10, "name": "Alex Thompson", "title": "Junior Developer", "manager_id": 4},
    {"id": 11, "name": "David Wilson", "title": "Product Director", "manager_id": 1},
    {"id": 12, "name": "James Taylor", "title": "Frontend Lead", "manager_id": 3},
    {"id": 13, "name": "Maria Garcia", "title": "Backend Lead", "manager_id": 3},
    {"id": 14, "name": "Robert Kim", "title": "DevOps Engineer", "manager_id": 8},
    {"id": 15, "name": "Amanda White", "title": "UX Designer", "manager_id": 7}
]