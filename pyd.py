from pydantic import BaseModel




class User(BaseModel):
    name : str
    email : str
    account_id : int


user = User(name="rafi", email="hello@test.com", account_id=3)
print(user)
