from app.schemas.users import UserCreate, UserRead
from datetime import datetime

# Simulate incoming data for UserCreate (like in POST /users)
user_create = UserCreate(email="test@example.com", password="securepass123")
print(user_create)

# Simulate returned data for UserRead (like in GET /users/{id})
user_read = UserRead(id=1, email="test@example.com", created_at=datetime.utcnow())
print(user_read)
