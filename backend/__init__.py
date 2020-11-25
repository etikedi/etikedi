from .config import app, Base, engine
from .routes import (
    dataset_router,
    user_router,
    sample_router,
    label_router,
    config_router,
)

dataset_router.include_router(
    label_router, prefix="/{dataset_id}/labels", tags=["Labels"]
)

dataset_router.include_router(
    config_router, prefix="/{dataset_id}/config", tags=["Configs"]
)

app.include_router(dataset_router, prefix="/datasets", tags=["Datasets"])

app.include_router(user_router, prefix="/users", tags=["Users & Auth"])

app.include_router(sample_router, prefix="/samples", tags=["Samples"])
