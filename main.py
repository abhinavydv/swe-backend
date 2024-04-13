from fastapi import FastAPI
from routers import user, hotels
import models as _
from config.db import engine, Base


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router)
app.include_router(hotels.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
