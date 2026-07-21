from dotenv import load_dotenv
load_dotenv()
from agents.clause_review import ClauseReviewAgent

# 一段示例合同（含违约金过高、押金不退等问题，方便观察检索增强效果）
contract_text = """
房屋租赁合同
甲方（出租方）：张三
乙方（承租方）：李四
1. 乙方租赁甲方位于XX路XX号的房屋，租期一年，月租金5000元。
2. 乙方须缴纳押金10000元，合同到期后押金不予退还。
3. 乙方如提前退租，需一次性支付违约金50000元。
4. 甲方有权随时收回房屋，无需提前通知。
"""

print("=" * 60)
print("正在分析合同（会先检索相关法条，再交给大模型）...")
print("=" * 60)

agent = ClauseReviewAgent()
result = agent.run(contract_text)

# 打印分析结果
print(f"\n【是否有效合同】{result.is_valid}")
print(f"【合同摘要】{result.summary}")
print(f"【整体风险等级】{result.overall_risk.value}")
print(f"\n【发现 {len(result.risk_items)} 项风险】")

for i, item in enumerate(result.risk_items, 1):
    print(f"\n--- 风险 {i} ---")
    print(f"类型：{item.risk_type}")
    print(f"等级：{item.level.value}")
    print(f"描述：{item.description}")
    print(f"相关条款：{item.clause}")
    print(f"修改建议：{item.suggestion}")
    print(f"⚖️ 法律依据：{item.legal_basis}")   # 重点看这行有没有值