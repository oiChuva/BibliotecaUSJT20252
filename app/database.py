from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker, declarative_base

connectionString = "mysql+pymysql://root:usjt%402025@localhost:3306/biblioteca_online"

engine = create_engine(connectionString, echo=True)

# base = declarative_base()
# localSession = sessionmaker(bind=engine)

