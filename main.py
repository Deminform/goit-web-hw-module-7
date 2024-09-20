import argparse
import random
import datetime

from sqlalchemy import and_, func, desc
from prettytable import PrettyTable

from conf.db import session
from conf.models import Student, Group, Teacher, Score, Subject
from error_decorator import db_error_decorator

table = PrettyTable()

model_dict = {
    'Student': [Student, ['id', 'fullname', 'group_id']],
    'Group': [Group, ['id', 'name']],
    'Teacher': [Teacher, ['id', 'fullname']],
    'Score': [Score, ['id', 'score', 'date', 'student_id', 'subject_id']],
    'Subject': [Subject, ['id', 'name', 'teacher_id']],
}


@db_error_decorator
def create_person(args):
    model, *_ = model_dict[args.model]
    first_name, last_name = args.name.split(' ')
    kwargs = {'first_name': first_name, 'last_name': last_name}
    if args.model == 'Student':
        kwargs['group_id'] = args.link_id

    person = model(**kwargs)
    session.add(person)
    session.commit()
    return "Successful!"


@db_error_decorator
def create_group(args):
    group = session.query(Group.name).filter(Group.name == args.name).all()
    if group:
        return "Already Exists!"
    group = Group(
        name=args.name)
    session.add(group)
    session.commit()
    return "Successful!"


@db_error_decorator
def create_subject(args):
    subject = Subject(
        name=args.name,
        teacher_id=args.link_id)
    session.add(subject)
    session.commit()
    return "Successful!"


@db_error_decorator
def create_score(args):
    student = None
    if args.index:
        student = (session.query(Student.id).filter(Student.id == args.index).first())
    elif args.name:
        first_name, last_name = args.name.split(' ')
        student = (session.query(Student.id)
                   .filter(and_(Student.first_name == first_name, Student.last_name == last_name))
                   .first())
    subject = (session.query(Subject.id).filter(Subject.name == args.subject).first())
    if not student:
        return "Student Not Found!"
    elif not subject:
        return "Subject Not Found!"
    score = Score(
        score=args.score,
        date=datetime.date.today(),
        student_id=student.id,
        subject_id=subject.id
    )
    session.add(score)
    session.commit()
    return "Successful!"


@db_error_decorator
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


@db_error_decorator
def remove_row_by_id(args):
    model, *_ = model_dict[args.model]
    result = session.query(model).filter(model.id == args.index).scalar()
    if not result:
        return "No such row"
    session.delete(result)
    session.commit()
    return f'Row {args.index} in {args.model} is deleted.'


@db_error_decorator
def update_row_by_id(args):
    model, *_ = model_dict[args.model]
    result = session.query(model).filter(model.id == args.index).scalar()
    if not result:
        return "No such row"

    if args.model == 'Score':
        if not args.score:
            return f"Score not provided for {args.model}."
        result.score = args.score

    elif args.model == 'Subject' and args.link_id:
        result.teacher_id = args.link_id

    elif args.model in ['Subject', 'Group']:
        if not args.name:
            return f"Name not provided for {args.model}."
        result.name = args.name

    elif args.model == 'Student' and args.link_id:
        result.group_id = args.link_id

    elif args.model in ['Student', 'Teacher']:
        if not args.name:
            return f"Name not provided for {args.model}."
        first_name, last_name = args.name.split(' ')
        result.first_name = first_name
        result.last_name = last_name

    session.commit()
    return f'Row {args.index} in {args.model} is updated.'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Homework for "Python-Web | Module 7',
        description='CLI program for CRUD operations with tables',
        epilog='Commands for the test:\n'
               '1. Create a student and assign to a group (using group ID):\n'
               '   python main.py -a create -m Student -n "John Doe" --group_id 1\n\n'
               '2. Create a group:\n'
               '   python main.py -a create -m Group -n "Group A"\n\n'
               '3. Create a teacher:\n'
               '   python main.py -a create -m Teacher -n "Albert Einstein"\n\n'
               '4. Create a subject (teacher assigned randomly):\n'
               '   python main.py -a create -m Subject --name "Psychology" --link_id 1\n\n'
               '5. Create a score for a student (using name):\n'
               '   python main.py -a create -m Score -n "John Doe" --subject "Mathematics" --score 4.0\n\n'
               '6. Create a score for a student (using ID):\n'
               '   python main.py -a create -m Score -id 38 --subject "Mathematics" --score 4.0\n\n'
               '7. List all students:\n'
               '   python main.py -a list -m Student\n\n'
               '8. Remove a student by ID:\n'
               '   python main.py -a remove -m Student -id 1\n\n'
               '9. Update a student name by ID:\n'
               '   python main.py -a update -m Student -id 1 -n "Johnathan Doe"\n\n'
               '10. Update a student group by ID:\n'
               '    python main.py -a update -m Student -id 1 --link_id 2\n\n'
               '11. Update a subject to assign a new teacher (by teacher ID):\n'
               '    python main.py -a update -m Subject -id 7 --link_id 4\n\n'
               '12. Update a subject name by ID:\n'
               '    python main.py -a update -m Subject -id 5 --name "Advanced Psychology"\n\n'
               '13. Update a group name by ID:\n'
               '    python main.py -a update -m Group -id 3 --name "Group B"\n',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-a', '--action',
                        type=str,
                        help='• Options: create / update / list / remove.',
                        metavar='',
                        required=True)

    parser.add_argument('-m', '--model',
                        type=str,
                        help='• Choose a model: Student / Group / Teacher / Score / Subject.',
                        metavar='',
                        required=True)

    parser.add_argument('-n', '--name',
                        type=str,
                        help='• Enter fullname "first_name last_name".',
                        metavar='')

    parser.add_argument('-id', '--index',
                        type=int,
                        help='• Row index.',
                        metavar='')

    parser.add_argument('--link_id',
                        type=int,
                        help='• Additional identifier for linking tables.',
                        metavar='')

    parser.add_argument('--score',
                        type=float,
                        help='• Score options: 4.0 / 3.7 / 3.3 / 3.0 / 2.7 / 2.3 / 2.0 / 1.7 / 1.3 / 1.0 / 0.0.',
                        metavar='')

    parser.add_argument('--subject',
                        type=str,
                        help='• To show subjects options use: "python main.py -a list -m Subject".',
                        metavar='')

    argv = parser.parse_args()

    if argv.action == 'create' and argv.model in ['Student', 'Teacher']:
        print(create_person(argv))
    elif argv.action == 'create' and argv.model == 'Score':
        print(create_score(argv))  # -a create -m Score -n 'John Doe' --score 4 -- subject 'Art'
    elif argv.action == 'create' and argv.model == 'Group':
        print(create_group(argv))
    elif argv.action == 'create' and argv.model == 'Subject':
        print(create_subject(argv))  # -a create -m Subject --name 'G777' (Вчитель назначається випадково)

    elif argv.action == 'list':
        print(show_list(argv))

    elif argv.action == 'remove':
        print(remove_row_by_id(argv))

    elif argv.action == 'update':
        print(update_row_by_id(argv))
