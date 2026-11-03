> **Submission record: rejected at EMNLP.** The note below describes the current revision, not the submitted version. Updated November 3, 2026.

## The question: should every failure be taken at face value?

When a model retries the same problem, it leaves both useful derivations and recurring mistakes. Putting that experience back into the prompt can help the next attempt, but “seeing a reminder” does not mean the model will follow it.

A quieter issue is that **a failed solution may still contain a correct strategy.** Treating the whole trace as negative experience and suppressing similar thoughts can block the path to the right answer. RG-CTO therefore asks: how can experience shape generation directly, while limiting the damage of wrong negative experience?

## Method: positive guidance, plus selective negative suppression

CTO lets the same frozen model score the next token under two conditions. The positive branch uses helpful experience. The negative branch is steered along a suspected-wrong line of thought, exposing generation tendencies tied to failure. Both branches share the same generated prefix, and only one continuation is sampled.

![Figure 1. RG-CTO: estimate the reliability of negative experience, then filter items and scale the contrastive branch.](../assets/figures/rgcto-method.png)

RG-CTO first checks each negative item with three signals:

- **Support:** do earlier traces support this pattern? Recurrence is only a clue; it does not prove the pattern is wrong.
- **Relevance:** is it related to the current problem and to the positive experience?
- **Conflict risk:** if we suppress it, might we also hurt valid reasoning supported by positive experience?

Low-reliability items are filtered. The mean reliability of the remaining items then sets how strongly the negative branch acts in this round. If no suitable negative experience remains, the method falls back to positive guidance. **Model parameters are never updated. Reliability is estimated per problem and per round, not retuned at every token.**

## Results: reliability control reduces misuse of experience

On the current revision's HMMT24 + Qwen3-4B-Thinking setup, mean Pass@1 after the third guided round is **59.7%** for RSE, **62.5%** for CTO, and **66.7%** for RG-CTO. Relative to RSE, which puts experience into the prompt, this is a **7.0 point** gain.

![Figure 2. Method comparison and cumulative ablation on HMMT24, Qwen3-4B, Iter3, averaged over three seeds.](../assets/figures/rgcto-results.png)

The main comparison generates 32 traces per problem per round, covering Iter0–Iter3. In the cumulative ablation, adding support, relevance, conflict estimation, and filtering in order raises the score from **62.5%** to **66.7%**. These are sequential gains, not independent module contributions. The right-hand axis is zoomed to make the differences visible.

The revision also extends to math, QA, code generation, and planning, covering 12 benchmark–model settings. RG-CTO attains the highest mean among the compared methods at Iter3 in these settings. Mean comparisons do not automatically imply that every difference is statistically significant.

## Implications and limits

Experience reuse should ask not only “which experiences were found,” but also “how much influence those experiences deserve.” Negative experience especially needs careful weighting.

Reliability estimates still come from the model, not from an independent proof of correctness, and dual-branch decoding adds inference cost. The work therefore supports **more controlled use of experience**, not a free improvement or the removal of bad experience.

*Based on the 2026-11-02 revision* Reliability-Gated Contrastive Trajectory Optimization for Test-Time Experience Reuse. *EMNLP rejection status provided by the author. Code: [RG-CTO](https://github.com/ZijunSong/RG-CTO).*
