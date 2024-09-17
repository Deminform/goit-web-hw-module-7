from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import joinedload, subqueryload

from conf.db import session
from conf.models import Student, Group, Teacher, Score, Subject


def select_1():
    students = (session.query(Student.fullname, func.avg(Score.score).label('avg_score'))
                .join(Score, Score.student_id == Student.id)
                .group_by(Student.id)
                .order_by(desc('avg_score')).limit(5))
    for s in students:
        print(s.fullname, round(s.avg_score, 2))


def select_2(subject='Physics'):
    students = (session.query(Student.fullname, func.avg(Score.score).label('avg_score'))
                .join(Score, Score.student_id == Student.id)
                .join(Subject, Subject.id == Score.subject_id)
                .where(Subject.name == subject)
                .group_by(Student.id)
                .order_by(desc('avg_score')).limit(1))

    for s in students:
        print(s.fullname, round(s.avg_score, 2))


if __name__ == '__main__':
    # select_1()
    select_2()
