"""Backward-compatibility Adapter for EduMate Database.

Re-exports all operations from the separate, dedicated `database` package.
All core database code now lives in `c:/Projects/EduMate/database/`.
"""

from database import (
    get_db,
    get_client,
    check_mongo_health,
    init_db,
    reset_db_to_baseline,
    seed_tg_ssc_mongodb,
    seed_database_if_empty,
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
    mongo_vector_store,
    MongoVectorStore,
)

# Export legacy seed alias for any existing scripts
seed_tg_ssc_data = seed_tg_ssc_mongodb
