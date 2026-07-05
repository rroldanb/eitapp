from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"

    def ready(self):
        # No bloquear startup si la DB externa no está reachable
        pass

    def check_db_connections(self):
        from django.db import connections
        from django.db.utils import OperationalError

        #dbs = ["default", "pg_local", "ORA", "supa"] # NO BORRAR, esto me permite cambiar conexiones a otras bases de datos y gestionar respaldos
        dbs = ["ORA"]

        for db_name in dbs:
            try:
                conn = connections[db_name]
                conn.ensure_connection()
                print(f"✅ Base de datos '{db_name}' conectada correctamente.")
            except OperationalError as e:
                print(f"❌ Error al conectar con '{db_name}': {e}")


# class CommonConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'apps.common'