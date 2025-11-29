from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os

router = APIRouter(prefix="/auth", tags=["auth"])

# Configurações JWT
SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_muito_segura_aqui")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Schemas
class UserCreate(BaseModel):
    nome: str
    email: str
    senha: str
    telefone: Optional[str] = None
    foto: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserUpdateStatus(BaseModel):
    status: str # 'active', 'blocked'

class UserUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    telefone: Optional[str] = None
    foto: Optional[str] = None

# Helpers
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# Endpoints
@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar se email já existe
    db_user = db.query(models.Usuario).filter(models.Usuario.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Verificar se é o primeiro usuário (será Admin e Ativo)
    count = db.query(models.Usuario).count()
    is_first = count == 0
    
    role = "admin" if is_first else "user"
    status_user = "active" if is_first else "pending"
    
    hashed_password = get_password_hash(user.senha)
    
    new_user = models.Usuario(
        nome=user.nome,
        email=user.email,
        senha_hash=hashed_password,
        telefone=user.telefone,
        foto=user.foto,
        role=role,
        status=status_user
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Gerar token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email, "role": new_user.role, "status": new_user.status},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "nome": new_user.nome,
            "email": new_user.email,
            "role": new_user.role,
            "status": new_user.status,
            "foto": new_user.foto
        }
    }

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm usa 'username' para o email
    user = db.query(models.Usuario).filter(models.Usuario.email == form_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado (verifique o email)",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário pendente de aprovação ou bloqueado."
        )
        
    # Atualizar último login
    user.ultimo_login = datetime.utcnow()
    db.commit()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "status": user.status},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "nome": user.nome,
            "email": user.email,
            "role": user.role,
            "status": user.status,
            "foto": user.foto
        }
    }

@router.get("/users")
def list_users(
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem listar usuários")
        
    users = db.query(models.Usuario).all()
    return [{
        "id": u.id,
        "nome": u.nome,
        "email": u.email,
        "role": u.role,
        "status": u.status,
        "foto": u.foto,
        "data_criacao": u.data_criacao,
        "ultimo_login": u.ultimo_login
    } for u in users]

@router.put("/users/{user_id}/status")
def update_status(
    user_id: int,
    status_data: UserUpdateStatus,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem alterar status")
        
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    if user.id == current_user.id:
         raise HTTPException(status_code=400, detail="Não é possível alterar o próprio status")

    user.status = status_data.status
    db.commit()
    
    return {"message": f"Status atualizado para {user.status}"}

@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem editar usuários")
        
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Não permitir admin editar o próprio role
    if user.id == current_user.id and user_data.role and user_data.role != user.role:
        raise HTTPException(status_code=400, detail="Não é possível alterar o próprio role")
    
    # Atualizar campos fornecidos
    if user_data.nome is not None:
        user.nome = user_data.nome
    if user_data.email is not None:
        # Verificar se email já existe (outro usuário)
        existing = db.query(models.Usuario).filter(
            models.Usuario.email == user_data.email,
            models.Usuario.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        user.email = user_data.email
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.telefone is not None:
        user.telefone = user_data.telefone
    if user_data.foto is not None:
        user.foto = user_data.foto
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "nome": user.nome,
        "email": user.email,
        "role": user.role,
        "status": user.status,
        "foto": user.foto,
        "telefone": user.telefone,
        "data_criacao": user.data_criacao
    }

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem deletar usuários")
        
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Não é possível deletar a própria conta")
    
    # Deletar usuário
    db.delete(user)
    db.commit()
    
    return {"message": "Usuário deletado com sucesso"}
