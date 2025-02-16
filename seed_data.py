from sqlalchemy.orm import sessionmaker
from database import engine

Session = sessionmaker(bind=engine)
db = Session()

sample_data = [
    {"id": 1, "name": "John Smith", "title": "CEO", "manager_id": None},
    {"id": 2, "name": "Sarah Johnson", "title": "CTO", "manager_id": 1},
    {"id": 3, "name": "David Wilson", "title": "Product Director", "manager_id": 1},
    {"id": 4, "name": "Lisa Brown", "title": "HR Director", "manager_id": 1},
    {"id": 5, "name": "Michael Chen", "title": "Engineering Manager", "manager_id": 2},
    {"id": 6, "name": "Peter Anderson", "title": "Product Manager", "manager_id": 3},
    {"id": 7, "name": "Rachel Torres", "title": "HR Manager", "manager_id": 4},
    {"id": 8, "name": "James Taylor", "title": "Frontend Lead", "manager_id": 5},
    {"id": 9, "name": "Maria Garcia", "title": "Backend Lead", "manager_id": 5},
    {"id": 10, "name": "Thomas Wright", "title": "UX Designer", "manager_id": 6},
    {"id": 11, "name": "Amanda White", "title": "Senior UX Designer", "manager_id": 6},
    {"id": 12, "name": "Sophie Chen", "title": "Senior HR Specialist", "manager_id": 7},
    {"id": 13, "name": "Robert Johnson", "title": "Junior UX Designer", "manager_id": 11},
    {"id": 14, "name": "Emily Davis", "title": "Senior Developer", "manager_id": 8},
    {"id": 15, "name": "Sam Smith", "title": "Senior Developer", "manager_id": 9},
    {"id": 16, "name": "Alex Thompson", "title": "Junior Developer", "manager_id": 14},
    {"id": 17, "name": "Mark Wilson", "title": "HR Analyst", "manager_id": 12},
    {"id": 18, "name": "Julia Santos", "title": "Recruitment Specialist", "manager_id": 12},
    {"id": 19, "name": "Daniel Lee", "title": "Junior Developer", "manager_id": 18},
    {"id": 20, "name": "Isabella Martinez", "title": "Senior Developer", "manager_id": 15},
    {"id": 21, "name": "Oliver Brown", "title": "Senior Developer", "manager_id": 13}
]