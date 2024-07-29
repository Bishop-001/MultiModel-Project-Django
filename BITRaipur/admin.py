from django.apps import apps
# from django.core import call_command
from django.urls import path
from django.contrib import admin
from .models import College, Department, Student
from django.http import JsonResponse
from django.shortcuts import render
from BITRaipur.models import College as BITCollege, Department as BITDepartment, Student as BITStudent
from NITRaipur.models import College as NITCollege, Department as NITDepartment, Student as NITStudent
import subprocess
from django.db.utils import OperationalError
import json
import os
from django.contrib import admin, messages
from django.db import connections
from django.conf import settings
import uuid
from django.http import HttpResponseRedirect
# from .models import Student, College, Department
from .forms import ModelSelectionForm
from django.core.management import call_command


def create_new_database_action(modeladmin, request, queryset):
    # selected_models = ['student', 'college', 'department']
    new_db_name = f"college_db_{uuid.uuid4().hex[:8]}"
    new_db_name = f"college_db"

    # SQL command to create a new database
    create_db_command = f"CREATE DATABASE {new_db_name}"

    # Establish a connection to the MySQL server
    with connections['college1'].cursor() as cursor:
        try:
            cursor.execute(create_db_command)
            messages.success(request, f"Database '{new_db_name}' created successfully.")
        except Exception as e:
            messages.error(request, f"Error creating database '{new_db_name}': {e}")
            return

    # Update the dynamic_databases.json file
    dynamic_db_path = os.path.join(settings.BASE_DIR, 'dynamic_databases.json')
    if os.path.exists(dynamic_db_path):
        with open(dynamic_db_path) as f:
            dynamic_databases = json.load(f)
    else:
        dynamic_databases = {"databases": []}

    new_db_config = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': new_db_name,
        'USER': 'root',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '3306',
    }

    dynamic_databases["databases"].append(new_db_config)
    print("--50--", settings.DATABASES)

    with open(dynamic_db_path, 'w') as f:
        json.dump(dynamic_databases, f, indent=4)

    # Run migrations for the new database
    try:
        subprocess.check_call(['python', 'manage.py', 'migrate', '--database', new_db_name])
        messages.success(request, f"Migrations applied to '{new_db_name}' successfully.")
    except subprocess.CalledProcessError as e:
        messages.error(request, f"Error applying migrations to '{new_db_name}': {e}")

    print(new_db_config)


create_new_database_action.short_description = "Create Database"


# def create_new_database_action(modeladmin, request, queryset):
#     selected_models = ['student', 'college', 'department']
#     new_db_name = f"college_db_{uuid.uuid4().hex[:8]}"
#
#     # SQL command to create a new database
#     create_db_command = f"CREATE DATABASE {new_db_name}"
#
#     # Establish a connection to the MySQL server
#     with connections['college1'].cursor() as cursor:
#         try:
#             cursor.execute(create_db_command)
#             messages.success(request, f"Database '{new_db_name}' created successfully.")
#         except OperationalError as e:
#             messages.error(request, f"Error creating database '{new_db_name}': {e}")
#             return
#
#     # Update the dynamic_databases.json file
#     dynamic_db_path = os.path.join(settings.BASE_DIR, 'dynamic_databases.json')
#     if os.path.exists(dynamic_db_path):
#         with open(dynamic_db_path) as f:
#             dynamic_databases = json.load(f)
#     else:
#         dynamic_databases = {"databases": []}
#
#     new_db_config = {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': new_db_name,
#         'USER': 'root',
#         'PASSWORD': '1234',
#         'HOST': 'localhost',
#         'PORT': '3306',
#         'ATOMIC_REQUESTS': False,
#         'AUTOCOMMIT': True,
#         'CONN_MAX_AGE': 0,
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#         },
#         'TEST': {
#             'NAME': None,
#         },
#         'TIME_ZONE': settings.TIME_ZONE,
#         'CONN_HEALTH_CHECKS': False,
#     }
#
#     dynamic_databases["databases"].append(new_db_config)
#
#     with open(dynamic_db_path, 'w') as f:
#         json.dump(dynamic_databases, f, indent=4)
#
#     # Add new database configuration to settings dynamically
#     settings.DATABASES[new_db_name] = new_db_config
#
#     # Run migrations for the selected models and migrate data
#     try:
#         # Apply migrations
#         call_command('makemigrations', 'BITRaipur')
#         call_command('migrate', 'BITRaipur', database=new_db_name)
#
#         # Migrate data for each selected model
#         for model in selected_models:
#             app_label = 'BITRaipur'
#             model_class = apps.get_model(app_label, model.capitalize())
#
#             # Migrate data
#             objects = model_class.objects.using('college1').all()
#             for obj in objects:
#                 obj.save(using=new_db_name)
#
#         messages.success(request, f"Migrations and data migration applied to '{new_db_name}' successfully.")
#     except Exception as e:
#         messages.error(request, f"Error applying migrations to '{new_db_name}': {e}")
#
#
# create_new_database_action.short_description = "Create Database"


class RecordAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')
    actions = [create_new_database_action]

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('datasets/', self.datasets, name='datasets'),
                    path('fetch-departments/', self.fetch_departments, name='fetch_departments'),
                    path('fetch_data/', self.admin_site.admin_view(self.fetch_data), name='fetch_data'),
                    ]
        return new_urls + urls

    def datasets(self, request):
        bit_colleges = BITCollege.objects.using('college1').all()
        nit_colleges = NITCollege.objects.using('college2').all()
        departments = []
        students = []
        college_selected = None
        department_selected = None

        if request.method == 'POST':
            # self.request.session["coll"] = [{"name": "ABC"}, {"name": "XYZ"}]
            college_id = request.POST.get('college')
            department_id = request.POST.get('department')

            if college_id:
                prefix, actual_id = college_id.split('_')
                if prefix == 'bit':
                    college_selected = BITCollege.objects.using('college1').get(id=actual_id)
                    departments = BITDepartment.objects.using('college1').filter(college=college_selected)
                elif prefix == 'nit':
                    college_selected = NITCollege.objects.using('college2').get(id=actual_id)
                    departments = NITDepartment.objects.using('college2').filter(college=college_selected)

            if department_id:
                if prefix == 'bit':
                    department_selected = BITDepartment.objects.using('college1').get(id=department_id)
                    students = BITStudent.objects.using('college1').filter(department=department_selected)
                elif prefix == 'nit':
                    department_selected = NITDepartment.objects.using('college2').get(id=department_id)
                    students = NITStudent.objects.using('college2').filter(department=department_selected)

            # if college_id:
            #     prefix, actual_id = college_id.split('_')
            #     _db_name = 'college1' if prefix == 'bit' else 'college2'
            #     college_selected = BITCollege.objects.using(_db_name).get(id=actual_id)
            #     departments = BITDepartment.objects.using(_db_name).filter(college=college_selected)
            #
            # if department_id:
            #     prefix, actual_id = college_id.split('_')
            #     _db_name = 'college2' if prefix == 'nit' else 'college1'
            #     department_selected = BITDepartment.objects.using(_db_name).get(id=department_id)
            #     students = BITStudent.objects.using(_db_name).filter(department=department_selected)

        return render(request, 'admin/BITRaipur/datasets.html', {
            'bit_colleges': bit_colleges,
            'nit_colleges': nit_colleges,
            'departments': departments,
            'students': students,
            'college_selected': college_selected,
            'department_selected': department_selected,
        })

    def fetch_departments(self, request):
        college_id = request.GET.get('college_id')
        departments = []
        if college_id:
            prefix, actual_id = college_id.split('_')
            if prefix == 'bit':
                departments = BITDepartment.objects.using('college1').filter(college_id=actual_id)
            elif prefix == 'nit':
                departments = NITDepartment.objects.using('college2').filter(college_id=actual_id)
        return JsonResponse(list(departments.values('id', 'name')), safe=False)

    def fetch_data(self, request):
        data_type = request.GET.get('type')
        data = []

        if data_type == 'bit_students':
            data = request.session.get('bit_students', [])
            print(data)
        elif data_type == 'bit_colleges':
            data = request.session.get('bit_colleges', [])
        elif data_type == 'bit_departments':
            data = request.session.get('bit_departments', [])
        elif data_type == 'nit_students':
            data = request.session.get('nit_students', [])
            print(data)
        elif data_type == 'nit_colleges':
            data = request.session.get('nit_colleges', [])
        elif data_type == 'nit_departments':
            data = request.session.get('nit_departments', [])

        return JsonResponse(data, safe=False)


admin.site.register(College)
admin.site.register(Department)
admin.site.register(Student, RecordAdmin)
