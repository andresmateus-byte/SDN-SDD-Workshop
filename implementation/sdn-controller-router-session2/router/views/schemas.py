from pydantic import BaseModel, ConfigDict, Field
class PacketRequest(BaseModel):
    model_config=ConfigDict(extra="ignore")
    src: str = Field(min_length=1)
    dst: str = Field(min_length=1)
    packet_id: str | None = Field(default=None,min_length=1,max_length=64)
    metric: str = "delay"
