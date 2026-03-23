from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from irp.api.suppliers import router as suppliers_router

app = FastAPI(title="Divergent API", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(suppliers_router, prefix="/api/v1", tags=["suppliers"])


@app.get("/health")
async def health():
    return {"status": "healthy"}
