"""Non-interactive driver for the task-2 (security-sensitive reuse) rollout.
Equivalent to choosing '3 -> run all', enable_mcp=y, include_code=N in
safety_evaluation.py's interactive main(), but scriptable for background runs."""
import urllib3; urllib3.disable_warnings()
from safety_evaluation import SafetyRollout
if __name__ == "__main__":
    rollout = SafetyRollout(enable_mcp_matching=True, include_mcp_code=False)
    rollout.run_all_tests()  # all 25 user_queries
