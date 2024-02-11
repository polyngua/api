from datetime import timedelta, timezone
from jose import JWTError, jwt

from src.core.entities.user import UserRepository
from src.core.entities.token import *
from src.core.services.use_cases.user import GetUserUseCase

SECRET = "d5aa8e3b7026837c61db4a78424b5f53858f4ac52617690c9e4bf1fb79e3ec67"  # TODO: Change this to a config val
ALGORITHM = "HS256"


class AuthenticateUserAndCreateTokenUseCase:
    def __init__(self, token_repository: TokenRepository, user_repository: UserRepository):
        self.token_repository = token_repository
        self.user_repository = user_repository

    def execute(self, email: str, password: str) -> Token:
        """
        Validate the inputs for the user, and create a new token for them if the user can be authenticated.
        """
        user = GetUserUseCase(self.user_repository).execute(email, password)  # This will authenticate the user.

        # Now create the token:
        LIFESPAN_MINS = 60

        expiration = datetime.now(timezone.utc) + timedelta(minutes=LIFESPAN_MINS)
        token_data = {"sub": str(user.ID), "exp": expiration}
        token = jwt.encode(token_data, SECRET, algorithm=ALGORITHM)

        return self.token_repository.create(token, expiration, user.ID)


class ValidateTokenAndGetUserUseCase:
    def __init__(self, token_repository: TokenRepository, user_repository: UserRepository):
        self.token_repository = token_repository
        self.user_repository = user_repository

    def execute(self, token: str):
        """
        Decode the given token, perform database checks, and get the user if all is ok.
        """
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])  # We do it in this order, to avoid an unnecessary database call if we get JWTError

        token = self.token_repository.get_by_token_string(token)

        if token.has_expired():
            raise JWTError("Token has expired.")

        user_id = payload.get("sub")

        if token.ID != user_id:
            raise JWTError("Invalid. Token has been tampered with")  # This should never occur if the cryptography has
                                                                     # worked. Very big problem if this happens
                                                                     # TODO: if this has happened we need to know.

        # If we have passed all checks to make it this far, we can validate the user!
        return self.user_repository.get(user_id)






