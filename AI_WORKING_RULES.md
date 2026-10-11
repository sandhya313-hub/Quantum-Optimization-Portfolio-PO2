# AI Working Rules --- PS-O2

You assist with an existing team project; you are not authorized to
redesign it or independently change requirements.

## Authority order

1.  Official `Problem_Statment_Details.pdf` and organizer
    clarifications.
2.  `TEAM_IMPLEMENTATION_PLAN.md`.
3.  Team-approved `INTERFACES.md`, configuration and tests.
4.  General technical knowledge only if consistent.

If sources conflict, stop and explain the conflict. Do not guess.

## Fixed scope

-   PS-O2 constrained portfolio optimization.
-   Returns `[5, 3, 4, 2]`; risk aversion `lambda = 2`; budget penalty
    `A = 20`; exactly `k = 2`.
-   Objective:
    `maximize r.T @ x - 2 * x.T @ Sigma @ x - 20 * (sum(x) - 2)**2`.
-   Binary variables; QAOA baseline `p = 1`.
-   Phase 1 compares Processor A and B only.
-   The common official risk matrix is pending. Never fabricate it or
    call a custom-matrix result official.
-   Processor C and custom Processor D are outside Phase 1.

## Before coding

1.  Read the plan, interfaces, relevant files and tests.
2.  State your understanding and identify files to modify.
3.  Identify assumptions, missing data and integration risks.
4.  Implement only the assigned task.

## Do not

-   Change the objective, parameter meanings, budget, processor scope or
    shared interfaces without approval.
-   Invent official inputs or measurements.
-   Create a competing objective evaluator.
-   Replace QAOA or add unrelated features without approval.
-   Change dependencies silently.
-   Modify another member's files without coordination.
-   Claim tests passed unless actually executed.
-   Rewrite the whole project to fix a local bug.

## Required response for coding tasks

Provide task understanding, unchanged interfaces, files modified,
implementation, tests and exact commands, tests actually run,
integration risks, and unresolved questions. AI suggestions are
proposals. If a detail is missing or conflicts with the approved plan,
ask instead of guessing.
