from django.contrib.auth.models import User


def create_username(name, request=None, profile=False):
    name = ''.join(e for e in name if e.isalnum())
    name = name[:29]
    base_name = name
    ctr = 1

    while True:
        if not User.objects.filter(username=name).exists() and not User.objects.filter(username=name).exists():
            break
        else:
            name = base_name + (str(ctr))
            ctr += 1

    # return the new name
    return name
