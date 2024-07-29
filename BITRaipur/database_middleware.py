from django.utils.deprecation import MiddlewareMixin
from BITRaipur.models import Student as BITStudent, College as BITCollege, Department as BITDepartment
from NITRaipur.models import Student as NITStudent, College as NITCollege, Department as NITDepartment


class DatabaseMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.path.startswith('/admin/'):
            # Fetch BITRaipur data
            bit_students = BITStudent.objects.using('college1').all()
            bit_colleges = BITCollege.objects.using('college1').all()
            bit_departments = BITDepartment.objects.using('college1').all()

            # Fetch NITRaipur data
            nit_students = NITStudent.objects.using('college2').all()
            nit_colleges = NITCollege.objects.using('college2').all()
            nit_departments = NITDepartment.objects.using('college2').all()

            # Store data in session
            request.session['bit_students'] = list(bit_students.values())
            request.session['bit_colleges'] = list(bit_colleges.values())
            request.session['bit_departments'] = list(bit_departments.values())
            request.session['nit_students'] = list(nit_students.values())
            request.session['nit_colleges'] = list(nit_colleges.values())
            request.session['nit_departments'] = list(nit_departments.values())

    def process_response(self, request, response):
        return response
