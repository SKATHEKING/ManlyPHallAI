# Phase 2: Quality Control & Evaluation Framework

**Status**: Planning  
**Estimated Duration**: 2-3 weeks  
**Objective**: Measure and improve answer quality, reduce hallucination, enable data-driven iteration

---

## Overview

Phase 2 establishes the foundation for continuous quality improvement:

1. Define quality metrics and evaluation framework
2. Create benchmark datasets for measurement
3. Implement hallucination detection
4. Build evaluation dashboard
5. Enable A/B testing for prompt/retrieval improvements
6. Document quality findings

---

## Core Concept: Quality Loop

```
Question → Answer → Evaluation → Metrics → Improvement → Next Version
                         ↑
                  Benchmark Data
```

The goal is to make quality **measurable** and **iterative**.

---

## Deliverables

### 1. Evaluation Metrics & Framework

#### A. Answer Quality Metrics

**Relevance Score** (0-1)
- Does the answer address the question?
- Manual: Humans rate 1-5, convert to 0-1
- Automated: Semantic similarity between question and answer
```python
# Test: For "What is enlightenment?" answer should be relevant
assert relevance_score(question, answer) > 0.7
```

**Factual Correctness** (0-1)
- Is the answer factually accurate based on sources?
- Manual: Expert review against source text
- Automated: Keyword overlap with source passages
```python
def factual_correctness(answer, source_texts):
    # Compare answer facts against source passages
    # Return accuracy score
    pass
```

**Citation Quality** (0-1)
- Are citations accurate and complete?
- All claims backed by sources?
- Proper attribution?
```python
def citation_quality(answer, citations, source_texts):
    # Verify each claim has corresponding citation
    # Check citations are from correct sources
    # Return quality score
    pass
```

**Completeness** (0-1)
- Does answer fully address the question?
- Missing important information?
```python
def completeness(question, answer, expected_topics):
    # Check if answer covers expected topics
    # Return coverage percentage
    pass
```

**Clarity** (0-1)
- Is the answer clear and well-structured?
- Grammatically correct?
- Appropriate length?
```python
def clarity_score(answer):
    # Check readability, grammar, structure
    # Return clarity score
    pass
```

#### B. Retrieval Quality Metrics

**Recall@K** - Did we retrieve the right passages?
```
Recall@5 = (relevant passages in top-5) / (total relevant passages)
```

**Precision@K** - How many retrieved passages were actually relevant?
```
Precision@5 = (relevant passages in top-5) / 5
```

**Mean Reciprocal Rank (MRR)** - How far down is the first relevant passage?
```
MRR = 1 / (rank of first relevant passage)
```

**Normalized Discounted Cumulative Gain (NDCG)** - Ranking quality
```python
def ndcg_score(retrieved_passages, relevant_passages, k=5):
    # Score considering both relevance and rank position
    pass
```

#### C. System Metrics

**Hallucination Rate** - How often does the system make up facts?
```python
def hallucination_detection(answer, source_texts):
    # Check if claims are supported by sources
    # Return hallucination percentage
    pass
```

**Confidence Calibration** - Are confidence scores accurate?
```python
def calibration_score(predicted_confidence, actual_correctness):
    # Compare predicted vs actual accuracy
    # Return calibration score (should be ~1.0)
    pass
```

**Latency** - Speed of different components
```python
retrieval_latency      # Vector search time
generation_latency     # LLM generation time
end_to_end_latency    # Total time
```

---

### 2. Benchmark Dataset

**Create standardized test set** for consistent measurement:

```
tests/data/benchmark/

├── questions.json          # 100 test questions
├── expected_answers.json   # Ground truth answers
├── relevant_sources.json   # Which books answer each Q
└── evaluation_results.jsonl # Results tracking over time
```

#### questions.json Format
```json
[
  {
    "id": "q1",
    "question": "What is the principle of correspondence?",
    "category": "hermetic_principles",
    "expected_sources": ["kybalion.pdf"],
    "difficulty": "medium",
    "expected_topics": [
      "As above so below",
      "Macrocosm and microcosm",
      "Universal principles"
    ]
  },
  ...
]
```

#### Test Dataset Components

**By Difficulty**:
- 30 easy questions (basic facts)
- 50 medium questions (concepts)
- 20 hard questions (reasoning, synthesis)

**By Type**:
- 40 factual questions (who, what, where)
- 40 conceptual questions (why, how)
- 20 reasoning questions (compare, analyze)

**By Source Complexity**:
- 40 answered by single source
- 40 answered by 2-3 sources
- 20 answered by 4+ sources

---

### 3. Evaluation Suite

**Files to Create**:
- `eval/evaluator.py` — Main evaluation engine
- `eval/metrics.py` — Metric calculations
- `eval/hallucination_detector.py` — Detect made-up facts
- `eval/benchmark_runner.py` — Run benchmarks
- `tests/test_evaluation.py` — Test evaluation itself

#### evaluator.py Structure
```python
class Evaluator:
    def __init__(self, benchmark_dataset):
        self.questions = benchmark_dataset
        self.results = []
    
    def evaluate_answer(self, question, answer, sources):
        """Comprehensive answer evaluation"""
        return {
            'relevance': relevance_score(question, answer),
            'correctness': factual_correctness(answer, sources),
            'citations': citation_quality(answer),
            'completeness': completeness(question, answer),
            'hallucination': hallucination_detection(answer, sources),
        }
    
    def evaluate_retrieval(self, query, retrieved, expected):
        """Evaluate retrieval quality"""
        return {
            'recall': recall_at_k(retrieved, expected),
            'precision': precision_at_k(retrieved, expected),
            'mrr': mean_reciprocal_rank(retrieved, expected),
            'ndcg': ndcg_score(retrieved, expected),
        }
    
    def run_benchmark(self):
        """Run full benchmark on all test questions"""
        results = []
        for q in self.questions:
            answer = answer_question(q['question'])
            evaluation = self.evaluate_answer(
                q['question'],
                answer.text,
                answer.sources
            )
            results.append({
                'question_id': q['id'],
                'question': q['question'],
                **evaluation,
            })
        return results
```

#### hallucination_detector.py
```python
class HallucinationDetector:
    def __init__(self, source_texts):
        self.sources = source_texts
        self.embeddings = embed_texts(source_texts)
    
    def detect_hallucinations(self, answer):
        """Find claims not supported by sources"""
        # 1. Extract factual claims from answer
        claims = extract_claims(answer)
        
        # 2. Check each claim against sources
        hallucinated = []
        for claim in claims:
            if not self._is_supported(claim):
                hallucinated.append({
                    'claim': claim,
                    'confidence': hallucination_score(claim, self.sources)
                })
        
        return hallucinated
    
    def _is_supported(self, claim):
        """Check if claim has supporting evidence"""
        # Embed claim
        # Search sources for similar passages
        # If top match < threshold, it's hallucinated
        pass
```

---

### 4. Evaluation Dashboard

**Files to Create**:
- `eval/dashboard.py` — Web dashboard
- `eval/templates/dashboard.html` — Frontend
- `eval/static/charts.js` — Visualization

#### Dashboard Features
```
┌─────────────────────────────────────────┐
│         ManlyPHallAI Evaluation         │
├─────────────────────────────────────────┤
│ Overall Score: 78.5%                    │
├─────────────────────────────────────────┤
│ Metrics (Last 7 Days)                   │
│  Relevance:        82% ↑                │
│  Correctness:      76% ↑                │
│  Citations:        73%                  │
│  Hallucination:     8% ↓ (Good!)        │
│  Latency:         2.3s ↓                │
├─────────────────────────────────────────┤
│ By Category                             │
│  Hermetic:        85% (25/25 Q)         │
│  Philosophy:      72% (15/20 Q)         │
│  Metaphysics:     81% (20/25 Q)         │
├─────────────────────────────────────────┤
│ Trends                                  │
│  ↑ Correctness improving                │
│  ↓ Hallucination decreasing             │
│  → Latency stable                       │
├─────────────────────────────────────────┤
│ Top Issues                              │
│  1. Multi-source questions (65% acc)    │
│  2. Complex reasoning (70% acc)         │
│  3. Long answers truncated              │
└─────────────────────────────────────────┘
```

#### Implementation (FastAPI + React)
```python
@app.get("/api/eval/metrics")
def get_metrics():
    latest = load_latest_benchmark_results()
    return {
        'overall_score': calculate_overall(latest),
        'metrics': {
            'relevance': latest['relevance'].mean(),
            'correctness': latest['correctness'].mean(),
            'hallucination': latest['hallucination'].mean(),
        },
        'trends': calculate_trends(load_all_benchmarks()),
        'by_category': breakdown_by_category(latest),
    }

@app.get("/api/eval/details/{question_id}")
def get_question_details(question_id: str):
    return get_evaluation_result(question_id)
```

---

### 5. Prompt Optimization Toolkit

**Create tools for iterative prompt improvement**:

```python
# eval/prompt_variants.py

prompt_v1 = "Use only provided passages..."
prompt_v2 = "Ground your answer in the sources..."
prompt_v3 = "Answer using ONLY these passages..."

# Test each variant on benchmark
results = {
    'v1': evaluate_prompts(prompt_v1),  # 78.5% accuracy
    'v2': evaluate_prompts(prompt_v2),  # 80.2% accuracy
    'v3': evaluate_prompts(prompt_v3),  # 79.8% accuracy
}

# v2 wins → Update production
```

**Prompt A/B Testing Framework**:
```python
class PromptOptimizer:
    def test_variant(self, prompt_template, questions):
        """Test new prompt on benchmark"""
        results = []
        for q in questions:
            answer = generate_answer(q, prompt=prompt_template)
            eval = evaluate_answer(answer)
            results.append(eval)
        return {
            'accuracy': mean(results),
            'variance': std(results),
            'improvement': (mean - baseline) / baseline
        }
    
    def find_best_prompt(self, variants, questions):
        """Compare multiple prompt variants"""
        results = {}
        for name, prompt in variants.items():
            results[name] = self.test_variant(prompt, questions)
        
        best = max(results.items(), key=lambda x: x[1]['accuracy'])
        return best
```

---

### 6. Iterative Improvement Workflow

**Weekly Improvement Cycle**:

```
┌─ Monday ───────────────────────────────┐
│ 1. Run benchmark (100 questions)       │
│ 2. Analyze results                     │
│ 3. Identify top 3 failure modes        │
└────────────────────────────────────────┘
         ↓
┌─ Tuesday-Wednesday ────────────────────┐
│ 4. Design improvements:                │
│    - Better prompt?                    │
│    - Better retrieval threshold?       │
│    - Better chunk size?                │
│    - Better model?                     │
└────────────────────────────────────────┘
         ↓
┌─ Thursday ─────────────────────────────┐
│ 5. A/B test improvements               │
│ 6. Measure lift vs baseline            │
│ 7. Select best performing version      │
└────────────────────────────────────────┘
         ↓
┌─ Friday ───────────────────────────────┐
│ 8. Deploy winning variant              │
│ 9. Commit to git with metrics          │
│ 10. Document changes & learnings       │
└────────────────────────────────────────┘
```

---

### 7. Documentation

**Files to Create**:
- `EVALUATION_GUIDE.md` — How to run evaluations
- `QUALITY_REPORT.md` — Baseline metrics
- `IMPROVEMENT_LOG.md` — History of changes
- `KNOWN_LIMITATIONS.md` — What still needs work

#### QUALITY_REPORT.md
```markdown
# Phase 2 Quality Baseline Report

**Report Date**: [Date after benchmark run]

## Overall Metrics

| Metric | Score | Target | Status |
|--------|-------|--------|--------|
| Relevance | 82.5% | >85% | 🟡 |
| Correctness | 76.3% | >80% | 🔴 |
| Citations | 88.1% | >90% | 🟡 |
| Hallucination Rate | 12.5% | <10% | 🔴 |

## By Difficulty

| Difficulty | Accuracy | Sample Size |
|-----------|----------|------------|
| Easy | 91% | 30Q |
| Medium | 78% | 50Q |
| Hard | 58% | 20Q |

## By Category

| Category | Accuracy | Issues |
|----------|----------|--------|
| Hermetic Principles | 85% | Multi-source confusion |
| Philosophy | 72% | Complex reasoning |
| Metaphysics | 81% | Context gaps |

## Top Issues

1. **Multi-source questions** (65% accuracy)
   - Impact: 20% of questions
   - Cause: Retrieval returns from wrong book
   - Solution: Implement source weighting

2. **Long answers truncated** (60% accuracy)
   - Impact: 15% of questions
   - Cause: Response exceeds token limit
   - Solution: Implement answer summarization

3. **Hallucinated facts** (12.5% hallucination rate)
   - Impact: Accuracy reduction 5-10%
   - Cause: LLM inventing details
   - Solution: Better prompts, verification layer

## Next Steps

- [ ] Improve multi-source retrieval
- [ ] Implement answer verification
- [ ] Optimize prompts for accuracy
- [ ] Add hallucination detection
```

---

## Implementation Schedule

### Week 1: Metrics & Dataset

**Day 1**: Define metrics framework
- [ ] Create eval/metrics.py with all metric functions
- [ ] Write tests for metric calculations
- [ ] Document metric rationale

**Day 2-3**: Build benchmark dataset
- [ ] Create 100 test questions
- [ ] Identify expected sources
- [ ] Define ground truth answers
- [ ] Verify dataset quality

**Day 4**: Build evaluation engine
- [ ] Create eval/evaluator.py
- [ ] Implement comprehensive evaluation
- [ ] Test on sample data

**Day 5**: Run baseline benchmark
- [ ] Run full benchmark on 100 questions
- [ ] Analyze results
- [ ] Document findings
- [ ] Create QUALITY_REPORT.md

### Week 2: Hallucination & Optimization

**Day 1-2**: Hallucination detection
- [ ] Create eval/hallucination_detector.py
- [ ] Test on known hallucinations
- [ ] Measure false positive/negative rates
- [ ] Integrate into evaluation

**Day 3**: Prompt optimization
- [ ] Design 3-5 prompt variants
- [ ] A/B test variants
- [ ] Measure improvements
- [ ] Deploy best variant

**Day 4-5**: Retrieval tuning
- [ ] Experiment with thresholds
- [ ] Test different k values
- [ ] Measure recall/precision impact
- [ ] Deploy best configuration

### Week 3: Dashboard & Documentation

**Day 1-2**: Build dashboard
- [ ] Create eval/dashboard.py
- [ ] Build frontend (React or simple HTML)
- [ ] Integrate metrics visualization
- [ ] Deploy dashboard

**Day 3**: Documentation
- [ ] Write EVALUATION_GUIDE.md
- [ ] Write IMPROVEMENT_LOG.md
- [ ] Document all learnings
- [ ] Update README with quality info

**Day 4-5**: Final tuning & commit
- [ ] Run final benchmark
- [ ] Commit all changes
- [ ] Push to git
- [ ] Prepare for Phase 3

---

## Success Criteria

### ✅ Metrics
- [ ] All metrics defined and tested
- [ ] Baseline measurements recorded
- [ ] Target thresholds set for each metric

### ✅ Dataset
- [ ] 100 test questions created
- [ ] Sources identified for each
- [ ] Dataset covers all difficulty levels

### ✅ Evaluation
- [ ] Evaluation runs successfully
- [ ] Results saved and tracked
- [ ] Dashboard displays metrics

### ✅ Quality Improvements
- [ ] Hallucination detection working
- [ ] At least 2 prompts tested and ranked
- [ ] Improvement documented

### ✅ Documentation
- [ ] EVALUATION_GUIDE.md complete
- [ ] QUALITY_REPORT.md published
- [ ] All changes documented

---

## Key Insights Expected

After Phase 2, you should understand:

1. **Current Quality Baseline** — Where we stand
2. **Main Failure Modes** — What breaks most often
3. **Improvement Opportunities** — Quick wins available
4. **Quality-Speed Tradeoff** — Can we optimize latency too?
5. **Data Needs** — Do we need more/better source material?
6. **Model Suitability** — Is llama2:7b good enough?

---

## Metrics Tracking Template

```yaml
# IMPROVEMENT_LOG.md

## Week 1: Baseline
- Relevance: 82.5%
- Correctness: 76.3%
- Hallucination: 12.5%
- Change: Baseline (no improvement yet)

## Week 2: Prompt V2
- Relevance: 83.2% (+0.7%)
- Correctness: 78.1% (+1.8%)  ← Improvement!
- Hallucination: 11.2% (-1.3%) ← Better!
- Change: Deployed prompt variant 2

## Week 3: Retrieval Tuning
- Relevance: 84.5% (+1.3%)
- Correctness: 79.4% (+1.3%)
- Hallucination: 10.8% (-0.4%)
- Change: Threshold 0.3 → 0.25, K 5 → 7
```

---

## Deliverables Checklist

### Code
- [ ] eval/metrics.py (200+ lines)
- [ ] eval/evaluator.py (300+ lines)
- [ ] eval/hallucination_detector.py (150+ lines)
- [ ] eval/benchmark_runner.py (100+ lines)
- [ ] eval/dashboard.py (200+ lines)
- [ ] tests/data/benchmark/questions.json (100 Qs)

### Documentation
- [ ] EVALUATION_GUIDE.md
- [ ] QUALITY_REPORT.md (with baseline metrics)
- [ ] IMPROVEMENT_LOG.md
- [ ] KNOWN_LIMITATIONS.md

### Results
- [ ] Baseline metrics recorded
- [ ] Hallucination detection working
- [ ] Improvement identified and implemented
- [ ] Dashboard deployed

---

## Dependencies on Other Phases

- Requires Phase 1e: API & Discord Bot (for testing)
- May inform Phase 1f: Performance targets
- Feeds into Phase 3: Web search evaluation

---

**Phase 2 Status**: Planning — Ready to begin implementation after Phase 1f
