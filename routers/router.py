# class AppRouter:
#     def db_for_read(self, model, **hints):
#         if model._meta.app_label == 'NITRaipur':
#             return 'college1'
#         elif model._meta.app_label == 'BITRaipur':
#             return 'college2'
#         return 'default'
#
#     def db_for_write(self, model, **hints):
#         if model._meta.app_label == 'NITRaipur':
#             return 'college1'
#         elif model._meta.app_label == 'BITRaipur':
#             return 'college2'
#         return 'default'
#
#     def allow_relation(self, obj1, obj2, **hints):
#         if obj1._meta.app_label in ['NITRaipur', 'BITRaipur'] and obj2._meta.app_label in ['NITRaipur', 'BITRaipur']:
#             return True
#         if obj1._meta.app_label == obj2._meta.app_label:
#             return True
#         return None
#
#     def allow_migrate(self, db, app_label, model_name=None, **hints):
#         if app_label == 'NITRaipur':
#             return db == 'college1'
#         elif app_label == 'BITRaipur':
#             return db == 'college2'
#         return db == 'default'

# CollegeProject/db_routers.py

class CollegeRouter:
    """
    A router to control all database operations on models in the
    BITRaipur and NITRaipur applications.
    """

    def db_for_read(self, model, **hints):
        # print("--------------------------------", self, model, hints)
        """
        Direct read operations for models.
        """
        if model._meta.app_label == 'BITRaipur':
            return 'college1'
        elif model._meta.app_label == 'NITRaipur':
            return 'college2'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Direct write operations for models.
        """
        if model._meta.app_label == 'BITRaipur':
            return 'college1'
        elif model._meta.app_label == 'NITRaipur':
            return 'college2'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the BITRaipur or NITRaipur apps is involved.
        """
        if obj1._meta.app_label == 'BITRaipur' or obj2._meta.app_label == 'BITRaipur':
            return True
        if obj1._meta.app_label == 'NITRaipur' or obj2._meta.app_label == 'NITRaipur':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure that the BITRaipur and NITRaipur apps only appear in their respective databases.
        All other apps (including Django's own tables) appear in the 'default' database.
        """
        if app_label == 'BITRaipur':
            return db == 'college_db'
        elif app_label == 'NITRaipur':
            return db == 'college2'
        else:
            return db == 'default'

