from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

# --- CONFIGURACIÓN LAB 4.2: METADATOS ---
app = FastAPI(
    title="SMAT - Sistema de Monitoreo de Alerta Temprana",
    description="""
    API robusta para la gestión y monitoreo de desastres naturales en tiempo real.
    
    **Entidades principales:**
    * **Estaciones:** Puntos de monitoreo físico.
    * **Lecturas:** Datos capturados por sensores de telemetría.
    """,
    version="1.0.0",
    contact={
        "name": "Soporte Técnico SMAT - FISI",
        "email": "juan.matiasl@unmsm.edu.pe", 
    }
)

class EstacionCreate(BaseModel):
    id: int
    nombre: str
    ubicacion: str

class LecturaCreate(BaseModel):
    estacion_id: int
    valor: float

# --- ENDPOINTS CON TAGS Y SUMMARY ---

@app.post("/estaciones/", status_code=201, tags=["Gestión de Infraestructura"], summary="Registrar estación")
def crear_estacion(estacion: EstacionCreate, db: Session = Depends(get_db)):
    nueva_estacion = models.EstacionDB(
        id=estacion.id, nombre=estacion.nombre, ubicacion=estacion.ubicacion
    )
    db.add(nueva_estacion)
    db.commit()
    db.refresh(nueva_estacion)
    return {"msg": "Estación guardada", "data": nueva_estacion}

@app.post("/lecturas/", status_code=201, tags=["Telemetría de Sensores"], summary="Recibir telemetría")
def registrar_lectura(lectura: LecturaCreate, db: Session = Depends(get_db)):
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == lectura.estacion_id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no existe")
    
    nueva_lectura = models.LecturaDB(valor=lectura.valor, estacion_id=lectura.estacion_id)
    db.add(nueva_lectura)
    db.commit()
    return {"status": "Lectura guardada"}

@app.get("/estaciones/{id}/historial", tags=["Reportes Históricos"], summary="Historial estadístico")
def obtener_historial(id: int, db: Session = Depends(get_db)):
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    valores = [l.valor for l in estacion.lecturas]
    conteo = len(valores)
    promedio = sum(valores) / conteo if conteo > 0 else 0.0
    
    return {
        "estacion_id": id,
        "lecturas": valores,
        "conteo": conteo,
        "promedio": promedio
    }