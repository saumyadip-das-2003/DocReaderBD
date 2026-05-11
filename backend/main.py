from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import ocr, reader, template


app = FastAPI(title="DocReader BD API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ocr.router)
app.include_router(template.router)
app.include_router(reader.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "service": "DocReader BD API"}


@app.on_event("startup")
async def on_startup() -> None:
    print("DocReader BD API started")
