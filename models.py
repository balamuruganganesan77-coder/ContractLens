"""
Data models for ContractLens AI Agent System
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class ExtractedField(BaseModel):
    field_name: str = Field(description="Name of the extracted contract field")
    value: str = Field(description="Value of the field, or 'Not found in contract' if missing")
    source_page: int = Field(default=1, description="Source page number where field was found")
    source_clause: str = Field(default="", description="Exact source clause text snippet")
    confidence: float = Field(default=0.9, description="Confidence score between 0.0 and 1.0")


class ContractExtraction(BaseModel):
    contract_title: str = Field(default="Contract Agreement", description="Identified contract title")
    contract_type: str = Field(default="Vendor/Service Agreement", description="Type of contract")
    parties: List[ExtractedField] = Field(default_factory=list, description="Parties bound by contract")
    effective_date: ExtractedField = Field(description="Contract effective or start date")
    expiration_date: ExtractedField = Field(description="Contract expiration or end date")
    renewal_terms: ExtractedField = Field(description="Automatic renewal terms and notice requirements")
    payment_terms: ExtractedField = Field(description="Payment terms, billing schedules, and currency")
    termination_conditions: ExtractedField = Field(description="Termination for convenience or breach clauses")
    governing_law: ExtractedField = Field(description="Governing jurisdiction and state law")
    executive_summary: str = Field(default="", description="Executive summary of the agreement")


class Obligation(BaseModel):
    id: Optional[int] = None
    contract_id: str
    party_responsible: str = Field(description="Party responsible for the obligation")
    obligation_text: str = Field(description="Detailed description of the obligation requirement")
    deadline: str = Field(default="Not specified", description="Deadline date or recurring cadence")
    deadline_type: str = Field(default="Fixed Date", description="Fixed Date, Recurring, Event-triggered, or None")
    frequency: str = Field(default="One-time", description="One-time, Monthly, Quarterly, Annually, etc.")
    source_page: int = Field(default=1, description="Page number of the clause")
    clause_text: str = Field(default="", description="Original clause reference text")
    status: str = Field(default="Upcoming", description="Upcoming, Due Soon, Overdue, No Deadline, Completed")


class RiskItem(BaseModel):
    id: Optional[int] = None
    contract_id: str
    risk_title: str = Field(description="Short title of the identified risk")
    severity: str = Field(description="High, Medium, or Low")
    reason: str = Field(description="Detailed explanation of why this clause presents a business risk")
    source_page: int = Field(default=1, description="Page number of the high-risk clause")
    clause_text: str = Field(default="", description="Verbatim text snippet of the risky clause")
    action_recommended: str = Field(description="Actionable human review recommendation for business stakeholders")


class TimelineEvent(BaseModel):
    id: Optional[int] = None
    contract_id: str
    event_title: str = Field(description="Short description of event or milestone")
    party: str = Field(default="General", description="Party involved")
    date_str: str = Field(description="Date formatted as YYYY-MM-DD or descriptive text")
    event_type: str = Field(description="Expiration, Renewal, Payment, Notice, Obligation, or Milestone")
    source_page: int = Field(default=1, description="Page number where date is specified")
    alert_level: str = Field(default="Upcoming", description="Overdue, Due within 30 days, or Upcoming")


class ComparisonItem(BaseModel):
    clause_name: str = Field(description="Name or title of section/clause being compared")
    v1_text: str = Field(description="Text in Version 1")
    v2_text: str = Field(description="Text in Version 2")
    change_type: str = Field(description="Added, Removed, or Modified")
    business_impact: str = Field(description="AI explanation of business impact and operational effect")
    source_page: str = Field(default="N/A", description="Page citation in document")


class ContractSummary(BaseModel):
    executive_summary: str
    parties_summary: str
    period_summary: str
    payment_summary: str
    obligations_summary: str
    renewal_summary: str
    termination_summary: str
    risks_summary: str
    deadlines_summary: str
