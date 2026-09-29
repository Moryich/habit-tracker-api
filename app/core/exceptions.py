class AppException(Exception):
    status_code = 500 # default value for direct base class call

    def __init__(self, message: str) -> None:
        self.message = message # value that will be given to child classes

# Something generic cases
class SomethingAlreadyExistsException(AppException):
    status_code = 409

class SomethingNotFoundException(AppException):
    status_code = 404

class SomethingIsInvalidException(AppException):
    status_code = 400

class SomethingIsForbiddenException(AppException):
    status_code = 403

# other exception cases
class InvalidCredentialsException(AppException):
    status_code = 401
