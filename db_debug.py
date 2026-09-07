from db_requester.db_client import get_db_session
from models.db_user import UserDBModel

# 1. Получение сессии (из db_client.py)
session = get_db_session()

# 2. Создание объекта модели (из user.py)
user = UserDBModel(email="test@test.com")

# 3. Выполнение операции через ORM
session.add(user)
session.commit()

# 4. Запрос данных
user = session.query(UserDBModel).filter(
    UserDBModel.email == "test@test.com"
).first()


def test_create_user_db(db_session)
    user_data = {
    """
    Здесь дата для создание записи в БД
    То что мы шлем по апи - не подойдет
    """
    }
    user = UserDBModel(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)