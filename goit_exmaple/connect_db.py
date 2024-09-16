from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

create = create_engine('sqlite:///database/mynotes.db')
Session = sessionmaker(bind=create)
session = Session()