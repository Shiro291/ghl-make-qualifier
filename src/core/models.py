from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class InboundLead(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    phone: str = Field(..., min_length=8)
    inquiry_text: str = Field(..., min_length=10)

class LeadQualification(BaseModel):
    estimated_capital: str = Field(description="Estimated capital e.g., $10k, Unknown")
    urgency_score: int = Field(ge=1, le=5, description="Urgency from 1 to 5")
    primary_goal: str = Field(description="Brief summary of their goal")
    status: str = Field(pattern="^(qualified|handoff)$", description="Must be 'qualified' or 'handoff'")
    reason: Optional[str] = Field(None, description="Reason for the status")
