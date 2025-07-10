#!/usr/bin/env python3
"""
SFDC Campaign Clarity - AI-Powered Campaign Description Generator

This script transforms Salesforce marketing campaign data into sales-friendly 
prospect intelligence using OpenAI's GPT models.
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from campaign_processor import CampaignProcessor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/campaign_description_generation.log'),
        logging.StreamHandler()
    ]
)


def main():
    """Main entry point for the campaign description generator"""
    parser = argparse.ArgumentParser(
        description='Generate AI campaign descriptions for Salesforce',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Standard run with OpenAI
  python main.py --no-openai              # Preview mode without OpenAI calls
  python main.py --limit 50               # Process only 50 campaigns
  python main.py --no-cache               # Force fresh data extraction
  python main.py --clear-cache            # Clear cache and exit
  python main.py --batch-size 5           # Process 5 campaigns per batch
        """
    )
    
    parser.add_argument('--no-openai', action='store_true', 
                        help='Run in prompt preview mode without calling OpenAI API')
    parser.add_argument('--batch-size', type=int, default=10,
                        help='Number of campaigns to process in each batch (default: 10)')
    parser.add_argument('--no-cache', action='store_true',
                        help='Force fresh extraction of campaign IDs (ignore cache)')
    parser.add_argument('--clear-cache', action='store_true',
                        help='Clear the campaign ID cache and exit')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of campaigns to process (useful for testing)')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Directory to save output files (default: current directory)')
    
    args = parser.parse_args()
    
    # Handle cache clearing
    if args.clear_cache:
        processor = CampaignProcessor()
        processor.clear_cache()
        print("Campaign ID cache cleared successfully")
        return
    
    # Check for required environment variables
    required_vars = ['SF_USERNAME', 'SF_PASSWORD', 'SF_SECURITY_TOKEN']
    if not args.no_openai:
        required_vars.append('OPENAI_API_KEY')
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file and ensure all required variables are set.")
        return 1
    
    # Initialize processor
    try:
        processor = CampaignProcessor(
            use_openai=not args.no_openai,
            output_directory=args.output_dir
        )
        
        # Show cache info if available
        cache_info = processor.get_cache_info()
        if cache_info:
            print(f"Cache info: {cache_info['total_campaigns']} campaigns, "
                  f"{cache_info['days_old']} days old")
        
        # Run the processor
        result = processor.run(
            use_cache=not args.no_cache,
            limit=args.limit,
            batch_size=args.batch_size
        )
        
        if result:
            print(f"\n✅ Process completed successfully!")
            print(f"📊 Main report saved to: {result}")
        else:
            print("\n⚠️  No campaigns were processed")
            
    except Exception as e:
        logging.error(f"Process failed: {e}")
        print(f"\n❌ Process failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 