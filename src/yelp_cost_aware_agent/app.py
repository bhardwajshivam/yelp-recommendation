from __future__ import annotations

from fastapi import FastAPI

from yelp_cost_aware_agent.api.routes import router
from yelp_cost_aware_agent.config import load_config

config = load_config()
app = FastAPI(title=config.app_name)
app.include_router(router)
