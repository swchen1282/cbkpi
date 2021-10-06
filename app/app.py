from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import api
from settings import Config

cathay_api = FastAPI(
    title=Config.APP_NAME,
    description=Config.APP_DESC,
    version=Config.APP_VER,
)

cathay_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cathay_api.include_router(api.router)


@cathay_api.get("/")
def grreetings():
    list_of_apis = [
        {
            "id": 1,
            "name": "get_rent_data",
            "description": """591租屋網 API 查詢""",
        },
    ]
    return {
        "Greetings": "Welcome to cathay_api services for 591租屋網",
        "Interactive doc": "<api_url>/docs",
        "List of apis": list_of_apis
    }
