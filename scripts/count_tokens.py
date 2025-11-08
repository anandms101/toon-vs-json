#!/usr/bin/env python3
"""
Count tokens for JSON and Toon files.
Uses tiktoken (local library) for OpenAI token counting - NO API CALLS OR KEYS NEEDED.
Uses approximation for Anthropic token counting.
"""

import json
import os
import sys
from pathlib import Path

try:
    import tiktoken
except ImportError:
    print("Error: tiktoken package not installed. Install with: pip install tiktoken")
    sys.exit(1)

try:
    from anthropic import Anthropic
except ImportError:
    print("Warning: anthropic package not installed. Anthropic token counts will be unavailable.")
    Anthropic = None


def count_openai_tokens(text, model="gpt-4"):
    """
    Count tokens using OpenAI's tiktoken library.
    
    This is a local operation - no API calls are made. The tiktoken library
    implements OpenAI's tokenization algorithm locally, so we get accurate
    token counts without needing API keys or making network requests.
    
    Args:
        text: The text string to count tokens for
        model: The OpenAI model name (used to select the correct tokenizer)
        
    Returns:
        Number of tokens in the text according to OpenAI's tokenization
    """
    try:
        # Get the encoding for the specified model
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except KeyError:
        # Fallback to cl100k_base encoding if model not found
        # This is the encoding used by GPT-4 and most recent OpenAI models
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))


def count_anthropic_tokens(text):
    """
    Estimate tokens for Anthropic models.
    
    Note: Anthropic doesn't provide a public tokenizer, so this is an
    approximation. Anthropic's tokenizer is similar to OpenAI's but not
    identical. We use a rough estimate of ~4 characters per token.
    
    Args:
        text: The text string to estimate tokens for
        
    Returns:
        Estimated number of tokens (approximation)
    """
    if Anthropic is None:
        return None
    
    try:
        # Anthropic doesn't have a direct public tokenizer API
        # We use a simple approximation: roughly 4 characters per token
        # This is a rough estimate; actual tokenization may vary
        # For more accuracy, you could use Anthropic's API to count tokens
        # but that would require API calls
        return len(text) // 4
    except Exception as e:
        print(f"Warning: Could not count Anthropic tokens: {e}")
        # Fallback approximation
        return len(text) // 4


def count_file_tokens(file_path):
    """Count tokens in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        openai_tokens = count_openai_tokens(content)
        anthropic_tokens = count_anthropic_tokens(content)
        
        return {
            'openai_tokens': openai_tokens,
            'anthropic_tokens': anthropic_tokens,
            'char_count': len(content)
        }
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def compare_formats(datasets_dir, outputs_dir):
    """Compare token counts between JSON and Toon formats."""
    datasets_path = Path(datasets_dir)
    outputs_path = Path(outputs_dir)
    
    results = {}
    
    # Find all JSON files
    json_files = list(datasets_path.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {datasets_dir}")
        return results
    
    print("Counting tokens for JSON and Toon files...")
    print()
    
    for json_file in json_files:
        filename = json_file.stem
        toon_file = outputs_path / f"{filename}.toon"
        
        if not toon_file.exists():
            print(f"⚠ Warning: {toon_file.name} not found, skipping {filename}")
            continue
        
        json_stats = count_file_tokens(json_file)
        toon_stats = count_file_tokens(toon_file)
        
        if json_stats and toon_stats:
            openai_reduction = ((json_stats['openai_tokens'] - toon_stats['openai_tokens']) / 
                              json_stats['openai_tokens'] * 100) if json_stats['openai_tokens'] > 0 else 0
            anthropic_reduction = ((json_stats['anthropic_tokens'] - toon_stats['anthropic_tokens']) / 
                                  json_stats['anthropic_tokens'] * 100) if json_stats['anthropic_tokens'] and json_stats['anthropic_tokens'] > 0 else 0
            
            results[filename] = {
                'json': {
                    'openai_tokens': json_stats['openai_tokens'],
                    'anthropic_tokens': json_stats['anthropic_tokens'],
                    'char_count': json_stats['char_count']
                },
                'toon': {
                    'openai_tokens': toon_stats['openai_tokens'],
                    'anthropic_tokens': toon_stats['anthropic_tokens'],
                    'char_count': toon_stats['char_count']
                },
                'reduction': {
                    'openai_percent': round(openai_reduction, 2),
                    'anthropic_percent': round(anthropic_reduction, 2) if anthropic_reduction else None,
                    'openai_tokens_saved': json_stats['openai_tokens'] - toon_stats['openai_tokens'],
                    'anthropic_tokens_saved': (json_stats['anthropic_tokens'] - toon_stats['anthropic_tokens']) 
                                             if json_stats['anthropic_tokens'] and toon_stats['anthropic_tokens'] else None
                }
            }
            
            print(f"📊 {filename}:")
            print(f"   JSON - OpenAI: {json_stats['openai_tokens']} tokens, Anthropic: {json_stats['anthropic_tokens']} tokens")
            print(f"   Toon - OpenAI: {toon_stats['openai_tokens']} tokens, Anthropic: {toon_stats['anthropic_tokens']} tokens")
            print(f"   Reduction - OpenAI: {openai_reduction:.2f}%, Anthropic: {anthropic_reduction:.2f}%")
            print()
    
    return results


def save_results(results, output_path):
    """Save token count results to JSON file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"✓ Results saved to {output_file}")


def main():
    """Main entry point."""
    # Get project root directory
    project_root = Path(__file__).parent.parent
    datasets_dir = project_root / "datasets"
    outputs_dir = project_root / "outputs"
    results_dir = project_root / "results"
    
    # Allow custom directories via command line
    if len(sys.argv) > 1:
        datasets_dir = Path(sys.argv[1])
    if len(sys.argv) > 2:
        outputs_dir = Path(sys.argv[2])
    
    results = compare_formats(datasets_dir, outputs_dir)
    
    if results:
        results_file = results_dir / "token_counts.json"
        save_results(results, results_file)
    else:
        print("No results to save.")


if __name__ == "__main__":
    main()

