import bcrypt
import uuid
class PasswordClass():
    
    def __init__(self):
        pass
    @staticmethod
    def createPw(pw):
        salt = bcrypt.gensalt()
        bit = pw.encode('utf-8')
        hash = bcrypt.hashpw(bit, salt)
        return hash
    @staticmethod
    def checkPw(pwSource,pwTarget):
        bit= pwSource.encode('utf-8')
        endBool= bcrypt.checkpw(bit,pwTarget)
        return endBool
    @staticmethod
    def help():
        print('''
        PW.createPw(pw)
        PW.checkPW(source,target)
        PW.generate_id()
        ''')  
    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())
PW = PasswordClass()
SECRET_KEY="noiuxnq8yw97t2q76d6auk [293u08r7t2yf32bepfijap]wgdywgoiwuhckslue98y38gjdsngi7at97gdoqoboeyw7c9s7gcspdnfl3h9efy8hp4feçsmlk jx9"