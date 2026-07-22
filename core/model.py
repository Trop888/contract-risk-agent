from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class RiskLevel(str,Enum):
    HIGH="高"
    MEDIUM="中"
    LOW="低"

class RiskItem(BaseModel):
    risk_type:str=Field(description="风险类型，如‘金额异常’、‘条款缺失’")
    level:RiskLevel=Field(description="风险等级，如‘高’、‘中’、‘低’")
    description:str=Field(description="风险描述")
    clause:Optional[str]=Field(default=None,description="相关的合同原文条款")
    suggestion:Optional[str]=Field(default=None,description="修改建议")
    legal_basis:Optional[str]=Field(default=None,description="相关法律依据，如《民法典》第五百八十五条")
    
class ContractAnalysisResult(BaseModel):
    is_valid:bool=Field(default=True,description="合同是否有效")
    summary:str=Field(description="合同摘要")
    risk_items:list[RiskItem]=Field(default_factory=list,description="发现的所有风险项")
    overall_risk:RiskLevel=Field(description="整体风险等级")
    overall_conclusion:str=Field(default="",description="总体结论与签署建议")
    contract_text:Optional[str]=Field(default=None,description="合同原文，供问答追溯使用")
    errors:list[str]=Field(default_factory=list,description="分析过程中发生的错误信息，用于故障隔离与降级")