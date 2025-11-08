# Toon vs JSON LLM Experiments

This project compares Toon (Token-Oriented Object Notation) format against JSON for LLM applications. We measure token reduction, cost savings, and performance differences across OpenAI and Anthropic APIs.

## What This Project Does

When working with large language models, every token costs money. This project tests whether using Toon format instead of JSON can reduce token usage and save costs. We've found that Toon typically reduces tokens by around 20%, which can translate to significant savings at scale.

The experiments cover:
- Token count comparisons between JSON and Toon formats
- Cost calculations for different models and usage levels
- Performance testing with actual LLM API calls (optional)

## Project Structure

```
toon-vs-json/
├── README.md                 # This file
├── experiments.md            # Experiment tracking and results
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variable template
├── LICENSE                   # MIT License
├── datasets/                 # Sample datasets for testing
│   ├── products.json        # E-commerce catalog (100+ products)
│   ├── api_response.json    # Nested API response data
│   ├── users.json           # User profile data (50+ users)
│   └── README.md            # Dataset descriptions
├── scripts/                  # Experiment scripts
│   ├── convert_to_toon.py   # Converts JSON files to Toon format
│   ├── count_tokens.py      # Counts tokens for both formats
│   ├── cost_calculator.py    # Calculates cost differences
│   ├── llm_comparison.py     # Tests LLM performance (requires API keys)
│   └── run_all_experiments.py  # Runs all experiments in sequence
├── results/                  # Generated results
│   ├── token_counts.json
│   ├── cost_analysis.json
│   ├── performance_results.json
│   └── summary_report.json
└── outputs/                  # Converted Toon files
    └── (generated .toon files)
```

## Getting Started

### Prerequisites

You'll need Python 3.8 or higher installed on your system.

### Installation

1. Clone or download this repository

2. Create a virtual environment (recommended to keep dependencies isolated):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (only needed for LLM performance testing):
```bash
cp .env.example .env
```

5. If you want to run LLM performance tests, edit `.env` and add your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

**Important**: API keys are only required for the LLM performance testing script. You can run token counting and cost analysis without any API keys.

- `convert_to_toon.py` - No API keys needed
- `count_tokens.py` - No API keys needed (uses local tiktoken library)
- `cost_calculator.py` - No API keys needed (just does math on token counts)
- `llm_comparison.py` - Requires API keys (makes actual API calls)

Both OpenAI and Anthropic offer free tiers if you want to test the LLM performance script. OpenAI gives new accounts $5 in free credits, and Anthropic offers a free tier with limited requests.

## Running Experiments

### Run Everything

To run all experiments in sequence:

```bash
python scripts/run_all_experiments.py
```

This will:
1. Convert all JSON files in the datasets folder to Toon format
2. Count tokens for both formats
3. Calculate cost differences
4. Ask if you want to run LLM performance tests (requires API keys)

### Run Individual Scripts

You can also run each script separately:

**Convert JSON to Toon:**
```bash
python scripts/convert_to_toon.py
```
This reads all JSON files from `datasets/` and creates corresponding `.toon` files in `outputs/`.

**Count Tokens:**
```bash
python scripts/count_tokens.py
```
Counts tokens using OpenAI's tokenization algorithm (via tiktoken library) and estimates for Anthropic. Results are saved to `results/token_counts.json`.

**Calculate Costs:**
```bash
python scripts/cost_calculator.py
```
Calculates cost differences for various models and usage scenarios. Results are saved to `results/cost_analysis.json`.

**Test LLM Performance:**
```bash
python scripts/llm_comparison.py
```
This script makes actual API calls to OpenAI and Anthropic, so it requires API keys and will consume credits. It tests how well LLMs perform with both formats across different tasks. Results are saved to `results/performance_results.json`.

You can skip this step entirely and still get valuable insights from token counting and cost analysis.

## Datasets

The project includes three sample datasets to test different data structures:

- **products.json**: E-commerce catalog with 100+ products, including nested specifications and shipping information
- **api_response.json**: Complex nested API response structure (simulated GitHub repository data)
- **users.json**: User profile data with 50+ users, including nested preferences and activity metrics

See `datasets/README.md` for more detailed descriptions of each dataset.

## Understanding the Results

All results are saved as JSON files in the `results/` directory:

- `token_counts.json`: Shows token counts for each dataset in both formats, plus reduction percentages
- `cost_analysis.json`: Detailed cost breakdowns for different models and annual savings projections
- `performance_results.json`: LLM response quality and consistency comparisons (if you ran the performance tests)
- `summary_report.json`: High-level summary of all experiments

The `experiments.md` file is automatically updated with the latest results when you run the orchestration script.

## Models Analyzed

The cost calculator includes pricing for:

**OpenAI Models:**
- GPT-4
- GPT-4 Turbo
- GPT-3.5 Turbo

**Anthropic Models:**
- Claude 3 Opus
- Claude 3 Sonnet
- Claude 3 Haiku

Pricing is based on rates as of 2024. If pricing changes, you can update the values in `scripts/cost_calculator.py`.

## What We've Found

Based on our experiments with the included datasets, Toon format typically reduces token usage by 15-23% compared to JSON. This reduction varies slightly depending on the data structure:

- Simple nested objects: around 16% reduction
- Complex nested structures: around 22% reduction
- Arrays with many items: around 20% reduction

At scale, these savings add up. For example, using GPT-4 at enterprise scale (1 billion tokens per month), switching to Toon format could save over $200,000 per year.

## Contributing

Contributions are welcome. You can:
- Add more diverse datasets
- Test additional LLM models
- Improve the analysis scripts
- Report bugs or suggest improvements

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Notes and Limitations

- Token counting for Anthropic uses approximations since we don't have direct access to their tokenizer. Actual tokenization may vary slightly.
- LLM performance tests consume API credits, so use them judiciously
- Results may vary based on model versions and API updates
- Update pricing in `cost_calculator.py` if you notice pricing changes

## Questions?

If you have questions or run into issues, feel free to open an issue or submit a pull request.
