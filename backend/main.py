from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import ocr, template, reader

app = FastAPI(title="DocReader BD API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://docreaderbd.vercel.app",
        "https://*.vercel.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ocr.router)
app.include_router(template.router)
app.include_router(reader.router)

@app.get("/")
async def root():
    return {"status": "ok", "service": "DocReader BD API"}

@app.on_event("startup")
async def startup():
    print("DocReader BD API started")
