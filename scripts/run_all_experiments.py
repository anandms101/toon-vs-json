#!/usr/bin/env python3
"""
Orchestrate all experiments: conversion, token counting, cost analysis, and LLM testing.
Generates summary report and updates experiments.md.
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime


def run_script(script_path, description):
    """
    Run a Python script as a subprocess and return success status.
    
    Args:
        script_path: Path to the Python script to run
        description: Human-readable description of what the script does
        
    Returns:
        True if script ran successfully, False otherwise
    """
    print(f"\n{'=' * 80}")
    print(f"STEP: {description}")
    print(f"{'=' * 80}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_path.parent.parent,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path.name}:")
        print(e.stdout)
        print(e.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def generate_summary_report(results_dir):
    """Generate a summary report from all experiment results."""
    results_path = Path(results_dir)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {}
    }
    
    # Read token counts
    token_counts_file = results_path / "token_counts.json"
    if token_counts_file.exists():
        with open(token_counts_file, 'r') as f:
            token_data = json.load(f)
        
        # Calculate average reductions
        openai_reductions = []
        anthropic_reductions = []
        
        for dataset_name, counts in token_data.items():
            if 'reduction' in counts:
                openai_reductions.append(counts['reduction']['openai_percent'])
                if counts['reduction']['anthropic_percent']:
                    anthropic_reductions.append(counts['reduction']['anthropic_percent'])
        
        avg_openai_reduction = sum(openai_reductions) / len(openai_reductions) if openai_reductions else 0
        avg_anthropic_reduction = sum(anthropic_reductions) / len(anthropic_reductions) if anthropic_reductions else 0
        
        report['summary']['token_reduction'] = {
            'average_openai_percent': round(avg_openai_reduction, 2),
            'average_anthropic_percent': round(avg_anthropic_reduction, 2) if anthropic_reductions else None,
            'datasets_analyzed': len(token_data)
        }
    
    # Read cost analysis
    cost_analysis_file = results_path / "cost_analysis.json"
    if cost_analysis_file.exists():
        with open(cost_analysis_file, 'r') as f:
            cost_data = json.load(f)
        
        report['summary']['cost_analysis'] = {
            'models_analyzed': len(cost_data.get('models', {})),
            'projections_available': 'projections' in cost_data
        }
    
    # Read performance results
    performance_file = results_path / "performance_results.json"
    if performance_file.exists():
        with open(performance_file, 'r') as f:
            perf_data = json.load(f)
        
        # Count tasks from first dataset if available
        tasks_count = 0
        if perf_data.get('tests'):
            first_dataset = list(perf_data['tests'].values())[0]
            tasks_count = len(first_dataset.get('tasks', {}))
        
        report['summary']['performance_tests'] = {
            'datasets_tested': len(perf_data.get('tests', {})),
            'tasks_per_dataset': tasks_count
        }
    
    return report


def update_experiments_md(experiments_file, summary_report, results_dir):
    """Update experiments.md with latest results."""
    experiments_path = Path(experiments_file)
    results_path = Path(results_dir)
    
    if not experiments_path.exists():
        print(f"Warning: {experiments_file} not found, skipping update")
        return
    
    # Read current experiments.md
    with open(experiments_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Generate results section
    results_section = "\n## Results\n\n"
    results_section += f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    
    # Token Counts
    token_counts_file = results_path / "token_counts.json"
    if token_counts_file.exists():
        with open(token_counts_file, 'r') as f:
            token_data = json.load(f)
        
        results_section += "### Token Counts\n\n"
        results_section += "| Dataset | JSON (OpenAI) | Toon (OpenAI) | Reduction |\n"
        results_section += "|---------|---------------|---------------|----------|\n"
        
        for dataset_name, counts in token_data.items():
            json_tokens = counts['json']['openai_tokens']
            toon_tokens = counts['toon']['openai_tokens']
            reduction = counts['reduction']['openai_percent']
            results_section += f"| {dataset_name} | {json_tokens:,} | {toon_tokens:,} | {reduction:.2f}% |\n"
        
        results_section += "\n"
    
    # Cost Analysis Summary
    cost_analysis_file = results_path / "cost_analysis.json"
    if cost_analysis_file.exists():
        results_section += "### Cost Analysis\n\n"
        results_section += "*See `results/cost_analysis.json` for detailed cost breakdowns and annual projections.*\n\n"
    
    # Performance Results
    performance_file = results_path / "performance_results.json"
    if performance_file.exists():
        results_section += "### Performance Results\n\n"
        results_section += "*See `results/performance_results.json` for detailed LLM performance comparisons.*\n\n"
    
    # Replace or append results section
    if "## Results" in content:
        # Replace existing results section
        lines = content.split('\n')
        new_lines = []
        skip_until_observations = False
        
        for line in lines:
            if line.strip() == "## Results":
                skip_until_observations = True
                new_lines.append(results_section.strip())
            elif skip_until_observations and line.startswith("##"):
                skip_until_observations = False
                new_lines.append(line)
            elif not skip_until_observations:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
    else:
        # Append results section before Observations
        if "## Observations" in content:
            content = content.replace("## Observations", results_section + "## Observations")
        else:
            content += "\n" + results_section
    
    # Write updated content
    with open(experiments_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated {experiments_file} with latest results")


def main():
    """Main entry point - run all experiments in sequence."""
    project_root = Path(__file__).parent.parent
    scripts_dir = project_root / "scripts"
    results_dir = project_root / "results"
    experiments_file = project_root / "experiments.md"
    
    print("=" * 80)
    print("TOON VS JSON LLM EXPERIMENTS")
    print("=" * 80)
    print(f"Starting experiments at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    steps = [
        (scripts_dir / "convert_to_toon.py", "Convert JSON files to Toon format"),
        (scripts_dir / "count_tokens.py", "Count tokens for JSON and Toon formats"),
        (scripts_dir / "cost_calculator.py", "Calculate cost differences"),
    ]
    
    # Optional: LLM comparison (requires API keys and consumes credits)
    # Ask user if they want to run LLM performance tests
    # These tests make actual API calls and will cost money
    run_llm_tests = input("\nRun LLM performance tests? (requires API keys, consumes credits) [y/N]: ").strip().lower() == 'y'
    
    if run_llm_tests:
        steps.append((scripts_dir / "llm_comparison.py", "Test LLM performance with both formats"))
    
    # Run all steps
    success_count = 0
    for script_path, description in steps:
        if run_script(script_path, description):
            success_count += 1
        else:
            print(f"\n⚠ Warning: {description} failed, but continuing...")
    
    print(f"\n{'=' * 80}")
    print(f"EXPERIMENTS COMPLETE")
    print(f"{'=' * 80}\n")
    print(f"Completed {success_count}/{len(steps)} steps successfully")
    
    # Generate summary report
    print("\nGenerating summary report...")
    summary_report = generate_summary_report(results_dir)
    
    summary_file = results_dir / "summary_report.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_report, f, indent=2)
    
    print(f"✓ Summary report saved to {summary_file}")
    
    # Update experiments.md
    print("\nUpdating experiments.md...")
    update_experiments_md(experiments_file, summary_report, results_dir)
    
    print("\n" + "=" * 80)
    print("All experiments completed!")
    print("=" * 80)
    print(f"\nResults are available in:")
    print(f"  - {results_dir / 'token_counts.json'}")
    print(f"  - {results_dir / 'cost_analysis.json'}")
    if run_llm_tests:
        print(f"  - {results_dir / 'performance_results.json'}")
    print(f"  - {results_dir / 'summary_report.json'}")
    print(f"  - {experiments_file}")


if __name__ == "__main__":
    main()

