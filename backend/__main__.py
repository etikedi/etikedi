import uvicorn

from .config import Base, engine

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    uvicorn.run('backend:app', host="0.0.0.0", reload=True)
