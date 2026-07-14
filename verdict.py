"""
Deterministic verdict rules for Build or Skip.

The LLM scores. This decides. Same scores in, same verdict out.

Design note: feasibility never triggers SKIP. A hard-to-build idea is a
scoping problem, not a bad idea -- that is what IMPROVE is for. Only a
weak problem kills an idea.
"""


def main(user_clarity_score, problem_strength_score, mvp_feasibility_score) -> dict:
    user_score = int(user_clarity_score)
    problem_score = int(problem_strength_score)
    feasibility_score = int(mvp_feasibility_score)

    if problem_score <= 2:
        verdict = "SKIP"
    elif user_score >= 4 and problem_score >= 4 and feasibility_score >= 4:
        verdict = "BUILD"
    else:
        verdict = "IMPROVE"

    return {"verdict": verdict}
