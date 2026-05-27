from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.convert import router as convert_router

app = FastAPI(
    title="文件格式转换 API",
    description="File format conversion service supporting documents, data, LaTeX, and OCR",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(convert_router)


@app.get("/")
async def root():
    return {"message": "文件格式转换 API is running", "docs": "/docs"}
