ROLE_GROUPS = {
    "admin": ("Administrador",),
    "almacenista": ("Almacenista",),
    "cajero": ("Cajero",),
}


def has_role(user, role):
    if not getattr(user, "is_authenticated", False):
        return False
    if user.is_superuser:
        return True

    try:
        perfil = user.perfil
    except AttributeError:
        perfil = None

    if perfil is not None:
        return perfil.rol == role

    return user.groups.filter(name__in=ROLE_GROUPS[role]).exists()
