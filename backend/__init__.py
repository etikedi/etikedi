from .config import app, Base, engine
from .routes import dataset_router, user_router, sample_router, label_router


app.include_router(
    dataset_router,
    prefix='/datasets',
    tags=['Datasets']
)

app.include_router(
    user_router,
    prefix='/users',
    tags=['Users & Auth']
)

app.include_router(
    sample_router,
    prefix='/samples',
    tags=['Samples']
)

app.include_router(
    label_router,
    tags=['Labels']
)
