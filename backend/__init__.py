from .config import app
from .routes import (
    dataset_router,
    user_router,
    sample_router,
    label_router,
    config_router,
    labeling_functions_router,
    battle_router
)

dataset_router.include_router(
    label_router, prefix="/{dataset_id}/labels", tags=["Labels"]
)

dataset_router.include_router(
    config_router, prefix="/{dataset_id}/config", tags=["Configs"]
)

dataset_router.include_router(
    labeling_functions_router, prefix="/{dataset_id}/labelingfunctions", tags=["LabelingFunctions"]
)

app.include_router(battle_router, prefix="/{dataset_id}/al-wars")

app.include_router(dataset_router, prefix="/datasets", tags=["Datasets"])

app.include_router(user_router, prefix="/users", tags=["Users & Auth"])

app.include_router(sample_router, prefix="/samples", tags=["Samples"])
