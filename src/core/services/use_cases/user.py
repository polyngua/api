from src.core.entities.user import User, UserRepository


class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.repo = user_repository

    def execute(self, user: User, password: str) -> User:
        # TODO: Check that user is uniquez
        new_user = self.repo.create(user.email, user.first_name, user.surname, password)

        return new_user
