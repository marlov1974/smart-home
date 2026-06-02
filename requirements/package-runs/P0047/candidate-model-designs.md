# P0047 candidate model designs

Option A, constrained continuous spread regression: useful as a baseline, but weak if rare spikes and regime persistence dominate the target.

Option B, two-stage bottleneck model: recommended next spread-specific design. Stage 1 classifies near-zero/positive/negative/spike regimes; Stage 2 predicts severity for non-zero regimes.

Option C, quantile/risk model: useful companion for high-spread risk and operational guardrails, especially if exact spread magnitude remains noisy.

Option D, direct SE3 model: should be evaluated if spread-specific regime modeling does not clearly beat direct SE3 target learning.

Option E, hybrid: best strategic direction after P0047: direct SE3 or SE1 baseline plus bottleneck risk adjustment/diagnostic.

P0047 recommendation: build a bottleneck/regime diagnostic first, then compare against a direct SE3 AI-1/AI-2 model in the next package. Do not use SE1-to-SE3 anchoring as the next step.
