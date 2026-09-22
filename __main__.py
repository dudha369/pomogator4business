from app import app
from bot_instance import setup_routes
from config import API_HOST, API_PORT

setup_routes()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=API_HOST, port=API_PORT)
