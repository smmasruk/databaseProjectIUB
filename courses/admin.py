from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Course) 
admin.site.register(Department) 
admin.site.register(Faculty)
admin.site.register(School) 
admin.site.register(Room)

