from sqlalchemy import and_, func, desc

from conf.db import session
from conf.models import Student, Group, Teacher, Score, Subject


def select_1():
    students = (session.query(Student.fullname, func.avg(Score.score).label('avg_score'))
                .join(Score, Score.student_id == Student.id)
                .group_by(Student.id)
                .order_by(desc('avg_score')).limit(5).all()
                )
    return [(s.fullname, round(s.avg_score, 2)) for s in students]


def select_2(subject):
    students = (session.query(Student.fullname, func.avg(Score.score).label('avg_score'))
                .join(Score, Score.student_id == Student.id)
                .join(Subject, Subject.id == Score.subject_id)
                .filter(Subject.name == subject)
                .group_by(Student.id)
                .order_by(desc('avg_score')).limit(1).all()
                )
    return (students[0].fullname, round(students[0].avg_score, 2)) if students else None


def select_3(subject):
    groups = (session.query(Group.name, func.avg(Score.score).label('avg_score'))
              .join(Student, Student.group_id == Group.id)
              .join(Score, Score.student_id == Student.id)
              .join(Subject, Score.subject_id == Subject.id)
              .filter(Subject.name == subject)
              .group_by(Group.name).all()
              )
    return [(g.name, round(g.avg_score, 2)) for g in groups] if groups else []


def select_4():
    scores = session.query(func.avg(Score.score).label('avg_score')).one()
    return round(scores.avg_score, 2)


def select_5(teacher):
    subjects = (session.query(Subject.name)
                .join(Teacher, Teacher.id == Subject.teacher_id)
                .filter(Teacher.last_name == teacher).all()
                )
    return [s.name for s in subjects]


def select_6(group):
    students = (session.query(Student.fullname)
                .join(Group, Group.id == Student.group_id)
                .filter(Group.name == group).all()
                )
    return [s.fullname for s in students]


def select_7(group, subject):
    scores = (session.query(Score.score, Student.fullname)
              .join(Group, Group.id == Student.group_id)
              .join(Score, Score.student_id == Student.id)
              .join(Subject, Subject.id == Score.subject_id)
              .filter(and_(Group.name == group, Subject.name == subject))
              .group_by(Score.id, Student.id).all()
              )

    return [(s.score, s.fullname) for s in scores]


def select_8(teacher):
    scores = (session.query(func.avg(Score.score).label('avg_score'))
              .join(Subject, Subject.id == Score.subject_id)
              .join(Teacher, Teacher.id == Subject.teacher_id)
              .filter(Teacher.last_name == teacher).one()
              )
    return round(scores.avg_score, 2)


def select_9(student_fullname):
    subjects = (session.query(Subject.name)
                .join(Score, Score.subject_id == Subject.id)
                .join(Student, Student.id == Score.student_id)
                .filter(Student.fullname == student_fullname)
                .group_by(Subject.id).all()
                )
    return [s.name for s in subjects]


def select_10(student_fullname, teacher_fullname):
    subjects = (session.query(Subject.name)
                .join(Teacher, Teacher.id == Subject.teacher_id)
                .join(Score, Score.subject_id == Subject.id)
                .join(Student, Student.id == Score.student_id)
                .filter(and_(Student.fullname == student_fullname, Teacher.fullname == teacher_fullname))
                .group_by(Subject.id).all()
                )
    return [s.name for s in subjects]


def select_11(student_fullname, teacher_fullname):
    scores_subquery = (session.query(Score.score)
                       .join(Subject, Subject.id == Score.subject_id)
                       .join(Teacher, Teacher.id == Subject.teacher_id)
                       .join(Student, Student.id == Score.student_id)
                       .filter(and_(Student.fullname == student_fullname, Teacher.fullname == teacher_fullname))
                       .subquery()
                       )

    score = session.query(func.avg(scores_subquery.c.score)).scalar()
    return round(score, 2)


def select_12(group, subject):
    scores_subquery = (session.query(Student.id, func.max(Score.date).label('max_date'))
                       .join(Student, Student.id == Score.student_id)
                       .join(Group, Group.id == Student.group_id)
                       .join(Subject, Subject.id == Score.subject_id)
                       .filter(and_(Group.name == group, Subject.name == subject))
                       .group_by(Student.id)
                       .subquery()
                       )

    score = (session.query(Score.score, Student.fullname)
             .join(Student, Student.id == Score.student_id)
             .join(scores_subquery, and_(scores_subquery.c.max_date == Score.date, Student.id == scores_subquery.c.id))
             .all()
             )

    return score


if __name__ == '__main__':
    func_list = [
        select_0(),
        select_1(),
        select_2('Mathematics'),
        select_3('History'),
        select_4(),
        select_5('Франчук'),
        select_6('G320'),
        select_7('G320', 'History'),
        select_8('Ярема'),
        select_9('Варфоломій Рябошапка'),
        select_10('Варфоломій Рябошапка', 'Єфрем Франчук'),
        select_11('Варфоломій Рябошапка', 'Єфрем Франчук'),
        select_12('G320', 'History')
    ]

    for i, func in enumerate(func_list):
        print(f'\n----------------------- func #: {i + 1} --------------------------\n')
        print(func)


