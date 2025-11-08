#!/usr/bin/env python3
"""
Compare LLM performance with JSON vs Toon formats.
Tests data extraction, summarization, and question answering tasks.
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Install with: pip install openai")
    OpenAI = None

try:
    from anthropic import Anthropic
except ImportError:
    print("Error: anthropic package not installed. Install with: pip install anthropic")
    Anthropic = None


# Test prompts for different LLM tasks
# These prompts test how well LLMs can work with both JSON and Toon formats
# across different types of tasks
TEST_PROMPTS = {
    'data_extraction': "Extract the following information from the data: names, IDs, and key metrics. Format as a structured list.",
    'summarization': "Provide a brief summary of the main information in this data.",
    'question_answering': "Answer the following question based on the data: What are the most important details?",
    'analysis': "Analyze this data and identify the top 3 most significant items or patterns."
}


def read_file(file_path):
    """Read file content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def test_openai(client, prompt, data, model="gpt-3.5-turbo"):
    """
    Test OpenAI API with given prompt and data.
    
    This function makes an actual API call to OpenAI, which requires
    an API key and will consume credits. It measures response time
    and token usage.
    
    Args:
        client: OpenAI client instance (initialized with API key)
        prompt: The task prompt to send to the model
        data: The data (JSON or Toon format) to analyze
        model: The OpenAI model to use (default: gpt-3.5-turbo)
        
    Returns:
        Dictionary with response details, token counts, and timing, or None if client unavailable
    """
    if client is None:
        return None
    
    try:
        start_time = time.time()
        
        # Make API call to OpenAI
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes structured data."},
                {"role": "user", "content": f"{prompt}\n\nData:\n{data}"}
            ],
            temperature=0.7,  # Moderate creativity
            max_tokens=500    # Limit response length
        )
        
        elapsed_time = time.time() - start_time
        
        # Extract response details
        return {
            'response': response.choices[0].message.content,
            'model': model,
            'input_tokens': response.usage.prompt_tokens,
            'output_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens,
            'response_time': elapsed_time,
            'success': True
        }
    except Exception as e:
        return {
            'error': str(e),
            'success': False
        }


def test_anthropic(client, prompt, data, model="claude-3-haiku-20240307"):
    """Test Anthropic API with given prompt and data."""
    if client is None:
        return None
    
    try:
        start_time = time.time()
        
        message = client.messages.create(
            model=model,
            max_tokens=500,
            temperature=0.7,
            messages=[
                {"role": "user", "content": f"{prompt}\n\nData:\n{data}"}
            ]
        )
        
        elapsed_time = time.time() - start_time
        
        return {
            'response': message.content[0].text,
            'model': model,
            'input_tokens': message.usage.input_tokens,
            'output_tokens': message.usage.output_tokens,
            'total_tokens': message.usage.input_tokens + message.usage.output_tokens,
            'response_time': elapsed_time,
            'success': True
        }
    except Exception as e:
        return {
            'error': str(e),
            'success': False
        }


def run_comparison_tests(datasets_dir, outputs_dir, results_dir):
    """Run comparison tests for all datasets."""
    datasets_path = Path(datasets_dir)
    outputs_path = Path(outputs_dir)
    results_path = Path(results_dir)
    results_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize API clients
    openai_client = None
    anthropic_client = None
    
    if OpenAI:
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            openai_client = OpenAI(api_key=openai_api_key)
        else:
            print("Warning: OPENAI_API_KEY not found in environment variables")
    else:
        print("Warning: OpenAI client not available")
    
    if Anthropic:
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_api_key:
            anthropic_client = Anthropic(api_key=anthropic_api_key)
        else:
            print("Warning: ANTHROPIC_API_KEY not found in environment variables")
    else:
        print("Warning: Anthropic client not available")
    
    if not openai_client and not anthropic_client:
        print("Error: No API clients available. Please set API keys in .env file.")
        return None
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }
    
    # Find all JSON files
    json_files = list(datasets_path.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {datasets_dir}")
        return results
    
    print("Running LLM comparison tests...")
    print("This may take a while and will consume API credits.")
    print()
    
    for json_file in json_files:
        filename = json_file.stem
        toon_file = outputs_path / f"{filename}.toon"
        
        if not toon_file.exists():
            print(f"⚠ Warning: {toon_file.name} not found, skipping {filename}")
            continue
        
        print(f"Testing {filename}...")
        
        json_data = read_file(json_file)
        toon_data = read_file(toon_file)
        
        dataset_results = {
            'dataset': filename,
            'tasks': {}
        }
        
        # Test each task type
        for task_name, prompt in TEST_PROMPTS.items():
            print(f"  Task: {task_name}")
            
            task_results = {
                'task': task_name,
                'prompt': prompt,
                'openai': {},
                'anthropic': {}
            }
            
            # Test with OpenAI
            if openai_client:
                print("    Testing with OpenAI (JSON)...")
                json_result = test_openai(openai_client, prompt, json_data)
                if json_result:
                    task_results['openai']['json'] = json_result
                
                print("    Testing with OpenAI (Toon)...")
                toon_result = test_openai(openai_client, prompt, toon_data)
                if toon_result:
                    task_results['openai']['toon'] = toon_result
            
            # Test with Anthropic
            if anthropic_client:
                print("    Testing with Anthropic (JSON)...")
                json_result = test_anthropic(anthropic_client, prompt, json_data)
                if json_result:
                    task_results['anthropic']['json'] = json_result
                
                print("    Testing with Anthropic (Toon)...")
                toon_result = test_anthropic(anthropic_client, prompt, toon_data)
                if toon_result:
                    task_results['anthropic']['toon'] = toon_result
            
            dataset_results['tasks'][task_name] = task_results
        
        results['tests'][filename] = dataset_results
        print()
    
    return results


def save_results(results, output_path):
    """Save test results to JSON file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"✓ Results saved to {output_file}")


def print_summary(results):
    """Print a summary of test results."""
    print("=" * 80)
    print("LLM PERFORMANCE COMPARISON SUMMARY")
    print("=" * 80)
    print()
    
    for dataset_name, dataset_data in results['tests'].items():
        print(f"Dataset: {dataset_name}")
        print("-" * 80)
        
        for task_name, task_data in dataset_data['tasks'].items():
            print(f"\nTask: {task_name}")
            
            # OpenAI comparison
            if 'openai' in task_data and 'json' in task_data['openai'] and 'toon' in task_data['openai']:
                json_result = task_data['openai']['json']
                toon_result = task_data['openai']['toon']
                
                if json_result.get('success') and toon_result.get('success'):
                    print(f"  OpenAI:")
                    print(f"    JSON - Tokens: {json_result['total_tokens']}, Time: {json_result['response_time']:.2f}s")
                    print(f"    Toon - Tokens: {toon_result['total_tokens']}, Time: {toon_result['response_time']:.2f}s")
                    token_savings = json_result['total_tokens'] - toon_result['total_tokens']
                    print(f"    Token Savings: {token_savings} ({token_savings/json_result['total_tokens']*100:.2f}%)")
            
            # Anthropic comparison
            if 'anthropic' in task_data and 'json' in task_data['anthropic'] and 'toon' in task_data['anthropic']:
                json_result = task_data['anthropic']['json']
                toon_result = task_data['anthropic']['toon']
                
                if json_result.get('success') and toon_result.get('success'):
                    print(f"  Anthropic:")
                    print(f"    JSON - Tokens: {json_result['total_tokens']}, Time: {json_result['response_time']:.2f}s")
                    print(f"    Toon - Tokens: {toon_result['total_tokens']}, Time: {toon_result['response_time']:.2f}s")
                    token_savings = json_result['total_tokens'] - toon_result['total_tokens']
                    print(f"    Token Savings: {token_savings} ({token_savings/json_result['total_tokens']*100:.2f}%)")
        
        print()


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    datasets_dir = project_root / "datasets"
    outputs_dir = project_root / "outputs"
    results_dir = project_root / "results"
    
    # Allow custom directories via command line
    if len(sys.argv) > 1:
        datasets_dir = Path(sys.argv[1])
    if len(sys.argv) > 2:
        outputs_dir = Path(sys.argv[2])
    
    results = run_comparison_tests(datasets_dir, outputs_dir, results_dir)
    
    if results:
        results_file = results_dir / "performance_results.json"
        save_results(results, results_file)
        print()
        print_summary(results)
    else:
        print("No results to save.")


if __name__ == "__main__":
    main()

