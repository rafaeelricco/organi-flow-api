from typing import Optional, List
from pydantic import BaseModel
import json
from pathlib import Path

class Employee(BaseModel):
    id: int
    name: str
    title: str
    manager_id: Optional[int] = None
    position: Optional[int] = None
    subordinates: List['Employee'] = []

# Initial data to be used when creating the file
INITIAL_DATA = [
    {
        "id": 3,
        "name": "David Wilson",
        "title": "Product Director",
        "manager_id": 1
    },
    {
        "id": 2,
        "name": "Sarah Johnson",
        "title": "CTO",
        "manager_id": 1
    },
    {
        "id": 5,
        "name": "Michael Chen",
        "title": "Engineering Manager",
        "manager_id": 2
    },
    {
        "id": 8,
        "name": "James Taylor",
        "title": "Frontend Lead",
        "manager_id": 5
    },
    {
        "id": 15,
        "name": "Emily Davis",
        "title": "Senior Developer",
        "manager_id": 8
    },
    {
        "id": 9,
        "name": "Maria Garcia",
        "title": "Backend Lead",
        "manager_id": 5
    },
    {
        "id": 10,
        "name": "Thomas Wright",
        "title": "UX Designer",
        "manager_id": 9
    },
    {
        "id": 1,
        "name": "John Smith",
        "title": "CEO",
        "manager_id": None
    },
    {
        "id": 6,
        "name": "Peter Anderson",
        "title": "Product Manager",
        "manager_id": 3
    },
    {
        "id": 11,
        "name": "Amanda White",
        "title": "Senior UX Designer",
        "manager_id": 6
    },
    {
        "id": 14,
        "name": "Robert Johnson",
        "title": "Junior UX Designer",
        "manager_id": 11
    }
]

def load_employees():
    try:
        with open('employees.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Employee.model_validate(emp) for emp in data]
    except FileNotFoundError:
        # Create the file with initial data if it doesn't exist
        employees = [Employee.model_validate(emp) for emp in INITIAL_DATA]
        save_employees(employees)
        return employees

def save_employees(employees: List[Employee]):
    with open('employees.json', 'w', encoding='utf-8') as f:
        json.dump([emp.model_dump() for emp in employees], f, ensure_ascii=False, indent=4)
