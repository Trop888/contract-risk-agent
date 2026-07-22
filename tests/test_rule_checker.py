from agents.rule_checker import RuleCheckAgent
from core.model import RiskLevel


def _run(text: str):
    """跑一遍规则预筛，返回风险项列表。"""
    return RuleCheckAgent().run(text)


def _types(items):
    """取出所有命中的风险类型，方便断言。"""
    return {item.risk_type for item in items}


def test_命中无限责任_高风险():
    items = _run("乙方须对一切损失承担无限责任，赔偿金额不设上限。约定仲裁解决争议，违约责任另行约定。")
    hit = [i for i in items if i.risk_type == "无限责任"]
    assert len(hit) == 1
    assert hit[0].level == RiskLevel.HIGH
    assert hit[0].source == "规则引擎"          # 来源必须标成规则引擎
    assert "无限责任" in (hit[0].clause or "")   # clause 应截取到原文片段


def test_命中单方解除权():
    items = _run("甲方有权随时解除本合同，无需承担责任。合同争议由仲裁解决，违约金按约定执行。")
    assert "单方解除权" in _types(items)


def test_命中不合理违约金_中风险():
    items = _run("任何一方违约需向对方双倍赔偿。争议提交仲裁，违约责任如前。")
    hit = [i for i in items if i.risk_type == "不合理违约金"]
    assert len(hit) == 1
    assert hit[0].level == RiskLevel.MEDIUM


def test_缺失争议解决条款():
    # 文本里完全没有 仲裁/诉讼/管辖/争议解决，应命中"缺失争议解决条款"
    items = _run("甲方向乙方支付货款，乙方按期交付货物。若违约需支付违约金。")
    assert "缺失争议解决条款" in _types(items)


def test_有争议解决条款则不报缺失():
    items = _run("双方约定发生争议提交北京仲裁委员会仲裁。违约责任按约定承担。")
    assert "缺失争议解决条款" not in _types(items)


def test_干净合同不误报命中式风险():
    text = "甲乙双方友好协商，按期交付、按期付款。发生争议提交仲裁解决，违约责任依约承担。"
    items = _run(text)
    命中式 = {"无限责任", "单方解除权", "不合理违约金", "自动续约风险"}
    assert not (_types(items) & 命中式)   # 不应命中任何命中式规则


def test_所有规则项来源均为规则引擎():
    items = _run("承担无限责任，甲方有权随时解除，双倍赔偿，自动续约。")
    assert all(item.source == "规则引擎" for item in items)


def test_结果可复现():
    text = "乙方承担无限责任，甲方有权随时解除本合同。"
    first = _types(_run(text))
    second = _types(_run(text))
    assert first == second   # 纯确定性逻辑，两次结果必须完全一致