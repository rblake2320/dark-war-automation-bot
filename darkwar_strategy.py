from dataclasses import dataclass

SAFE = {"claim_free_reward", "collect_completed_queue", "start_idle_research", "start_idle_training", "start_gate_prerequisite"}

@dataclass(frozen=True)
class Decision:
    action: str
    expected: str
    risk: str = "none"

def choose(state: dict) -> Decision:
    if state.get("purchase_modal") or state.get("confidence", 1) < .8:
        return Decision("stop", "no state change", "blocked")
    if state.get("free_rewards"):
        return Decision("claim_free_reward", "reward badge decreases")
    if state.get("completed_queue"):
        return Decision("collect_completed_queue", "queue clears")
    if not state.get("research_active"):
        return Decision("start_idle_research", "research timer appears")
    if not state.get("training_active"):
        return Decision("start_idle_training", "training timer appears")
    if state.get("gate_prerequisite"):
        return Decision("start_gate_prerequisite", "build timer appears")
    return Decision("wait", "next timer or event changes")
