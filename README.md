<img src="https://res.cloudinary.com/dnqiosdb6/image/upload/v1739812292/organi-flow-api-cover_sqymud.png" alt="cover">

RESTful API built with FastAPI that provides a robust backend system for managing organizational hierarchies. This API offers endpoints for querying, updating, and maintaining complex organizational structures while ensuring data integrity and preventing invalid hierarchical relationships.

Try it out: <a href="https://organi-flow-api.onrender.com" target="_blank">Live Demo</a>

## Main Features

### 1. API Information Query

**Endpoint:** GET `/`

- Returns basic API information such as name, version, and creation date

### 2. Organizational Structure View

**Endpoint:** GET `/employees`

- Returns the complete organizational structure in tree format
- Includes all employees and their hierarchical relationships

### 3. Manager Update

**Endpoint:** POST `/update-employee-manager`

- Updates an employee's manager
- Required payload:

```json
{
  "id": 1, // Employee ID
  "new_manager_id": 2 // New manager ID
}
```

- Automatic validations:
  - Prevents employee from being their own manager
  - Avoids hierarchical loops
  - Verifies existence of employee and manager

### 4. Complete Structure Update

**Endpoint:** POST `/update-manager`

- Allows updating the entire organizational structure
- Receives the complete organizational tree

## Data Structure

### Tree Node Format

```json
{
  "name": "Employee Name",
  "attributes": {
    "id": 1,
    "title": "Position",
    "manager_id": 0
  },
  "children": []
}
```

## Error Codes

| Code | Description                                  |
| ---- | -------------------------------------------- |
| 400  | Self-management attempt or hierarchical loop |
| 404  | Employee or manager not found                |
| 500  | Internal server error                        |

## How to Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the server:

```bash
uvicorn main:app --reload
```

3. Access the API at: `http://localhost:8000`
