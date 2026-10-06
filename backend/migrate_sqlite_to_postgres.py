"""One-time copy of legacy EduMate SQLite records into PostgreSQL.

Usage: python -m backend.migrate_sqlite_to_postgres --email account@example.com
"""

import argparse
import sqlite3
from pathlib import Path

from sqlalchemy import create_engine, inspect, text

from backend.config import settings
from backend.database import init_db, IS_POSTGRES

OWNED_TABLES = (
    "study_materials",
    "quiz_sessions",
    "weak_areas",
    "strong_areas",
    "subject_progress",
    "student_goals",
    "study_plans",
    "daily_study_tasks",
    "revision_schedule",
    "voice_sessions",
)


def migrate(sqlite_path: Path, email: str) -> dict[str, int]:
    if not IS_POSTGRES:
        raise RuntimeError("Set DATABASE_URL to PostgreSQL before running this migration.")
    if not sqlite_path.is_file():
        raise FileNotFoundError(f"SQLite database not found: {sqlite_path}")

    init_db()
    source = sqlite3.connect(f"file:{sqlite_path.resolve().as_posix()}?mode=ro", uri=True)
    source.row_factory = sqlite3.Row
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    copied: dict[str, int] = {}

    try:
        with engine.begin() as destination:
            account = destination.execute(
                text(
                    """
                    SELECT p.id AS student_id
                    FROM app_users u
                    JOIN student_profile p ON p.user_id = u.id
                    WHERE lower(u.email) = lower(:email)
                    """
                ),
                {"email": email.strip()},
            ).mappings().first()
            if account is None:
                raise LookupError("Create the target account in EduMate before migrating its SQLite data.")
            student_id = account["student_id"]

            legacy_profile = source.execute(
                "SELECT * FROM student_profile WHERE id = 1;"
            ).fetchone()
            if legacy_profile:
                source_columns = set(legacy_profile.keys())
                destination_columns = {
                    column["name"] for column in inspect(engine).get_columns("student_profile")
                }
                profile_values = {
                    key: legacy_profile[key]
                    for key in source_columns & destination_columns
                    if key not in {"id", "user_id", "email"}
                }
                if profile_values:
                    assignments = ", ".join(f"{key} = :{key}" for key in profile_values)
                    destination.execute(
                        text(f"UPDATE student_profile SET {assignments} WHERE id = :student_id"),
                        {**profile_values, "student_id": student_id},
                    )

            inspector = inspect(engine)
            for table_name in OWNED_TABLES:
                source_columns = {
                    column["name"]
                    for column in source.execute(f"PRAGMA table_info({table_name});").fetchall()
                }
                destination_columns = {
                    column["name"] for column in inspector.get_columns(table_name)
                }
                columns = sorted(
                    (source_columns & destination_columns)
                    | ({"student_id"} & destination_columns)
                )
                if not columns:
                    copied[table_name] = 0
                    continue

                rows = source.execute(f"SELECT * FROM {table_name};").fetchall()
                if not rows:
                    copied[table_name] = 0
                    continue

                column_sql = ", ".join(columns)
                bind_sql = ", ".join(f":{column}" for column in columns)
                statement = text(
                    f"INSERT INTO {table_name} ({column_sql}) VALUES ({bind_sql})"
                )
                migrated_rows = []
                for row in rows:
                    values = {
                        column: row[column] if column in source_columns else None
                        for column in columns
                    }
                    if "student_id" in values:
                        values["student_id"] = student_id
                    migrated_rows.append(values)
                destination.execute(statement, migrated_rows)
                copied[table_name] = len(migrated_rows)
    finally:
        source.close()
        engine.dispose()

    return copied


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy the legacy SQLite database into PostgreSQL.")
    parser.add_argument(
        "--sqlite",
        type=Path,
        default=Path(__file__).with_name("edumate.db"),
        help="Path to the source SQLite database (default: backend/edumate.db)",
    )
    parser.add_argument("--email", required=True, help="Existing EduMate account that will own the imported data")
    args = parser.parse_args()
    counts = migrate(args.sqlite, args.email)
    print("SQLite data copied to PostgreSQL:")
    for table_name, count in counts.items():
        print(f"  {table_name}: {count} rows")


if __name__ == "__main__":
    main()
