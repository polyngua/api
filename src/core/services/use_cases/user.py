from src.core.entities.user import User, UserRepository
from src.core.services.data_transfer_objects.user import UserOut, UserCreate


class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.repo = user_repository

    def execute(self, user: UserCreate) -> UserOut:
        user = self.repo.create(user.email, user.first_name, user.surname, user.password)

        return UserOut(**user.as_dict())
