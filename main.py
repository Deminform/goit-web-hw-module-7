import argparse
import random
import datetime

from sqlalchemy import and_, func, desc
from prettytable import PrettyTable

from conf.db import session
from conf.models import Student, Group, Teacher, Score, Subject


table = PrettyTable()

model_dict = {
    'Student': [Student, ['id', 'fullname', 'group_id']],
    'Group': [Group, ['id', 'name']],
    'Teacher': [Teacher, ['id', 'fullname']],
    'Score': [Score, ['id', 'score', 'date', 'student_id', 'subject_id']],
    'Subject': [Subject, ['id', 'name', 'teacher_id']],
}


def create_student(args):
    first_name, last_name = args.name.split(' ')
    student = Student(
        first_name=first_name,
        last_name=last_name,
        group_id=args.group_name)
    session.add(student)
    session.commit()


def create_teacher(args):
    first_name, last_name = args.name.split(' ')
    teacher = Teacher(
        first_name=first_name,
        last_name=last_name)
    session.add(teacher)
    session.commit()


def create_group(args):
    group = session.query(Group.name).filter(Group.name == args.name).all()
    if not group:
        group = Group(
            name=args.name)
        session.add(group)
        session.commit()
        message = f'Group: {args.name} was created'
    else:
        message = f'Group: {args.name} already exists'
    return message


def create_subject(args):
    teacher = session.query(func.count(Teacher.id)).scalar()
    subject = Subject(
        name=args.name,
        teacher_id=random.randint(1, teacher))
    session.add(subject)
    session.commit()


def create_score(args):
    student = session.query(Student.id).filter(Student.fullname == args.name).one()
    subject = session.query(Subject.id).filter(Subject.name == args.subject).one()
    score = Score(
        score=args.score,
        date=datetime.date.today(),
        student_id=student.id,
        subject_id=subject.id
        )
    session.add(score)
    session.commit()


def show_list(args):
    model, columns = model_dict[args.model]
    result = session.query(model).all()
    table.field_names = columns
    all_rows = []

    for obj in result:
        filed = []
        for column in columns:
            filed.append(getattr(obj, column))
        all_rows.append(filed)

    table.add_rows(all_rows)
    return table.get_string()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Homework for "Python-Web | Module 7',
        description='CLI program for CRUD operations with tables',
        epilog='Helpful text for the user will be added')

    parser.add_argument('-a', '--action',
                        type=str,
                        help='CRUD operation [create, update, list, remove]',
                        metavar='',
                        required=True)

    parser.add_argument('-m', '--model',
                        type=str,
                        help='Choose a model ["Student", "Group", "Teacher", "Score", "Subject"]',
                        metavar='',
                        required=True)

    parser.add_argument('-g', '--group_name',
                        type=str,
                        help='Need to choose a model',
                        metavar='')

    parser.add_argument('-sc', '--score',
                        type=float,
                        help='Need to choose a score [4.0, 3.7, 3.3, 3.0, 2.7, 2.3, 2.0, 1.7, 1.3, 1.0, 0.0]',
                        metavar='')

    parser.add_argument('-sub', '--subject',
                        type=str,
                        help='Need to choose a score ["Mathematics", '
                             '"Physics", '
                             '"History", '
                             '"Geography", '
                             '"Computer", "Science",'
                             ' "Biology", '
                             '"Chemistry", '
                             '"Literature", '
                             '"Art"]',
                        metavar='')

    parser.add_argument('-n', '--name',
                        type=str,
                        help='Enter fullname "first_name last_name',
                        metavar='')

    parser.add_argument('-id', '--index',
                        type=int,
                        help='Row index',
                        metavar='')

    argv = parser.parse_args()

    if argv.action == 'create' and argv.model == 'Student':
        print(create_student(argv))
    elif argv.action == 'create' and argv.model == 'Teacher':
        print(create_teacher(argv))  # -a create -m Teacher -n 'Boris Jonson'
    elif argv.action == 'create' and argv.model == 'Score':
        print(create_teacher(argv))  # -a create -m Score -n 'John Doe' --score 4 -- subject 'Art'
    elif argv.action == 'create' and argv.model == 'Group':
        print(create_group(argv))
    elif argv.action == 'create' and argv.model == 'Subject':
        print(create_subject(argv))  # -a create -m Subject --name 'G777'

    elif argv.action == 'list':
        print(show_list(argv))
