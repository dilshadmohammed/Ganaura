
import jwt

SECRET_KEY = 'django-insecure-dgb9&02$ski*_+mz!@fns!3j7wtpvs_e4+p$ii-+n+xug%2_hq'

class JWTUtils:
    @staticmethod
    def fetch_user_id_ws(token):
        """Decode JWT token and return user ID"""
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return decoded_token.get("id")
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None