from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import engine, get_db
from .auth import crear_token_acceso, obtener_identidad_actual

# Crea las tablas al iniciar
models.Base.metadata.create_all(bind=engine)

# --- METADATOS EXACTOS DE LA GUÍA (Lab 4.2) ---
app = FastAPI(
    title="SMAT - Sistema de Monitoreo de Alerta Temprana",
    description="""
API robusta para la gestión y monitoreo de desastres naturales.
Permite la telemetría de sensores en tiempo real y el cálculo de niveles de riesgo.

**Entidades principales:**
* **Estaciones:** Puntos de monitoreo físico.
* **Lecturas:** Datos capturados por sensores.
* **Riesgos:** Análisis de criticidad basado en umbrales.
""",
    version="1.0.0",
    terms_of_service="http://unmsm.edu.pe/terms/",
    contact={
        "name": "Soporte Técnico SMAT - FISI",
        "url": "http://fisi.unmsm.edu.pe",
        "email": "juan.matiasl@unmsm.edu.pe", # Tu correo para que sepa que eres tú
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# --- REQUISITO LAB 4.3: CONFIGURACIÓN DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ENDPOINT DE SEGURIDAD (LAB 4.4)
@app.post("/token", tags=["Seguridad"])
async def login():
    return {"access_token": crear_token_acceso({"sub": "admin_smat"}), "token_type": "bearer"}

# ENDPOINTS PROTEGIDOS CON JWT
@app.post("/estaciones/", status_code=201, tags=["Gestión de Infraestructura"])
def crear_estacion(estacion: schemas.EstacionCreate, db: Session = Depends(get_db), token: str = Depends(obtener_identidad_actual)):
    return crud.crear_estacion(db=db, estacion=estacion)

@app.post("/lecturas/", status_code=201, tags=["Telemetría de Sensores"])
def registrar_lectura(lectura: schemas.LecturaCreate, db: Session = Depends(get_db), token: str = Depends(obtener_identidad_actual)):
    # RETO DE INTEGRIDAD 4.4: Verificar si existe la estación
    estacion_db = db.query(models.EstacionDB).filter(models.EstacionDB.id == lectura.estacion_id).first()
    if not estacion_db:
        raise HTTPException(status_code=404, detail="Error de Integridad: La estación no existe.")
    return crud.crear_lectura(db=db, lectura=lectura)

@app.get("/estaciones/stats", response_model=schemas.StatsResumen, tags=["Auditoría"])
def obtener_estadisticas(db: Session = Depends(get_db)):
    return crud.obtener_estadisticas_globales(db)

@app.get("/estaciones/{id}/historial", tags=["Reportes Históricos"])
def obtener_historial(id: int, db: Session = Depends(get_db)):
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    valores = [l.valor for l in estacion.lecturas]
    conteo = len(valores)
    promedio = sum(valores) / conteo if conteo > 0 else 0.0
    return {"estacion_id": id, "lecturas": valores, "conteo": conteo, "promedio": promedio}