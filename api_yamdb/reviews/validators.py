from django.core.exceptions import ValidationError

from api.constants import ME_URL_PATH


def validate_not_me(value):
    if value.lower() == ME_URL_PATH:
        raise ValidationError(
            'Использовать имя "me" в качестве username запрещено'
        )
