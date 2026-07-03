from pydantic import BaseModel

# ================== Pydantic models ===================

# Request body pydantic models
class UserInput(BaseModel):
    input : str
    interview_type : int             # 1 corresponds to user being the interviewer and 2 to user being the interviewee    


# Response Body pydantic models
class ResponseModel(BaseModel):
    success : bool
    data : str | dict
    message : str
    meta : dict = {}

class Messages(BaseModel):
    interviewer : str
    data : list[dict]