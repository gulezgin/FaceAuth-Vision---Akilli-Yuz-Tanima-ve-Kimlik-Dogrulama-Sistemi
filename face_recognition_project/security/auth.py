from functools import wraps
from jwt import encode, decode
from werkzeug.security import generate_password_hash, check_password_hash
import os
from .exception import UnauthorizedError, ForbiddenError


class SecurityManager:
    def __init__(self):
        self.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')

    def get_token(self):
        # Token alma mantığı eklenmeli
        pass

    def verify_token(self, token):
        try:
            return decode(token, self.secret_key, algorithms=['HS256'])
        except:
            raise UnauthorizedError()

    def require_auth(self, role='user'):
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                token = self.get_token()
                if not token:
                    raise UnauthorizedError()

                user_data = self.verify_token(token)
                if role not in user_data['roles']:
                    raise ForbiddenError()

                return f(*args, **kwargs)

            return decorated

        return decorator