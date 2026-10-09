from getpass import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from inventario.models import PerfilUsuario


class Command(BaseCommand):
    help = "Crea usuarios para los roles administrador, almacenista y cajero."

    usuarios_roles = (
        ("admin", PerfilUsuario.Rol.ADMIN, "Administrador"),
        ("almacenista", PerfilUsuario.Rol.ALMACENISTA, "Almacenista"),
        ("cajero", PerfilUsuario.Rol.CAJERO, "Cajero"),
    )

    def handle(self, *_args, **_options):
        User = get_user_model()

        for username, rol, nombre_grupo in self.usuarios_roles:
            grupo, _ = Group.objects.get_or_create(name=nombre_grupo)
            usuario, creado = User.objects.get_or_create(
                username=username,
                defaults={"is_active": True},
            )
            if creado:
                usuario.set_password(self._solicitar_password(usuario))
                usuario.save(update_fields=["password"])

            usuario.groups.set([grupo])
            PerfilUsuario.objects.update_or_create(
                usuario=usuario,
                defaults={"rol": rol},
            )
            estado = "creado" if creado else "actualizado"
            self.stdout.write(
                self.style.SUCCESS(
                    f"Usuario '{username}' {estado} con rol '{nombre_grupo}'."
                )
            )

    def _solicitar_password(self, usuario):
        while True:
            password = getpass(f"Contraseña nueva para {usuario.username}: ")
            confirmacion = getpass("Confirma la contraseña: ")
            if password != confirmacion:
                self.stderr.write(self.style.ERROR("Las contraseñas no coinciden."))
                continue
            try:
                validate_password(password, user=usuario)
            except ValidationError as error:
                self.stderr.write(self.style.ERROR(" ".join(error.messages)))
                continue
            return password
