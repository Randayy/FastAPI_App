from fastapi import APIRouter
import logging
from app.db.connect_redis import check_redis_connection
from app.db.connect_postgresql import check_connection



logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log')

router = APIRouter()

@router.get("/")
async def health_check():
    logging.info("Health check started")
    redis = await check_redis_connection()
    postgres = await check_connection()
    logging.info("Connected to Redis and PostgreSQL")
    return { 
            "status_code": 200,
            "detail": "ok",
            "result": "working",
            "redis_status": f"{redis}",
            "postgres_status": f"{postgres}"
            }

# @router.post("/user")
# async def create_user(user_data: UserCreateSchema, db = Depends(get_session)):
#     async with get_session() as session:
#         user = User(**user_data.dict())
#         session.add(user)
#         await session.commit()
#         await session.refresh(user)
#         return user

# def hash_password(password: str) -> str:
#     hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#     return hashed_password.decode('utf-8')

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# @router.post("/user")
# async def create_user(user_data: SignUpRequestSchema, db: AsyncSession = Depends(get_session)):
#     hashed_password = hash_password(user_data.password)
#     user_data_dict = user_data.dict()
#     user_data_dict['password'] = hashed_password
#     user = User(**user_data_dict)
#     db.add(user)
#     await db.commit()
#     await db.refresh(user)
#     return user

# @router.get("/users/{user_id}")
# async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_session)):
#     user = await db.execute(select(User).filter(User.id == user_id))
#     user = user.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user


# @router.get("/users/")
# async def get_users_list(db: AsyncSession = Depends(get_session)):
#     users = await db.execute(select(User))
#     users = users.scalars().all()
#     return users
    

