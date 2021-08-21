from rest_framework.exceptions import APIException


class BadRequest(APIException):
    status_code = 400
    default_detail = 'Bad request'
    default_code = 'bad_request'


class BaseEmailError(Exception):
    pass


class EmailNotValid(BaseEmailError):
    pass


class BaseUserError(Exception):
    pass


class BadVerboseRole(BaseUserError):
    pass
