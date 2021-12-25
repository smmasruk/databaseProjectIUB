from django.db import models

# Create your models here.
class Room(models.Model):
    room_id = models.CharField(unique=True, max_length=100)
    room_capacity = models.IntegerField()

    def __str__(self):
        return self.room_id


class Faculty(models.Model):
    id_no = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('id_no', 'name')
    
    def __str__(self):
        return self.name


class School(models.Model):
    school_title = models.CharField(max_length=100)
    
    def __str__(self):
        return self.school_title


class Department(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.name

# SCHOOL_TITLE	CourseID	COFFERED_WITH	Sec	Crs	size	stuNo	ROOM_ID	RoomSize	BLOCKED	COURSE_NAME	FACULTY_FULL_NAME	STRAT_TIME	END_TIME	ST_MW	Dept	ClassSize	stuCr	Year	Semester	Level	SemesterNo	
    

class Course(models.Model):
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    course_id = models.CharField(max_length=100)
    section = models.IntegerField()
    credit_hour = models.IntegerField()
    capacity = models.IntegerField()
    enrolled = models.IntegerField()
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    course_name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    st_mw = models.CharField(max_length=10)
    year = models.IntegerField()
    semester = models.CharField(max_length=100)
    student_credit = models.IntegerField()
    class_size = models.IntegerField()
    level = models.CharField(max_length=20, null=True)
    
    # course_id + section = unique
    class Meta:
        unique_together = ('course_id', 'section', 'year', 'semester')
    
    
    def __str__(self):
        return self.course_id + ' ' + str(self.section) + ' ' + self.semester + ' ' + str(self.year)
    
    