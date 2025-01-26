class SQLiteRouter:
    """
    A router to control database operations for 'dz_auth' and other apps.
    Routes all writes to SQLite for sessions, and MySQL for custom models.
    """
     
    def db_for_read(self, model, **hints):
        # Route reads for dz_auth or other apps to MySQL, sessions to SQLite
        if model._meta.app_label in ['dz_auth', 'appointments']:
            return 'default'  # MySQL for dz_auth custom models
        if model._meta.app_label == 'sessions':
            return 'sqlite'  # SQLite for session table
        return None

    def db_for_write(self, model, **hints):
        # Route writes for dz_auth or other apps to MySQL, sessions to SQLite
        if model._meta.app_label in ['dz_auth', 'appointments']:
            return 'default'  # MySQL for dz_auth custom models
        if model._meta.app_label == 'sessions':
            return 'sqlite'  # SQLite for session table
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return True  # Allow relations between models if necessary

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # If migrating 'dz_auth', use MySQL; for sessions, use SQLite
        if app_label in ['dz_auth', 'appointments']:
            return db == 'default'  # MySQL for dz_auth
        if app_label == 'sessions':
            return db == 'sqlite'  # SQLite for sessions
        return None
