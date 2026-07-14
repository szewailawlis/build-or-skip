# Build or Skip

An AI workflow that tells you whether your product idea is worth building.

Most AI tools encourage you. This one is willing to say no.

**[Try it →](https://udify.app/workflow/XKdySsK4Nt1oD5XH)**

![workflow](assets/workflow.png)

## Why this is a workflow, not a prompt

The first version was a single agent. One large system prompt did everything:
analyze the idea, decide the verdict, propose an MVP, write the launch post.

It was fast to build. It was also unreliable, in four specific ways.

**It was too agreeable.** It returned `BUILD` constantly, including for ideas
that were obviously too large for one person to finish.

**Even when it said IMPROVE, it didn't actually narrow anything.** A pet travel
app came back with a verdict of IMPROVE — and an MVP that still contained hotel
recommendations, maps, emergency vets, route planning, and breed-specific health
advice. The verdict changed. The scope didn't.

**Structured output was unstable.** Boolean fields sometimes came back as empty
strings instead of `true` / `false`. The fix was to drop booleans entirely and
use enums — `REQUIRED / NOT_REQUIRED`, `HIGH / LOW`. A model that has to pick a
*word* is more reliable than one that has to pick a *type*.

**One prompt was doing four jobs.** Extraction, evaluation, decision, and
generation all shared the same context. A bad extraction quietly poisoned the
verdict, and there was no way to tell which step had failed.

v0.2 splits those four jobs into separate nodes, and moves the decision out of
the model entirely into a Code node with fixed thresholds. When something goes
wrong now, I can see *which node* went wrong.

That mattered almost immediately.

## The bug that made this worth building

The first working version of v0.2 told me to build a **daily motivational quote
app**.

```
user_clarity_score:     4
problem_strength_score: 4
mvp_feasibility_score:  5

VERDICT: BUILD
```

The scoring prompt asked whether the problem was *meaningful*. A quote app is
meaningful. It's also frequent. It scored well on every axis I had defined.

Worse — and this is the part that generalizes — **worthless ideas score high on
feasibility, precisely because they're trivial to build.** A quote app has no
external data, no safety risk, three simple features. It sails through. The
scoring was rewarding exactly what it should have killed.

Because the pipeline was split into nodes, I could see this was a *scoring*
failure, not a decision failure. The thresholds were fine. The rubric wasn't.

## The fix

One question, added to the Problem Strength rubric:

> **What does the user do TODAY without this product?**

Motivational quotes → open any free app. Or nothing at all.

```
problem_strength_score: 4 → 2

VERDICT: SKIP
```

Nothing else changed. Same model, same thresholds, same architecture. The model
had been rating *pleasant*. It needed to rate *necessary*.

## How it works

| Node | Role |
| --- | --- |
| **Extract Idea Structure** | LLM turns a vague idea into structured fields — target user, core problem, features, data dependencies, safety risk |
| **Score Idea** | LLM scores three dimensions 1–5, with reasons |
| **Code: Verdict** | **Fixed rules, not the LLM**, produce BUILD / IMPROVE / SKIP |
| **IF/ELSE** | Routes to one of three branches |
| **Branch Instructions** | Each verdict gets a different generation instruction |
| **Variable Aggregator** | Merges the three mutually exclusive branches |
| **Generate Final Report** | Writes the report under branch-specific constraints |

The division of labor is the whole point: **the LLM understands and generates.
Code decides.** Same scores in, same verdict out — every time. The moment I let
the model draw the conclusion, it started flattering me.

## Verdict rules

```python
def main(user_clarity_score, problem_strength_score, mvp_feasibility_score) -> dict:
    user_score        = int(user_clarity_score)
    problem_score     = int(problem_strength_score)
    feasibility_score = int(mvp_feasibility_score)

    if problem_score <= 2:
        verdict = "SKIP"
    elif user_score >= 4 and problem_score >= 4 and feasibility_score >= 4:
        verdict = "BUILD"
    else:
        verdict = "IMPROVE"

    return {"verdict": verdict}
```

Note that feasibility never triggers SKIP. A hard-to-build idea isn't a bad idea
— it's a **scoping** problem, and that's what IMPROVE is for. Only a weak
problem kills an idea.

## What SKIP actually looks like

A tool that says "don't build this" and then hands you a 7-day plan is lying to
you. You'll follow the plan.

So SKIP outputs no MVP, no build plan, no launch post. It stops:

> **Alternative Direction**
>
> No alternative recommended. This problem is already solved well enough by
> existing free options.

This took an explicit override in the report prompt. The 11-section template
creates its own gravity — the model wants to fill the blanks. **Structure is
instruction.**

## Calibration

Thresholds are worthless until you check them against ideas you already have an
opinion about. Four cases, four hits:

| Idea | clarity | problem | feasibility | Verdict |
| --- | --- | --- | --- | --- |
| Changelog → tweet tool for indie devs | 5 | 4 | 4 | **BUILD** |
| Competitor price tracker for small sellers | 4 | 4 | 2 | **IMPROVE** |
| After-school program finder for parents | 4 | 4 | 3 | **IMPROVE** |
| Daily motivational quote app | 3 | 2 | 4 | **SKIP** |

Full reports in [`examples/`](examples/).

Worth noticing: the quote app and the changelog tool have *nearly the same
feasibility score*. Feasibility carries almost no signal on its own. Everything
turns on problem strength.

## Run it

**[Live demo →](https://udify.app/workflow/XKdySsK4Nt1oD5XH)**

Or run your own:

1. Import [`workflow.yml`](workflow.yml) into [Dify](https://dify.ai)
2. Add your OpenAI key
3. Paste an idea

Runs on `gpt-4o-mini`. A full evaluation costs roughly **$0.002**.

## Repo layout

```
workflow.yml          Dify DSL — import this
prompts/              The three LLM prompts, as plain text
code/verdict.py       The decision rules
examples/             Real output for all three verdicts
```

## What I'd change next

- **Score variance.** The thresholds are deterministic, but the *scores* are not
  — the same idea, phrased differently, can move a point. The determinism is
  real at the decision layer, and honest about being absent below it.
- **Problem Strength is doing all the work.** Three dimensions, one of which
  decides almost everything. Either the other two earn their place or they go.
- **SKIP is rare.** By design. But I haven't tested enough genuinely bad ideas to
  know if the rate is right.

## License

MIT
