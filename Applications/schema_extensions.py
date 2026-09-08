"""
drf_spectacular OpenAPI extension for CookieJWTAuthentication.

Registers the custom CookieJWTAuthentication class with drf_spectacular
so it can properly document the authentication scheme in Swagger/Redoc.
"""
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class CookieJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'Applications.authentication.CookieJWTAuthentication'
    name = 'CookieJWTAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': (
                'JWT authentication via Bearer token in Authorization header '
                'or via HttpOnly `access_token` cookie.'
            ),
        }
