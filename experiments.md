# Toon vs JSON LLM Experiments

## Introduction

This document tracks experiments comparing Toon (Token-Oriented Object Notation) vs JSON for LLM applications. We measure token reduction, cost savings, and performance across OpenAI and Anthropic APIs.

## Hypothesis

Toon format should provide:
- Significant token reduction compared to JSON
- Cost savings in LLM API calls
- Comparable or better performance in LLM tasks

## Methodology

### Datasets
- **products.json**: E-commerce catalog with 100+ products
- **api_response.json**: Nested API response data
- **users.json**: User profile data with 50+ users

### Metrics
- Token count reduction percentage
- Cost per 1M tokens (input/output)
- Response quality and consistency
- Response times

## Results

*Last updated: 2025-11-08 16:33:53*

### Token Counts

| Dataset | JSON (OpenAI) | Toon (OpenAI) | Reduction |
|---------|---------------|---------------|----------|
| users | 22,891 | 17,664 | 22.83% |
| api_response | 3,186 | 2,674 | 16.07% |
| products | 21,909 | 16,988 | 22.46% |

### Cost Analysis

*See `results/cost_analysis.json` for detailed cost breakdowns and annual projections.*
### Token Counts
*Results will be populated after running experiments*

### Cost Analysis
*Results will be populated after running experiments*

### Performance Results
*Results will be populated after running experiments*

## Observations

*Observations will be added as experiments are run*

## Code Snippets

### Running Experiments
```bash
python scripts/run_all_experiments.py
```

### Individual Scripts
```bash
# Convert JSON to Toon
python scripts/convert_to_toon.py

# Count tokens
python scripts/count_tokens.py

# Calculate costs
python scripts/cost_calculator.py

# Test LLM performance
python scripts/llm_comparison.py
```

## Article Draft

*Article sections will be added as insights are gathered*

