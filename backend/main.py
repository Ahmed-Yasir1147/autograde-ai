from fastapi import FastAPI
import uvicorn
import uvicorn
from api.v1.routes import router
from core.config import APP_TITLE, APP_VERSION, APP_DESCRIPTION
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

app.include_router(router)

@app.get("/")
def read_root():
    return {
        'name': APP_TITLE,
        'version': APP_VERSION,
        'description': APP_DESCRIPTION,
        'endpoints': {
            'POST   /api/v1/grade_exams': "Grade exams",
            'GET    /api/v1/get_grading_scheme': "Get grading scheme",
        },
    }

if __name__=='__main__':
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
    )