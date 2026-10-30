import uvicorn
from router.config import RouterConfig
if __name__ == "__main__":
    config=RouterConfig()
    uvicorn.run("router.app:app",host=config.host,port=config.port,log_level=config.log_level.lower())
