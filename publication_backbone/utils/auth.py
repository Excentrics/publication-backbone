import base64
from django.contrib.auth import authenticate

def basic_auth(request):
    header = "HTTP_AUTHORIZATION"

    if header in request.META:
        auth = request.META[header].split()
        if len(auth) == 2:
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).split(':')
                user = authenticate(username=uname, password=passwd)
                if user is not None and user.is_active:
                        request.user = user

    return user