
from database import get_session
from seguridad import PW, SECRET_KEY
from fastapi import Depends, FastAPI, HTTPException, status, security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Field, Session, select
import jwt
app = FastAPI(title="Génesis-project")

# Constante del algoritmo (corregido el nombre de tu parámetro anterior)
ALGORITHM = "HS256"

# Esto le dice a FastAPI que busque el token en el header "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.get('/')
def rodhelp():
    return {"message": "Génesis API running"}

class Account(SQLModel, table=True):  
    id: str = Field(primary_key=True)  
    name: str
    power: str | None = Field(default="USER")
    password: str

@app.post('/register', status_code=status.HTTP_201_CREATED)
def create_account(
    i_name: str, 
    i_password: str, 
    session: Session = Depends(get_session) 
):
    pw = PW.createPw(i_password)
    i_id = PW.generate_id()
    statname = session.exec(select(Account).where(Account.name == i_name)).first()
    statid = session.exec(select(Account).where(Account.id == i_id)).first()

    if statname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,  
            detail='this name already exists, please try again'
        )
    if statid:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  
            detail='this ID already exists, fatal error'
        )
    newacc = Account(id=i_id, name=i_name, password=pw)  
    session.add(newacc)
    session.commit()
    session.refresh(newacc)
    
    return {"message": "Account created successfully", "id": newacc.id}

@app.post('/login')
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    # OAuth2PasswordRequestForm guarda el usuario en form_data.username y la contraseña en form_data.password
    find_user = session.exec(select(Account).where(Account.name == form_data.username)).first()
    
    if find_user and PW.checkPw(form_data.password, find_user.password):
        token_data = {'name': find_user.name, 'id': find_user.id, 'rol': find_user.power}
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

# Función de dependencia para validar el token y extraer al usuario actual
def get_current_user(
    token: str = Depends(oauth2_scheme), 
    session: Session = Depends(get_session)
):
    try:
        # Decodificamos el token usando tu misma SECRET_KEY y ALGORITHM
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name: str = payload.get("name")
        if user_name is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired"
        )
    
    # Buscamos al usuario en la base de datos para asegurarnos de que aún existe
    user = session.exec(select(Account).where(Account.name == user_name)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

@app.delete('/delete_account')
def delete_account(
    current_user: Account = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Gracias a get_current_user, FastAPI intercepta la petición, valida el token 
    # y si es correcto, te inyecta el objeto 'current_user' del usuario autenticado.
    
    session.delete(current_user)
    session.commit()
    
    return {"message": f"Account '{current_user.name}' successfully deleted"}