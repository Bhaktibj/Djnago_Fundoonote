from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six # Utilities for writing the code that runs on python 2 & 3


# PasswordResetTokenGenerator create a token that will be used for account verification \
# that will be send by email


class TokenGenerator(PasswordResetTokenGenerator): # password Generator is extended with TokenGenerator
    def _make_hash_value(self, user, timestamp):
        return (
                six.text_type(user.pk) + six.text_type(timestamp) +
                six.text_type(user.is_active)
        )


account_activation_token = TokenGenerator() # that will be send by email
