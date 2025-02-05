import uvicorn
from fastapi import FastAPI
from app.config import settings
from app.routes import router

app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)

# Include routes
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
