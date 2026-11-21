from pydantic import BaseModel, Field


class AgentStep(BaseModel):
    title: str
    detail: str


class AgentResponse(BaseModel):
    text: str
    steps: list[AgentStep] = Field(default_factory=list)
    show_audio: bool = False
    task_size: str = "medium"
    timer: bool = True
    encouragement: str | None = None
    safety_notice: str | None = None
    alerted: bool = False
