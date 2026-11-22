from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from sqlmodel import Field, SQLModel, Session, select

from database import get_session
from seguridad import PW, SECRET_KEY

router = APIRouter()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# tokenUrl apunta al endpoint de login montado bajo /users
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


class Account(SQLModel, table=True):
    __tablename__ = "accounts"
    id: str = Field(primary_key=True)
    name: str = Field(index=True, unique=True)
    power: str | None = Field(default="USER")
    password: str


class AccountCreate(SQLModel):
    name: str
    password: str


class AccountResponse(SQLModel):
    id: str
    name: str
    power: str | None


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    payload: AccountCreate,
    session: Session = Depends(get_session),
):
    existing_user = session.exec(
        select(Account).where(Account.name == payload.name)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This name already exists, please try again",
        )

    new_acc = Account(
        id=PW.generate_id(),
        name=payload.name,
        password=PW.createPw(payload.password),
    )
    session.add(new_acc)
    session.commit()
    session.refresh(new_acc)

    return new_acc


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    find_user = session.exec(
        select(Account).where(Account.name == form_data.username)
    ).first()

    if find_user and PW.checkPw(form_data.password, find_user.password):
        token = create_access_token(
            {"sub": find_user.name, "id": find_user.id, "power": find_user.power}
        )
        return {"access_token": token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> Account:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name: str | None = payload.get("sub")
        if user_name is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired",
        )

    user = session.exec(select(Account).where(Account.name == user_name)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


@router.get("/me", response_model=AccountResponse)
def read_current_user(current_user: Account = Depends(get_current_user)):
    return current_user


@router.delete("/delete_account")
def delete_account(
    current_user: Account = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    session.delete(current_user)
    session.commit()
    return {"message": f"Account '{current_user.name}' successfully deleted"}