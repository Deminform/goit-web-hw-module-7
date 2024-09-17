from random import choice, choices, randint

from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

from conf.db import session
from conf.models import Student, Group, Teacher, Score, Subject

fake = Faker('uk-UA')
SCORES = [4.0, 3.7, 3.3, 3.0, 2.7, 2.3, 2.0, 1.7, 1.3, 1.0, 0.0]
SUBJECTS = [
    'Mathematics',
    'Physics',
    'History',
    'Geography',
    'Computer Science',
    'Biology',
    'Chemistry',
    'Literature',
    'Art'
]


def insert_students(students_count):
    groups = session.query(Group).all()

    for _ in range(students_count):
        student = Student(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            group_id=choice(groups).id,
        )
        session.add(student)


def insert_groups(groups_count):
    for _ in range(groups_count):
        group = Group(
            name=('G' + str(randint(300, 399))),
        )
        session.add(group)


def insert_teachers(teachers_count):
    for _ in range(teachers_count):
        teacher = Teacher(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
        )
        session.add(teacher)


def insert_subjects():
    teachers = session.query(Teacher).all()

    for sub in SUBJECTS:
        subject = Subject(
            name=sub,
            teacher_id=choice(teachers).id,
        )
        session.add(subject)


def insert_scores(scores_count):
    students = session.query(Student).all()
    subjects = session.query(Subject).all()

    for student in students:
        fake_date = fake.date_between(start_date='-2y')
        for _ in range(scores_count):
            score = Score(
                score=choices(SCORES, weights=[5, 6, 7, 8, 8, 8, 6, 3, 2, 1, 1], k=1)[0],
                date=fake_date,
                student_id=student.id,
                subject_id=choice(subjects).id,
            )
            session.add(score)


if __name__ == '__main__':
    try:
        insert_groups(3)
        insert_teachers(5)
        session.commit()
        insert_students(50)
        insert_subjects()
        session.commit()
        insert_scores(20)
        session.commit()
    except SQLAlchemyError as e:
        print(e)
        session.rollback()
    finally:
        session.close()

