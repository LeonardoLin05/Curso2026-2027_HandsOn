
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mi aplicación",
    description="API desarrollada con FastAPI",
    version="1.0.0"
)

# Permitir peticiones desde React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Backend funcionando correctamente"
    }

@app.get("/api/health")
async def health():
    return {
        "status": "ok"
    }
