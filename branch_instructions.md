# Branch Instructions

Three Template nodes, one per verdict. Each outputs a fixed string into a
variable named `output`, which the Variable Aggregator merges into a single
`branch_instruction` fed to the report node.

No LLM here -- the branch only needs to swap the generation instruction.

## SKIP Instruction

```
Explain why the original idea should be skipped. Suggest a simpler and more useful alternative only when appropriate. Do not force the idea into a buildable project.
```

## BUILD Instruction

```
Keep the strongest focused version of the original idea and generate a realistic 7-day MVP plan. Limit the MVP to no more than three core features.
```

## IMPROVE Instruction

```
Narrow the idea to one target user, one primary problem, and no more than three MVP features. Move maps, payments, real-time databases, account systems, and medical or legal capabilities to Future Version.
```
