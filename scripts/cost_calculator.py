#!/usr/bin/env python3
"""
Calculate and compare costs for OpenAI and Anthropic APIs.
Uses current pricing for GPT-4, GPT-3.5-turbo, Claude 3 Opus/Sonnet.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


# Pricing per 1M tokens (as of 2024)
# These prices are based on official pricing pages from OpenAI and Anthropic
# Update these values if pricing changes in the future
# Format: price in USD per 1 million tokens
PRICING = {
    'openai': {
        'gpt-4': {
            'input': 30.00,  # $30 per 1M input tokens
            'output': 60.00   # $60 per 1M output tokens
        },
        'gpt-4-turbo': {
            'input': 10.00,  # $10 per 1M input tokens
            'output': 30.00  # $30 per 1M output tokens
        },
        'gpt-3.5-turbo': {
            'input': 0.50,   # $0.50 per 1M input tokens
            'output': 1.50   # $1.50 per 1M output tokens
        }
    },
    'anthropic': {
        'claude-3-opus': {
            'input': 15.00,  # $15 per 1M input tokens
            'output': 75.00  # $75 per 1M output tokens
        },
        'claude-3-sonnet': {
            'input': 3.00,   # $3 per 1M input tokens
            'output': 15.00 # $15 per 1M output tokens
        },
        'claude-3-haiku': {
            'input': 0.25,   # $0.25 per 1M input tokens
            'output': 1.25   # $1.25 per 1M output tokens
        }
    }
}


def calculate_cost(tokens, price_per_million):
    """
    Calculate the cost for a given number of tokens.
    
    Args:
        tokens: Number of tokens
        price_per_million: Price per 1 million tokens in USD
        
    Returns:
        Cost in USD
    """
    return (tokens / 1_000_000) * price_per_million


def calculate_savings(json_tokens, toon_tokens, price_per_million):
    """Calculate cost savings from using Toon format."""
    json_cost = calculate_cost(json_tokens, price_per_million)
    toon_cost = calculate_cost(toon_tokens, price_per_million)
    savings = json_cost - toon_cost
    savings_percent = (savings / json_cost * 100) if json_cost > 0 else 0
    return {
        'json_cost': json_cost,
        'toon_cost': toon_cost,
        'savings': savings,
        'savings_percent': savings_percent
    }


def analyze_token_counts(token_counts_file):
    """Analyze token counts and calculate costs."""
    with open(token_counts_file, 'r', encoding='utf-8') as f:
        token_data = json.load(f)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'models': {},
        'datasets': {},
        'summary': {}
    }
    
    # Analyze each model
    for provider, models in PRICING.items():
        results['models'][provider] = {}
        
        for model_name, pricing in models.items():
            model_results = {
                'input_pricing': pricing['input'],
                'output_pricing': pricing['output'],
                'datasets': {}
            }
            
            total_json_input = 0
            total_toon_input = 0
            total_json_output = 0
            total_toon_output = 0
            
            # Calculate costs for each dataset
            for dataset_name, counts in token_data.items():
                json_tokens = counts['json']['openai_tokens']  # Using OpenAI tokenizer as baseline
                toon_tokens = counts['toon']['openai_tokens']
                
                # Assume output tokens are 50% of input tokens (typical for responses)
                json_output_tokens = int(json_tokens * 0.5)
                toon_output_tokens = int(toon_tokens * 0.5)
                
                input_costs = calculate_savings(json_tokens, toon_tokens, pricing['input'])
                output_costs = calculate_savings(json_output_tokens, toon_output_tokens, pricing['output'])
                
                total_cost_json = input_costs['json_cost'] + output_costs['json_cost']
                total_cost_toon = input_costs['toon_cost'] + output_costs['toon_cost']
                total_savings = input_costs['savings'] + output_costs['savings']
                
                model_results['datasets'][dataset_name] = {
                    'input': input_costs,
                    'output': output_costs,
                    'total': {
                        'json_cost': total_cost_json,
                        'toon_cost': total_cost_toon,
                        'savings': total_savings,
                        'savings_percent': (total_savings / total_cost_json * 100) if total_cost_json > 0 else 0
                    }
                }
                
                total_json_input += json_tokens
                total_toon_input += toon_tokens
                total_json_output += json_output_tokens
                total_toon_output += toon_output_tokens
            
            # Calculate totals
            total_input_costs = calculate_savings(total_json_input, total_toon_input, pricing['input'])
            total_output_costs = calculate_savings(total_json_output, total_toon_output, pricing['output'])
            
            model_results['totals'] = {
                'input': total_input_costs,
                'output': total_output_costs,
                'combined': {
                    'json_cost': total_input_costs['json_cost'] + total_output_costs['json_cost'],
                    'toon_cost': total_input_costs['toon_cost'] + total_output_costs['toon_cost'],
                    'savings': total_input_costs['savings'] + total_output_costs['savings'],
                    'savings_percent': ((total_input_costs['savings'] + total_output_costs['savings']) / 
                                      (total_input_costs['json_cost'] + total_output_costs['json_cost']) * 100) 
                                     if (total_input_costs['json_cost'] + total_output_costs['json_cost']) > 0 else 0
                }
            }
            
            results['models'][provider][model_name] = model_results
    
    # Project annual savings for different usage scenarios
    scenarios = {
        'low': 1_000_000,      # 1M tokens per month
        'medium': 10_000_000,  # 10M tokens per month
        'high': 100_000_000,   # 100M tokens per month
        'enterprise': 1_000_000_000  # 1B tokens per month
    }
    
    results['projections'] = {}
    for provider, models in PRICING.items():
        results['projections'][provider] = {}
        for model_name, pricing in models.items():
            # Get average reduction percentage from token counts
            avg_reduction = 0
            count = 0
            for dataset_name, counts in token_data.items():
                reduction = counts['reduction']['openai_percent']
                if reduction:
                    avg_reduction += reduction
                    count += 1
            avg_reduction = avg_reduction / count if count > 0 else 0
            
            model_projections = {}
            for scenario_name, monthly_tokens in scenarios.items():
                monthly_json_cost = calculate_cost(monthly_tokens, pricing['input'] + pricing['output'])
                monthly_toon_tokens = monthly_tokens * (1 - avg_reduction / 100)
                monthly_toon_cost = calculate_cost(monthly_toon_tokens, pricing['input'] + pricing['output'])
                monthly_savings = monthly_json_cost - monthly_toon_cost
                annual_savings = monthly_savings * 12
                
                model_projections[scenario_name] = {
                    'monthly_tokens': monthly_tokens,
                    'monthly_json_cost': monthly_json_cost,
                    'monthly_toon_cost': monthly_toon_cost,
                    'monthly_savings': monthly_savings,
                    'annual_savings': annual_savings,
                    'reduction_percent': avg_reduction
                }
            
            results['projections'][provider][model_name] = model_projections
    
    return results


def print_summary(results):
    """Print a human-readable summary of cost analysis."""
    print("=" * 80)
    print("COST ANALYSIS SUMMARY")
    print("=" * 80)
    print()
    
    for provider, models in results['models'].items():
        print(f"{provider.upper()} Models:")
        print("-" * 80)
        
        for model_name, model_data in models.items():
            totals = model_data['totals']['combined']
            print(f"\n{model_name}:")
            print(f"  Total Cost (JSON): ${totals['json_cost']:.4f}")
            print(f"  Total Cost (Toon): ${totals['toon_cost']:.4f}")
            print(f"  Savings: ${totals['savings']:.4f} ({totals['savings_percent']:.2f}%)")
        
        print()
    
    print("=" * 80)
    print("ANNUAL SAVINGS PROJECTIONS")
    print("=" * 80)
    print()
    
    for provider, models in results['projections'].items():
        print(f"{provider.upper()} Models:")
        print("-" * 80)
        
        for model_name, scenarios in models.items():
            print(f"\n{model_name}:")
            for scenario_name, data in scenarios.items():
                print(f"  {scenario_name.capitalize()} usage ({data['monthly_tokens']:,} tokens/month):")
                print(f"    Annual Savings: ${data['annual_savings']:,.2f}")
                print(f"    Reduction: {data['reduction_percent']:.2f}%")
            print()


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    results_dir = project_root / "results"
    token_counts_file = results_dir / "token_counts.json"
    
    # Allow custom file path via command line
    if len(sys.argv) > 1:
        token_counts_file = Path(sys.argv[1])
    
    if not token_counts_file.exists():
        print(f"Error: Token counts file not found: {token_counts_file}")
        print("Run count_tokens.py first to generate token counts.")
        sys.exit(1)
    
    print("Calculating costs...")
    print()
    
    results = analyze_token_counts(token_counts_file)
    
    # Save results
    output_file = results_dir / "cost_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"✓ Cost analysis saved to {output_file}")
    print()
    
    # Print summary
    print_summary(results)


if __name__ == "__main__":
    main()

