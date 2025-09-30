from langchain_openai import ChatOpenAI
from quiz_agents.config import settings
from quiz_agents.models import RoleRoute, ApplicantInfo, FinalReport

llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=settings.TEMPERATURE)
llm_with_role_route = llm.with_structured_output(RoleRoute)
llm_with_applicant_info = llm.with_structured_output(ApplicantInfo)
llm_with_final_report = llm.with_structured_output(FinalReport)
