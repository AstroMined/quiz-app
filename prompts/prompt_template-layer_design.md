Hello, I'm presenting you with a detailed markdown file named `backend_repo_summary.md`, which acts as a comprehensive representation of a project's repository. This file is generated using a Python script that meticulously walks through the project directory, encapsulating the essence of the entire project structure, including directories, files (e.g., README.md, LICENSE), and specific file contents (with a focus on `.py`, `.js`, `.html`, `.css` files) into a structured markdown document. Here's how the content is organized:

1. **Directories** are prominently highlighted as main headers, formatted as `# Directory: path/to/directory`. This layout showcases each directory within the project with its full path, ensuring a transparent hierarchy of the project's architecture.

2. **Files**, specifically focusing on README.md files, Python scripts, and other specified file types, are listed under secondary headers within their respective directory sections, formatted as `## File: filename`. README.md files are given precedence, appearing first in each section, followed by Python scripts and other files, arranged to reflect the project's logical structure.

3. **Content** of these files is presented in code blocks right after their corresponding headers, using syntax highlighting appropriate to the file type (```markdown for README.md, ```python for Python scripts, etc.), facilitating a clear understanding of each file's purpose and content.

**Guidelines for Engaging with the Project:**

- When recommending changes or additions, please provide precise file paths. For modifications, reference the existing path as outlined in the markdown. For new file suggestions, align with the existing project structure.

- Aim to output complete scripts or file contents directly, avoiding placeholders. This method enables immediate application and simplifies integration into the project.

- Ensure thorough commenting within Python files, including detailed module and function docstrings. The first line of each Python script should be a descriptive comment in the form `# filename: path/to/file.py`, indicating the script's filename and location.

- In cases where project functionality needs clarification or specific details are unclear, please ask targeted questions to avoid assumptions and ensure accuracy.

**[Task-Specific Guidance]:**

*In this section, detailed assistance is requested for the following tasks within my project:*

**Task:** 

As my senior Python engineer, it is your duty to ensure code follows a logical design pattern and best practices and to provide working code to implement that design.
We're going to be working on ensuring our CRUD functions are designed to the architectural philosophy explained below.
Please only return 3 fully updated CRUD scripts per response to stay within your output token limit.


We are working on a FastAPI application that follows a "4 layer" architecture. The layers are:

1. **FastAPI Endpoints**: Handles HTTP requests and responses.
2. **CRUD Functions**: Acts as an intermediary between the API and the database.
3. **Pydantic Schemas**: Used for data validation, serialization, and deserialization.
4. **SQLAlchemy Models**: Directly interact with the database.

I have refactored my SQLAlchemy models and Pydantic schemas to ensure accurate data validation. Now, I need to refactor my CRUD functions to maintain a clear separation of concerns. Here are my requirements:

1. **CRUD Functions**:
    - CRUD functions should interact directly with SQLAlchemy models and the database.
    - They should receive and return standard data formats (e.g., dictionaries, lists).
    - CRUD functions should not directly interact with Pydantic schemas.
    - CRUD functions should handle all database transactions, such as session management and committing changes.
    - CRUD functions must properly establish all relationships necessary in the database.


Ensure that the CRUD functions are clean, maintainable, and follow a clear separation of concerns.

---

**Example:**

### FastAPI Endpoint (Layer 1)

```python
from fastapi import APIRouter, HTTPException
from typing import List
from .schemas import ItemCreate, ItemRead
from .crud import create_item, get_items

router = APIRouter()

@router.post("/items/", response_model=ItemRead)
async def create_new_item(item: ItemCreate):
    item_data = item.dict()
    new_item = create_item(item_data)
    return ItemRead.from_attributes(new_item)

@router.get("/items/", response_model=List[ItemRead])
async def read_items():
    items = get_items()
    return [ItemRead.from_attributes(item) for item in items]
```

### CRUD Functions (Layer 2)

```python
from .models import Item
from .database import SessionLocal

def create_item(item_data: dict):
    db = SessionLocal()
    try:
        new_item = Item(**item_data)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_items():
    db = SessionLocal()
    try:
        items = db.query(Item).all()
        return items
    finally:
        db.close()
```

### Pydantic Schemas (Layer 3)

```python
from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    description: str

class ItemRead(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True
        from_attributes = True  # Use this instead of from_orm for newer Pydantic versions
```

### SQLAlchemy Models (Layer 4)

```python
from sqlalchemy import Column, Integer, String
from .database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
```

### Key Points:

- **CRUD Functions**:
  - Focus on database operations and return raw data (e.g., dictionaries).
  - It's also highly important the CRUD functions exist to properly establish all relationships necessary in the database.
- **API Endpoints**:
  - Handle HTTP interactions, validate data using Pydantic schemas, and convert data between schemas and raw formats.
  - We are NOT focusing on making changes to the endpoints right now. We'll do that after the CRUD functions have been refactored and tested.

This design ensures that each layer has a distinct responsibility, promoting maintainability and scalability in oour FastAPI application.

Please don't make any assumptions about the design goals.
If you have any questions about the intentions of the code, please ask clarifying questions.
