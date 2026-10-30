from __future__ import annotations


_TEAM_NAMES = {
    "home": "阿根廷",
    "away": "法国",
}

_EVENT_SUMMARIES = {
    "foul_committed": "{team}在边线附近犯规，对手获得任意球，防守需要快速重新落位。",
    "free_kick_restart": "{team}准备任意球重启，注意前点争抢和二点球保护。",
    "ball_out_touchline": "比赛在边线附近暂停，{team}将准备重新组织，先观察落位变化。",
    "throw_in_restart": "{team}获得界外球重启，接应点和盯人转换值得关注。",
    "attacking_phase": "{team}正在持续压上进攻，危险等级{danger}，对手需要保持防线紧凑。",
    "pass_into_penalty_area": "{team}把球送入禁区，危险等级{danger}，门前防守和第二落点很关键。",
    "shot_on_target": "{team}完成射正，危险等级{danger}，门前补射和门将处理值得关注。",
    "goalkeeper_save": "{team}门将完成扑救并控制险情，下一步要尽快发动转换。",
}


def summarize_event(event: str, team: str, danger: int, ball_x: int) -> str:
    """Return a factual, compact Chinese input summary for the board-side LLM."""
    team_name = _TEAM_NAMES.get(team, team or "球队")
    template = _EVENT_SUMMARIES.get(
        event,
        "{team}出现{event}，危险等级{danger}，需要观察攻防两端的下一步选择。",
    )
    summary = template.format(team=team_name, event=event or "比赛变化", danger=max(0, min(5, danger)))
    return summary[:64]
