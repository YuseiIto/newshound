# Alembic related imports
from alembic import command
from alembic.config import Config
from config import Config as AppConfig

def run_migrations(c: AppConfig):
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option(
        "sqlalchemy.url", f"sqlite:///{c.database_file}"
    )  # Inject database URL
    try:
        command.upgrade(alembic_cfg, "head")  # Keep the database up-to-date
    except Exception as e:
        print(f"Migration Error: {e}")
