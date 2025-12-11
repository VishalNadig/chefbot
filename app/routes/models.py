from pydantic import BaseModel


# Dummy user model
class User(BaseModel):
    """Base User Dummy Model"""

    name: str
    surname: str


# Dummy Data
users = [
    User(name='A', surname='N'),
    User(name='B', surname='O'),
    User(name='C', surname='P'),
    User(name='D', surname='Q'),
    User(name='E', surname='R'),
    User(name='F', surname='S'),
    User(name='G', surname='T'),
    User(name='H', surname='U'),
    User(name='I', surname='V'),
    User(name='J', surname='W'),
    User(name='K', surname='X'),
    User(name='L', surname='Y'),
    User(name='M', surname='Z'),
    # ...
]
