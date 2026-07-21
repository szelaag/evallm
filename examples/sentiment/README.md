# Sentiment classification example

Demonstrates evallm on a sentiment classification task, split into three
suites by difficulty: `basic` (clear sentiment), `edge_cases` (mixed or
factual signals), and `sarcasm` (irony).

Run it:

```bash
cd examples/sentiment
evallm run evallm.yaml -r
```

The report shows per-suite accuracy and confusion matrices — a good look at
where a model starts to struggle as inputs get harder.