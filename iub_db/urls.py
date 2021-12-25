"""iub_db URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from courses.views import (upload, test_view, dept_chart, iub_trend, rev_among_schools, class_dist, pie_chart,
                    school_chart, home, all_school_trend, all_dept_trend, rev_of_sets)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/', upload, name='upload'),
    path('', home, name='home'),
    path('dept_chart/<str:dept>/', dept_chart, name='deptchar'),
    path('school_chart/<str:dept>/', school_chart, name='schoolchar'),
    path('allschooltrend/', all_school_trend, name='revTrendschl'),
    path('alldepttrend/', all_dept_trend, name='revTrenddept'),
    path('iubtrend/', iub_trend, name='revIub'),
    path('revamongschools/', rev_among_schools, name='revAmongSchools'),
    path('revofsets/', rev_of_sets, name='revOfSets'),
    path('class/<str:sem>/<str:year>', class_dist, name='classDist'),
    path('pie/<str:sem>/<str:year>', pie_chart, name='pieChart'),

]
