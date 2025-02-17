from sqlalchemy.orm import sessionmaker
from database import engine

Session = sessionmaker(bind=engine)
db = Session()

sample_data = [
  { "id": 1, "name": "John Smith", "title": "CEO", "manager_id": None },
  { "id": 2, "name": "Sarah Johnson", "title": "CTO", "manager_id": 1 },
  { "id": 3, "name": "David Wilson", "title": "Product Director", "manager_id": 1 },
  { "id": 5, "name": "Michael Chen", "title": "Engineering Manager", "manager_id": 2 },
  { "id": 6, "name": "Peter Anderson", "title": "Product Manager", "manager_id": 3 },
  { "id": 8, "name": "James Taylor", "title": "Frontend Lead", "manager_id": 5 },
  { "id": 9, "name": "Maria Garcia", "title": "Backend Lead", "manager_id": 5 },
  { "id": 10, "name": "Thomas Wright", "title": "UX Designer", "manager_id": 9 },
  { "id": 11, "name": "Amanda White", "title": "Senior UX Designer", "manager_id": 6 },
  { "id": 14, "name": "Robert Johnson", "title": "Junior UX Designer", "manager_id": 11 },
  { "id": 15, "name": "Emily Davis", "title": "Senior Developer", "manager_id": 8 },
]