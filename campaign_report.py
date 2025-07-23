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

# Add src directory to path for dynamic imports
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

# Import the main processor
try:
    from src import CampaignProcessor
except ImportError as e:
    print(f"Error importing CampaignProcessor: {e}")
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
        logging.FileHandler('logs/campaign_report.log'),
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
  python campaign_report.py                          # Standard run with OpenAI (1000 member limit, 12 months back)
  python campaign_report.py --no-openai              # Preview mode without OpenAI calls
  python campaign_report.py --member-limit 500       # Query only 500 CampaignMembers (faster)
  python campaign_report.py --member-limit 0         # Query all CampaignMembers (unlimited)
  python campaign_report.py --months-back 6          # Look back only 6 months for campaign members
  python campaign_report.py --no-cache               # Force fresh data extraction
  python campaign_report.py --clear-cache            # Clear cache and exit
  python campaign_report.py --batch-size 5           # Process 5 campaigns per batch
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
    parser.add_argument('--member-limit', type=int, default=1000,
                        help='Maximum number of CampaignMembers to query for performance control (default: 1000, use 0 for unlimited)')
    parser.add_argument('--months-back', type=int, default=12,
                        help='Number of months to look back for campaign members (default: 12)')
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
    
    print("🚀 SFDC Campaign Clarity - AI Campaign Analysis")
    print("=" * 55)
    print(f"Target Campaigns: Campaigns with members from last {args.months_back} months")
    print(f"Member Limit: {'Unlimited' if args.member_limit == 0 else args.member_limit}")
    print(f"OpenAI Processing: {'Enabled' if not args.no_openai else 'Disabled (Preview Mode)'}")
    print(f"Batch Size: {args.batch_size}")
    print(f"Cache Mode: {'Enabled' if not args.no_cache else 'Disabled (Fresh extraction)'}")
    print()

    # Initialize processor
    try:
        print("🔧 Initializing components...")
        processor = CampaignProcessor(
            use_openai=not args.no_openai,
            output_directory=args.output_dir
        )
        
        # Show cache info if available
        cache_info = processor.get_cache_info()
        if cache_info:
            print(f"📦 Cache info: {cache_info['total_campaigns']} campaigns, "
                  f"{cache_info['days_old']} days old, "
                  f"member limit: {cache_info.get('member_limit_str', 'unknown')}, "
                  f"months back: {cache_info.get('months_back', 12)}")
        print()
        
        # Run the processor
        result = processor.run(
            use_cache=not args.no_cache,
            batch_size=args.batch_size,
            member_limit=args.member_limit,
            months_back=args.months_back
        )
        
        if not result:
            print("\n⚠️  No campaigns were processed")
            
    except Exception as e:
        logging.error(f"Process failed: {e}")
        print(f"\n❌ Process failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 