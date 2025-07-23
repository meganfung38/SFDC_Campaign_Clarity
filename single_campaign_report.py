#!/usr/bin/env python3
"""
SFDC Campaign Clarity - Single Campaign Analysis

This script analyzes a single Salesforce campaign by ID and generates
AI-powered sales-friendly descriptions using the same pipeline as the main tool.
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from typing import Optional

# Add src directory to path for dynamic imports
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

# Import the required components
try:
    from src.salesforce_client import SalesforceClient
    from src.openai_client import OpenAIClient
    from src.context_manager import ContextManager
except ImportError as e:
    print(f"Error importing components: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Source directory: {src_dir}")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/single_campaign.log'),
        logging.StreamHandler()
    ]
)


def validate_campaign_id(campaign_id: str) -> str:
    """Validate Salesforce campaign ID format
    
    Args:
        campaign_id: Campaign ID to validate
        
    Returns:
        Valid campaign ID
        
    Raises:
        ValueError: If campaign ID format is invalid
    """
    if not campaign_id:
        raise ValueError("Campaign ID cannot be empty")
    
    # Remove any extra whitespace
    campaign_id = campaign_id.strip()
    
    # Salesforce IDs are either 15 or 18 characters
    if len(campaign_id) not in [15, 18]:
        raise ValueError(f"Invalid campaign ID length: {len(campaign_id)}. Must be 15 or 18 characters.")
    
    # Basic format check (alphanumeric)
    if not campaign_id.isalnum():
        raise ValueError("Campaign ID must contain only alphanumeric characters")
    
    return campaign_id


def process_single_campaign(campaign_id: str, use_openai: bool = True) -> dict:
    """Process a single campaign and generate AI description
    
    Args:
        campaign_id: Salesforce campaign ID
        use_openai: Whether to use OpenAI for description generation
        
    Returns:
        Dictionary with campaign data and AI description
    """
    try:
        # Initialize components
        salesforce_client = SalesforceClient()
        openai_client = OpenAIClient(use_openai=use_openai)
        context_manager = ContextManager()
        
        print(f"📋 Analyzing campaign: {campaign_id}")
        logging.info(f"Processing single campaign: {campaign_id}")
        
        # Extract campaign data
        df = salesforce_client.extract_campaigns([campaign_id])
        
        if df.empty:
            raise ValueError(f"No campaign found with ID: {campaign_id}")
        
        campaign = df.iloc[0]
        print(f"✅ Found campaign: {campaign.get('Name', 'Unknown')}")
        
        # Generate enriched context
        context = context_manager.enrich_campaign_context(campaign)
        print(f"📝 Generated context ({len(context)} characters)")
        
        # Generate AI description
        if use_openai:
            print("🤖 Generating AI description...")
            description, prompt = openai_client.generate_description(campaign, context)
            print(f"✅ AI description generated ({len(description)} characters)")
        else:
            print("⚠️  Running in preview mode (no OpenAI)")
            description = "Preview mode - no AI description generated"
            prompt = "Preview mode - no prompt generated"
        
        # Prepare results
        result = {
            'campaign_data': campaign.to_dict(),
            'enriched_context': context,
            'ai_prompt': prompt,
            'ai_description': description,
            'processing_mode': 'AI Generated' if use_openai else 'Preview Mode'
        }
        
        return result
        
    except Exception as e:
        logging.error(f"Failed to process campaign {campaign_id}: {e}")
        raise


def display_results(result: dict, campaign_id: str):
    """Display campaign analysis results
    
    Args:
        result: Processing results dictionary
        campaign_id: Campaign ID
    """
    campaign = result['campaign_data']
    
    print("\n" + "="*80)
    print(f"📊 CAMPAIGN ANALYSIS RESULTS")
    print("="*80)
    
    print(f"\n📋 Campaign Details:")
    print(f"  ID: {campaign_id}")
    print(f"  Name: {campaign.get('Name', 'N/A')}")
    print(f"  Channel: {campaign.get('Channel__c', 'N/A')}")
    print(f"  Type: {campaign.get('Type', 'N/A')}")
    print(f"  Description: {campaign.get('Description', 'N/A')}")
    
    if campaign.get('Program__c'):
        print(f"  Program: {campaign.get('Program__c')}")
    if campaign.get('Sub_Channel__c'):
        print(f"  Sub-Channel: {campaign.get('Sub_Channel__c')}")
    
    print(f"\n📝 Enriched Context ({len(result['enriched_context'])} characters):")
    print("-" * 40)
    print(result['enriched_context'])
    
    if result['processing_mode'] == 'AI Generated':
        print(f"\n🤖 AI Sales Description:")
        print("-" * 40)
        print(result['ai_description'])
    else:
        print(f"\n⚠️  Preview Mode - No AI description generated")
        print("    Use without --no-openai flag to generate AI descriptions")
    
    print("\n" + "="*80)


def save_results(result: dict, campaign_id: str, output_dir: Optional[str] = None):
    """Save results to a text file
    
    Args:
        result: Processing results dictionary
        campaign_id: Campaign ID
        output_dir: Output directory (defaults to current directory)
    """
    try:
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = Path('.')
        
        filename = f"single_campaign_{campaign_id}.txt"
        filepath = output_path / filename
        
        campaign = result['campaign_data']
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("SFDC Campaign Clarity - Single Campaign Analysis\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Campaign ID: {campaign_id}\n")
            f.write(f"Campaign Name: {campaign.get('Name', 'N/A')}\n")
            f.write(f"Channel: {campaign.get('Channel__c', 'N/A')}\n")
            f.write(f"Type: {campaign.get('Type', 'N/A')}\n")
            f.write(f"Processing Mode: {result['processing_mode']}\n")
            f.write(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("ENRICHED CONTEXT:\n")
            f.write("-" * 30 + "\n")
            f.write(result['enriched_context'] + "\n\n")
            
            if result['processing_mode'] == 'AI Generated':
                f.write("AI SALES DESCRIPTION:\n")
                f.write("-" * 30 + "\n")
                f.write(result['ai_description'] + "\n\n")
                
                f.write("AI SYSTEM PROMPT USED:\n")
                f.write("-" * 30 + "\n")
                f.write(result['ai_prompt'] + "\n")
        
        print(f"💾 Results saved to: {filepath}")
        return filepath
        
    except Exception as e:
        logging.error(f"Failed to save results: {e}")
        print(f"⚠️  Could not save results: {e}")
        return None


def main():
    """Main entry point for single campaign analysis"""
    parser = argparse.ArgumentParser(
        description='Analyze a single Salesforce campaign and generate AI descriptions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python single_campaign_report.py "0013600000XYZ123"
    python single_campaign_report.py "0013600000XYZ123456" --no-openai
    python single_campaign_report.py "0013600000ABC789" --output-dir ./analysis
    python single_campaign_report.py "0013600000XYZ123" --months-back 6  # Use 6-month lookback
        """
    )
    
    parser.add_argument('campaign_id', help='Salesforce campaign ID (15 or 18 characters)')
    parser.add_argument('--no-openai', action='store_true', help='Preview mode without AI generation')
    parser.add_argument('--months-back', type=int, default=12,
                        help='Number of months to look back for campaign members (default: 12, used for member count validation)')
    parser.add_argument('--output-dir', help='Directory to save output file')
    parser.add_argument('--no-save', action='store_true', help='Do not save results to file')
    
    args = parser.parse_args()
    
    try:
        # Validate campaign ID
        campaign_id = validate_campaign_id(args.campaign_id)
        
        print("🚀 SFDC Campaign Clarity - Single Campaign Analysis")
        print("=" * 60)
        print(f"Campaign ID: {campaign_id}")
        print(f"Mode: {'Preview (no AI)' if args.no_openai else 'AI Generation'}")
        if args.output_dir:
            print(f"Output Directory: {args.output_dir}")
        print("=" * 60)
        
        # Process the campaign
        result = process_single_campaign(campaign_id, use_openai=not args.no_openai)
        
        # Display results
        display_results(result, campaign_id)
        
        # Save results unless --no-save is specified
        if not args.no_save:
            save_results(result, campaign_id, args.output_dir)
        
        print("\n✅ Single campaign analysis completed successfully!")
        logging.info(f"Single campaign analysis completed for: {campaign_id}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logging.error(f"Single campaign analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 