from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

# Configuración de Seguridad
SECRET_KEY = "UNMSM_FISI_SMAT_2026_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def crear_token_acceso(data: dict):
    para_encriptar = data.copy()
    expiracion = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    para_encriptar.update({"exp": expiracion})
    return jwt.encode(para_encriptar, SECRET_KEY, algorithm=ALGORITHM)

async def obtener_identidad_actual(token: str = Depends(oauth2_scheme)):
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credenciales_exception
        return username
    except JWTError:
        raise credenciales_exception