"""EduMate Unified MongoDB Database Package.

Consolidates all database models, connections, queries, seeding,
and vector storage into a single unified package.
"""

from database.connection import (
    get_db,
    get_client,
    check_mongo_health,
    mongo_manager,
    DEFAULT_MONGODB_URI,
    DEFAULT_DB_NAME,
)

from database.seed_data import (
    seed_tg_ssc_mongodb,
    seed_database_if_empty,
    reset_database_to_baseline,
)

from database.repository import (
    get_student_profile,
    update_student_settings,
    list_student_goals,
    insert_student_goal,
    delete_student_goal,
    toggle_student_goal,
    select_active_goal,
    list_daily_tasks,
    insert_daily_task,
    toggle_daily_task,
    list_study_materials,
    insert_study_material,
    delete_study_material,
    create_quiz_session,
    get_quiz_session,
    update_quiz_session_evaluation,
    record_weak_area,
    record_strong_area,
    list_weak_areas,
    list_strong_areas,
    list_subject_progress,
    list_revision_items,
    record_revision_completion,
    insert_study_plan,
    record_voice_session,
    list_voice_sessions,
)

from database.vector_store import (
    mongo_vector_store,
    MongoVectorStore,
)


def init_db() -> None:
    """Initialize MongoDB indexes and seed baseline TG SSC data if collection is empty."""
    seed_database_if_empty()


def reset_db_to_baseline() -> None:
    """Reset MongoDB database to authentic TG SSC baseline."""
    reset_database_to_baseline()


# Initialize on import
init_db()

__all__ = [
    "get_db",
    "get_client",
    "check_mongo_health",
    "init_db",
    "reset_db_to_baseline",
    "seed_tg_ssc_mongodb",
    "seed_database_if_empty",
    "get_student_profile",
    "update_student_settings",
    "list_student_goals",
    "insert_student_goal",
    "delete_student_goal",
    "toggle_student_goal",
    "select_active_goal",
    "list_daily_tasks",
    "insert_daily_task",
    "toggle_daily_task",
    "list_study_materials",
    "insert_study_material",
    "delete_study_material",
    "create_quiz_session",
    "get_quiz_session",
    "update_quiz_session_evaluation",
    "record_weak_area",
    "record_strong_area",
    "list_weak_areas",
    "list_strong_areas",
    "list_subject_progress",
    "list_revision_items",
    "record_revision_completion",
    "insert_study_plan",
    "record_voice_session",
    "list_voice_sessions",
    "mongo_vector_store",
    "MongoVectorStore",
]
