from django.contrib import admin
from .models import College, Department, Student

# Register your models here.

admin.site.register(College)
admin.site.register(Department)
admin.site.register(Student)
