import sqlite3
from datetime import datetime, timedelta
from itertools import zip_longest
from random import choices, randint
from conf.db import session

import faker

NUMBER_STUDENTS = 50
NUMBER_GROUPS = 3
NUMBER_TEACHERS = 5
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
NUMBER_SCORES = 20 * NUMBER_STUDENTS
SCORES = [4.0, 3.7, 3.3, 3.0, 2.7, 2.3, 2.0, 1.7, 1.3, 1.0, 0.0]


def generate_fake_data(number_students, number_groups, number_teachers, subjects, number_score):
    fake_students = []
    fake_groups = []
    fake_teachers = []
    fake_subjects = []
    fake_scores = []
    fake_data = faker.Faker()

    for _ in range(number_students):
        fake_students.append(fake_data.name())

    for _ in range(number_groups):
        fake_groups.append('G' + str(randint(300, 399)))

    for _ in range(number_teachers):
        fake_teachers.append(fake_data.name())

    for subject in subjects:
        fake_subjects.append(subject)

    for _ in range(number_score):
        fake_scores.append(choices(SCORES, weights=[5, 6, 7, 8, 8, 8, 6, 3, 2, 1, 1], k=1)[0])

    return fake_students, fake_groups, fake_teachers, fake_subjects, fake_scores


def prepare_data(students, groups, teachers, subjects, scores):
    for_students = []
    for i, student in enumerate(students):
        first_name, last_name = student.split(' ', 1)
        group = i % len(groups) + 1
        for_students.append((first_name, last_name, group,))

    for_groups = []
    for group in groups:
        for_groups.append((group,))

    for_teachers = []
    for teacher in teachers:
        first_name, last_name = teacher.split(' ', 1)
        for_teachers.append((first_name, last_name,))

    for_subjects = []
    for i, subject in enumerate(subjects):
        teacher = i % len(teachers) + 1
        for_subjects.append((subject, teacher,))

    for_score = []
    start_date = datetime(2023, 1, 1)
    for i, score in enumerate(scores):
        student = i % len(students) + 1
        subject = i % len(subjects) + 1
        for_score.append((
            score,
            (start_date + timedelta(days=randint(0, 364))).strftime('%Y-%m-%d'),
            student,
            subject,
            ))

    for_teachers_to_group = []
    for i, _ in enumerate(zip_longest(teachers, groups)):
        teacher_index = i % len(teachers) + 1
        group_index = i % len(groups) + 1
        for_teachers_to_group.append((teacher_index, group_index))

    return for_students, for_groups, for_teachers, for_subjects, for_score, for_teachers_to_group


def insert_data_to_db(students, groups, teachers, subjects, scores, m2m):
    with session as con:
        cur = con.cursor()

        sql_to_students = 'INSERT INTO students(first_name, last_name, group_id) VALUES (?, ?, ?)'
        cur.executemany(sql_to_students, students)

        sql_to_groups = 'INSERT INTO groups(name) VALUES (?)'
        cur.executemany(sql_to_groups, groups)

        sql_to_teachers = 'INSERT INTO teachers(first_name, last_name) VALUES (?, ?)'
        cur.executemany(sql_to_teachers, teachers)

        sql_to_subjects = 'INSERT INTO subjects(name, teacher_id) VALUES (?, ?)'
        cur.executemany(sql_to_subjects, subjects)

        sql_to_scores = 'INSERT INTO scores(score, date, student_id, subject_id) VALUES (?, ?, ?, ?)'
        cur.executemany(sql_to_scores, scores)

        sql_to_teachers_to_groups = 'INSERT INTO teachers_to_groups(teacher_id, group_id) VALUES (?, ?)'
        cur.executemany(sql_to_teachers_to_groups, m2m)


if __name__ == '__main__':
    gen_list = generate_fake_data(NUMBER_STUDENTS, NUMBER_GROUPS, NUMBER_TEACHERS, SUBJECTS, NUMBER_SCORES)
    students_data, groups_data, teachers_data, subjects_data, scores_data, m2m_data = prepare_data(*gen_list)
    insert_data_to_db(students_data, groups_data, teachers_data, subjects_data, scores_data, m2m_data)
