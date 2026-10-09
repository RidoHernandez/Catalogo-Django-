from getpass import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea los usuarios cajero y almacenista con sus grupos de acceso."

    usuarios_roles = (
        ("cajero", "Cajero"),
        ("almacenista", "Almacenista"),
    )

    def handle(self, *_args, **_options):
        User = get_user_model()

        for username, nombre_grupo in self.usuarios_roles:
            grupo, _ = Group.objects.get_or_create(name=nombre_grupo)
            usuario, creado = User.objects.get_or_create(
                username=username,
                defaults={"is_active": True},
            )
            if creado:
                usuario.set_password(self._solicitar_password(usuario))
                usuario.save(update_fields=["password"])

            usuario.groups.set([grupo])
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
