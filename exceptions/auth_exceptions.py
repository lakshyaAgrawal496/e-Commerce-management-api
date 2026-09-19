class UserAlreadyExistsError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class AuthenticationError(Exception):
    pass

class AuthorizationError(Exception):
    pass