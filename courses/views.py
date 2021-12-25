from django.shortcuts import redirect, render
from .models import *
import csv
import datetime
from django.db.models import Sum, Max, Min

def check_time(time):
    # check HH:MM format 
    try:
        datetime.datetime.strptime(time, '%H:%M')
        return True
    except ValueError:
        return False


# upload an xl file and save data to database
def upload(request):
    if request.method == 'POST':
        myfile = request.FILES.get('myfile')
        data = myfile.read().decode('utf-8').splitlines()
        #skip the first line
        data = data[1:]
        reader = csv.reader(data)
        for line in reader:
            # SCHOOL_TITLE	COFFER_COURSE_ID	COFFERED_WITH	SECTION	CREDIT_HOUR	CAPACITY	ENROLLED	ROOM_ID	ROOM_CAPACITY	BLOCKED	COURSE_NAME	FACULTY_FULL_NAME	STRAT_TIME	END_TIME	ST_MW
            # SCHOOL_TITLE, COURSE_ID, COFFERED_WITH, SECTION, SECTION, CAPACITY, ENROLLED, ROOM_ID, ROOM_CAPACITY, BLOCKED, COURSE_NAME, FACULTY_FULL_NAME, STRAT_TIME, END_TIME, ST_MW = line        
            SCHOOL_TITLE, COURSE_ID, COFFERED_WITH, SECTION, CREDIT_HOUR, CAPACITY, ENROLLED,	ROOM_ID, ROOM_CAPACITY, BLOCKED,	COURSE_NAME, FACULTY_FULL_NAME,	START_TIME,	END_TIME,ST_MW,	Dept, ClassSize, stuCr, year, semester, Level, SemesterNo, _ = line	
            
            find = Course.objects.filter(course_id=COURSE_ID, section=SECTION, year=year, semester=semester)
            if find:
                continue
            
            
            faculty, faculty_created = Faculty.objects.get_or_create(id_no = FACULTY_FULL_NAME.split('-')[0], name = FACULTY_FULL_NAME.split('-')[1])
            faculty.save()
            
            school, school_created = School.objects.get_or_create(school_title = SCHOOL_TITLE)
            school.save()
            
            department, department_created = Department.objects.get_or_create(name = Dept, school = school)
            department.save()
            
            room, room_created = Room.objects.get_or_create(room_id = ROOM_ID, room_capacity = ROOM_CAPACITY)
            room.save()
            
            
            
            course, course_created = Course.objects.get_or_create(
                course_id = COURSE_ID, 
                section = SECTION, 
                credit_hour = CREDIT_HOUR, 
                capacity = CAPACITY, 
                enrolled = ENROLLED, 
                room = room, 
                course_name = COURSE_NAME, 
                faculty = faculty, 
                start_time = START_TIME if check_time(START_TIME) else datetime.time(0,0), 
                end_time = END_TIME if check_time(END_TIME) else datetime.time(0,0), 
                st_mw = ST_MW,
                student_credit = stuCr,
                year = year, 
                semester = semester,
                department = department,
                class_size = 0 if ClassSize == '' else ClassSize,
                level = Level,
            )
            
            course.save()
        return redirect('/upload/')
    return render(request, 'courses/upload.html')

def test_view(request):
    all_years = Course.objects.all().values_list('year', flat=True).distinct()
    all_semesters = Course.objects.all().values_list('semester', flat=True).distinct()
    
    revenue_dict = {}
    for year in all_years:
        for semester in all_semesters:
            revenue_dict[(year, semester)] = Course.objects.filter(year=year, semester=semester).aggregate(Sum('student_credit'))['student_credit__sum']
    
    return render(request, 'courses/hello.html', {'revenue_dict': revenue_dict})


def home(request, **kwargs):
    return render(request, 'courses/home.html', {'nums': range(2009, 2022), 'seasons': ['Summer', 'Spring', 'Autumn']})


def dept_chart(request, **kwargs):
    dept = Department.objects.filter(name=kwargs['dept'])[0]   # cse is the target dept for now
    counter_dict = {}
    percentChange = {}
    courses = Course.objects.filter(department=dept)
    for course in courses:
        if course.semester + str(course.year) in counter_dict:
            counter_dict[str(course.semester + str(course.year))] += course.student_credit
        else:
            counter_dict[str(course.semester + str(course.year))] = course.student_credit

    minyear = min([course.year for course in courses])   # first year in the data
    for course in counter_dict:
        if int(course[-4:]) == minyear:
            continue
        increase = (counter_dict[course] - counter_dict[course[:-4] + str(int(course[-4:]) - 1)])/counter_dict[course[:-4] + str(int(course[-4:]) - 1)]
        increase *= 100
        percentChange[course] = increase
    
    return render(request, 'courses/deptRev.html', {'dept': dept, 'counter_dict': counter_dict, 'percentChange': percentChange})


def school_chart(request, **kwargs):
    school = School.objects.filter(school_title=kwargs['dept'])[0]   #  target school for now
    counter_dict = {}
    percentChange = {}
    depts = Department.objects.filter(school=school)
    courses = []
    for dept in depts:
        courses = courses + list(Course.objects.filter(department=dept))
    # print(courses)
    for course in courses:
        if course.semester + str(course.year) in counter_dict:
            counter_dict[str(course.semester + str(course.year))] += course.student_credit
        else:
            counter_dict[str(course.semester + str(course.year))] = course.student_credit

    minyear = min([course.year for course in courses])   # first year in the data
    for course in counter_dict:
        if int(course[-4:]) == minyear:
            continue
        increase = (counter_dict[course] - counter_dict[course[:-4] + str(int(course[-4:]) - 1)])/counter_dict[course[:-4] + str(int(course[-4:]) - 1)]
        increase *= 100
        percentChange[course] = increase
    
    return render(request, 'courses/schoolRev.html', {'school': school, 'counter_dict': counter_dict, 'percentChange': percentChange})


def school_data(school):
    counter_dict = {}
    depts = Department.objects.filter(school=school)
    courses = []
    for dept in depts:
        courses = courses + list(Course.objects.filter(department=dept))
    for course in courses:
        if course.semester + str(course.year) in counter_dict:
            counter_dict[str(course.semester + str(course.year))] += course.student_credit
        else:
            counter_dict[str(course.semester + str(course.year))] = course.student_credit
    return counter_dict


def all_school_trend(request):
    schools = School.objects.all()
    allSchoolData = {}
    for school in schools:
        data = school_data(school)
        allSchoolData[school.school_title] = data
    return render(request, 'courses/allSchoolTrend.html', {'data': allSchoolData})


def dept_data(dept):
    counter_dict = {}
    courses = Course.objects.filter(department=dept)
    for course in courses:
        if course.semester + str(course.year) in counter_dict:
            counter_dict[str(course.semester + str(course.year))] += course.student_credit
        else:
            counter_dict[str(course.semester + str(course.year))] = course.student_credit
    return counter_dict        

def all_dept_trend(request):
    depts = list(Department.objects.filter(name= 'CSE'))[0:1] + list(Department.objects.filter(name='EEE')) + list(Department.objects.filter(name='PhySci'))
    print(Department.objects.filter(name= 'CSE'))
    allDeptData = {}
    for dept in depts:
        data = dept_data(dept)
        allDeptData[dept.name] = data
    print(allDeptData)
    return render(request, 'courses/allDeptTrend.html', {'data': allDeptData})



def iub_trend(request):
    counter_dict = {}
    percentChange = {}
    courses = Course.objects.all()
    for course in courses:
        if course.semester + str(course.year) in counter_dict:
            counter_dict[str(course.semester + str(course.year))] += course.student_credit
        else:
            counter_dict[str(course.semester + str(course.year))] = course.student_credit

    minyear = min([course.year for course in courses])   # first year in the data
    for course in counter_dict:
        if int(course[-4:]) == minyear:
            continue
        increase = (counter_dict[course] - counter_dict[course[:-4] + str(int(course[-4:]) - 1)])/counter_dict[course[:-4] + str(int(course[-4:]) - 1)]
        increase *= 100
        percentChange[course] = increase
    
    return render(request, 'courses/iubRev.html', {'counter_dict': counter_dict, 'percentChange': percentChange})

from collections import OrderedDict

def rev_among_schools(request):
    season = ['Spring', 'Summer', 'Autumn']

    start = 2009
    end = 2021
    keys = [i + str(j) for j in range(start, end + 1) for i in season]

    schools = list(School.objects.all())
    allSchoolData = {}
    
    for school in schools:
        allSchoolData[school.school_title] = dict()
        data = school_data(school)
        for key in keys:
            if key in data:
                allSchoolData[school.school_title][key] = data[key]
            else:
                allSchoolData[school.school_title][key] = 0

    for i in range(len(schools)):
        if i == 0:
            continue

        for key in allSchoolData['SLASS']:
            allSchoolData[schools[i].school_title][key] += allSchoolData[schools[i - 1].school_title][key] 

    return render(request, 'courses/revAmongSchool.html', {'data': allSchoolData})




def rev_of_sets(request):
    season = ['Spring', 'Summer', 'Autumn']

    start = 2009
    end = 2021
    keys = [i + str(j) for j in range(start, end + 1) for i in season]

    depts = list(Department.objects.filter(name='CSE'))[0:1] + list(Department.objects.filter(name='EEE')) + list(Department.objects.filter(name='PhySci'))
    allDeptData = {}
    
    for dept in depts:
        allDeptData[dept.name] = dict()
        data = dept_data(dept)
        for key in keys:
            if key in data:
                allDeptData[dept.name][key] = data[key]
            else:
                allDeptData[dept.name][key] = 0
    for i in range(len(depts)):
        if i == 0:
            continue
        for key in allDeptData[depts[i].name]:
            allDeptData[depts[i].name][key] += allDeptData[depts[i - 1].name][key]
    return render(request, 'courses/revOfSets.html', {'data': allDeptData})


def class_dist(request, **kwargs):
    sem = kwargs['sem']
    year = kwargs['year']
    schools = School.objects.all()
    keys = [str(10 * i - 9) + '-' + str(10 * i) for i in range(1,7)]
    keys.append('60+')

    enrolledDist = {}
    for school in schools:
        enrolledDist[school.school_title] = {k: 0 for k in keys}
        depts = Department.objects.filter(school=school)
        for dept in depts:
            courses = Course.objects.filter(department=dept, semester=sem, year=int(year))
            for course in courses:
                if course.enrolled < 10:
                    enrolledDist[school.school_title]['1-10'] += 1
                elif course.enrolled < 20:
                    enrolledDist[school.school_title]['11-20'] += 1
                elif course.enrolled < 30:
                    enrolledDist[school.school_title]['21-30'] += 1
                elif course.enrolled < 40:
                    enrolledDist[school.school_title]['31-40'] += 1
                elif course.enrolled < 50:
                    enrolledDist[school.school_title]['41-50'] += 1
                elif course.enrolled < 60:
                    enrolledDist[school.school_title]['51-60'] += 1
                else:
                    enrolledDist[school.school_title]['60+'] += 1
    
    return render(request, 'courses/enrolledDist.html', {'title': sem + year, 'data': enrolledDist})


def pie_chart(request, **kwargs):
    sem = kwargs['sem']
    year = kwargs['year']    
    schools = School.objects.all()
    keys = [str(10 * i - 9) + '-' + str(10 * i) for i in range(1,7)]
    keys.append('60+')

    enrolledDist = {}
    for school in schools:
        enrolledDist[school.school_title] = {k: 0 for k in keys}
        depts = Department.objects.filter(school=school)
        for dept in depts:
            courses = Course.objects.filter(department=dept, semester=sem, year=int(year))
            for course in courses:
                if course.enrolled < 10:
                    enrolledDist[school.school_title]['1-10'] += 1
                elif course.enrolled < 20:
                    enrolledDist[school.school_title]['11-20'] += 1
                elif course.enrolled < 30:
                    enrolledDist[school.school_title]['21-30'] += 1
                elif course.enrolled < 40:
                    enrolledDist[school.school_title]['31-40'] += 1
                elif course.enrolled < 50:
                    enrolledDist[school.school_title]['41-50'] += 1
                elif course.enrolled < 60:
                    enrolledDist[school.school_title]['51-60'] += 1
                else:
                    enrolledDist[school.school_title]['60+'] += 1

    for6 = {k: 0 for k in keys}
    for7 = {k: 0 for k in keys}
    for key in keys:
        summ = 0
        for school in enrolledDist:
            summ += enrolledDist[school][key]
        for6[key] = summ / 12
        for7[key] = summ / 14
    return render(request, 'courses/PIE.html', {'title': sem + year, 'for6':for6, 'for7': for7 })
    



