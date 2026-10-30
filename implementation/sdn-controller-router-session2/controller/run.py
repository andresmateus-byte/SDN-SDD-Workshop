import uvicorn
from controller.config import ControllerConfig
if __name__ == "__main__":
    config=ControllerConfig()
    uvicorn.run("controller.app:app",host=config.host,port=config.port,log_level=config.log_level.lower())
