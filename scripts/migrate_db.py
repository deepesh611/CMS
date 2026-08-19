"""One-button data migration from the current SQLite database to another
SQLAlchemy-supported backend (PostgreSQL, MySQL, or SQL Server).

Usage:
    python scripts/migrate_db.py "postgresql://user:pass@host:5432/cms"
    python scripts/migrate_db.py "mysql+pymysql://user:pass@host/cms"
    python scripts/migrate_db.py "mssql+pyodbc://user:pass@host/cms?driver=ODBC+Driver+17+for+SQL+Server"

The target schema is created from the SQLAlchemy models, then every table's
rows are copied over in dependency order. The source is read-only.
"""
import sys

from sqlalchemy import create_engine, insert

# Ensure the app package is importable when run as a script
sys.path.insert(0, ".")

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
import app.models  # noqa: F401,E402  (import all models/tables)


def migrate(target_url):
    app = create_app()
    with app.app_context():
        source_engine = db.engine
        target_engine = create_engine(target_url)

        print(f"Source: {source_engine.url}")
        print(f"Target: {target_engine.url}")

        # Create schema on the target
        db.metadata.create_all(target_engine)
        print("Target schema created.")

        # Copy tables in dependency (create) order
        with source_engine.connect() as src, target_engine.begin() as dst:
            for table in db.metadata.sorted_tables:
                rows = [dict(r._mapping) for r in src.execute(table.select())]
                if rows:
                    dst.execute(insert(table), rows)
                print(f"  {table.name}: {len(rows)} rows")

        print("Migration complete.")
        print("Update DATABASE_URL in your .env to point at the new database.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    migrate(sys.argv[1])
