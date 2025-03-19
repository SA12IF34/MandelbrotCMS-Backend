from .models import Goal
from .serializers import GoalSerializer

from missions.models import Mission
from missions.serializers import MissionSerializer

from entertainment.models import Entertainment
from entertainment.serializers import EntertainmentSerializer

from learning_tracker.models import Course
from learning_tracker.serializers import CourseSerializer

from sessions_manager.models import Project
from sessions_manager.serializers import ProjectSerializer

from django.db.models import Q
from rest_framework.serializers import ValidationError


def create_indivisual_missions(data):
    serializer = MissionSerializer(data=data, many=True)

    if serializer.is_valid():
        serializer.save()

        data = list(map(lambda x: x['id'], serializer.data))

        return data
    
    raise ValidationError()


def lockEntertainment(materials, goal):
    materials = Entertainment.objects.filter(Q(id__in=materials))
    
    for material in materials:
        serializer = EntertainmentSerializer(instance=material, data={'locked': True, 'lock_reason': goal}, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:            
            raise ValidationError()

    return True

def unlockEntertainment(materials):
    materials = Entertainment.objects.filter(Q(id__in=materials))
    
    for material in materials:
        serializer = EntertainmentSerializer(instance=material, data={'locked': False, 'lock_reason': None}, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:            
            raise ValidationError()

    return True


def get_rewards(rewards): 
    rewards = Entertainment.objects.filter(Q(id__in=rewards))
    serializer = EntertainmentSerializer(instance=rewards, many=True)

    return serializer.data

def get_projects(projects):
    projects = Project.objects.filter(Q(id__in=projects))
    serializer = ProjectSerializer(instance=projects, many=True)

    return serializer.data

def get_courses(courses):
    courses = Course.objects.filter(Q(id__in=courses))
    serializer = CourseSerializer(instance=courses, many=True)

    return serializer.data

def get_missions(missions):
    missions = Mission.objects.filter(Q(id__in=missions))
    serializer = MissionSerializer(instance=missions, many=True)

    return serializer.data

def calculateProgress(goal_data):
    
    overall_amount = 0
    done_amount = 0

    if 'projects' in goal_data:
        overall, done = calculate_projects_progress(goal_data['projects'])

        overall_amount += overall
        done_amount += done


    if 'courses' in goal_data:
        overall, done = calculate_course_progress(goal_data['courses'])

        overall_amount += overall
        done_amount += done


    if 'missions' in goal_data:
        overall, done = calculate_missions_progress(goal_data['missions'])

        overall_amount += overall
        done_amount += done

    if 'goals' in goal_data:
        
        for goal in goal_data['goals']:
            data = Goal.objects.get(id=goal)
            serializer = GoalSerializer(instance=data)

            overall, done = calculateProgress(serializer.data)[1:]

            overall_amount += overall
            done_amount += done
    
    return round((done_amount/overall_amount if overall_amount else 0)*100), overall_amount, done_amount

def calculate_projects_progress(project_ids):
    projects = Project.objects.filter(Q(id__in=project_ids))

    overall = 0
    done = 0

    for project in projects:
        count = project.partition_set.all().count()

        if project.status == 'completed':
            done += count

        overall += count
    
    return overall, done

def calculate_course_progress(course_ids):
    courses = Course.objects.filter(Q(id__in=course_ids))

    overall = 0
    done = 0

    for course in courses:
        
        if course.list:
            count = course.section_set.all().count()

            if course.status == 'done':
                done += count

            overall += count

        else:
            if course.status == 'done':
                done += 1

            overall += 1 


    return overall, done

def calculate_missions_progress(mission_ids):
    missions = Mission.objects.filter(Q(id__in=mission_ids))

    overall = 0
    done = 0

    for mission in missions:
        if mission.status == 'done':
            done += 1

        overall += 1

    return overall, done

