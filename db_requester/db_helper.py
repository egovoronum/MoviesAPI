import allure
from sqlalchemy.orm import Session
from models.db_user import UserDBModel
from models.db_movie import MovieDBModel

class DBHelper:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    @allure.step("Создать тестового пользователя")
    def create_test_user(self, user_data: dict) -> UserDBModel:
        user = UserDBModel(**user_data)
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    @allure.step("Получить пользователя по ID")
    def get_user_by_id(self, user_id: str):
        return self.db_session.query(UserDBModel).filter(UserDBModel.id == user_id).first()

    @allure.step("Получить пользователя по email")
    def get_user_by_email(self, email: str):
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).first()

    @allure.step("Проверить существование пользователя по email")
    def user_exists_by_email(self, email: str) -> bool:
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).count() > 0

    @allure.step("Удалить пользователя")
    def delete_user(self, user: UserDBModel):
        """Удаляет пользователя"""
        self.db_session.delete(user)
        self.db_session.commit()

    @allure.step("Очистить тестовые данные")
    def cleanup_test_data(self, objects_to_delete: list):
        """Очищает тестовые данные"""
        for obj in objects_to_delete:
            if obj:
                self.db_session.delete(obj)
        self.db_session.commit()

    @allure.step("Получить фильм по названию")
    def get_movie_by_name(self, name: str):
        """Получает фильм по названию"""
        return self.db_session.query(MovieDBModel).filter(MovieDBModel.name == name).first()

    @allure.step("Получить фильм по ID")         
    def get_movie_by_id(self, movie_id: str):
        return self.db_session.query(MovieDBModel).filter(MovieDBModel.id == movie_id).first()


    @allure.step("Создать тестовый фильм")
    def create_test_movie(self, movie_dict: dict):
        movie = MovieDBModel(**movie_dict)
        self.db_session.add(movie)
        self.db_session.commit()
        self.db_session.refresh(movie)
        return movie

    @allure.step("Удалить фильм")
    def delete_movie(self, movie: MovieDBModel):
        self.db_session.delete(movie)
        self.db_session.commit()
