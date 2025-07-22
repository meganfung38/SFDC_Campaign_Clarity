"""
Single Campaign Description Generator

This script generates an AI description for a specific campaign by ID.
Perfect for testing or generating descriptions for individual campaigns.
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

# Import required components
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
        logging.FileHandler('logs/single_campaign_report.log'),
        logging.StreamHandler()
    ]
)


def find_campaign_by_id(salesforce_client, campaign_id: str):
    """Find campaign by ID (15 or 18 character Salesforce ID)"""
    try:
        # Validate Salesforce ID format
        if not campaign_id or len(campaign_id) not in [15, 18]:
            raise ValueError("Campaign ID must be 15 or 18 characters long")
        
        # Query for specific campaign by ID
        search_query = f"""
        SELECT BMID__c, Channel__c, Description, Id, Integrated_Marketing__c, 
               Intended_Country__c, Intended_Product__c, Marketing_Message__c, 
               Name, Non_Attributable__c, Program__c, Short_Description_for_Sales__c, 
               Sub_Channel__c, Sub_Channel_Detail__c, TCP_Campaign__c, 
               TCP_Program__c, TCP_Theme__c, Territory__c, Type, Vendor__c, 
               Vertical__c, IsActive
        FROM Campaign 
        WHERE Id = '{campaign_id}'
        """
        
        results = salesforce_client.sf.query_all(search_query)
        
        if not results['records']:
            return None
        
        return results['records'][0]
            
    except Exception as e:
        logging.error(f"Error searching for campaign: {e}")
        raise


def generate_single_description(campaign, use_openai=True):
    """Generate description for a single campaign"""
    try:
        context_manager = ContextManager()
        
        # Convert to pandas Series for compatibility
        import pandas as pd
        campaign_series = pd.Series(campaign)
        
        if not use_openai:
            # Preview mode - just show the enriched context
            enriched_context = context_manager.enrich_campaign_context(campaign_series)
            return f"PREVIEW MODE - Enriched Context:\n{enriched_context}", "preview"
        
        # Generate AI description
        openai_client = OpenAIClient(use_openai=True)
        enriched_context = context_manager.enrich_campaign_context(campaign_series)
        
        description, prompt_type = openai_client.generate_description(
            campaign_series, enriched_context
        )
        
        return description, prompt_type
        
    except Exception as e:
        logging.error(f"Error generating description: {e}")
        return f"Error generating description: {e}", "error"


def main():
    """Main entry point for single campaign description generator"""
    parser = argparse.ArgumentParser(
        description='Generate AI description for a specific campaign',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python single_campaign_report.py "0013600000XYZ123"
  python single_campaign_report.py "0013600000XYZ123456" --no-openai
  python single_campaign_report.py "0013600000ABC789"
        """
    )
    
    parser.add_argument('campaign_id', 
                        help='Campaign ID (15 or 18 character Salesforce ID)')
    parser.add_argument('--no-openai', action='store_true', 
                        help='Preview mode - show enriched context without OpenAI call')
    
    args = parser.parse_args()
    
    # Check for required environment variables
    required_vars = ['SF_USERNAME', 'SF_PASSWORD', 'SF_SECURITY_TOKEN']
    if not args.no_openai:
        required_vars.append('OPENAI_API_KEY')
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file and ensure all required variables are set.")
        return 1
    
    try:
        # Initialize Salesforce client
        print(f"🔍 Searching for campaign: '{args.campaign_id}'")
        salesforce_client = SalesforceClient()
        
        # Find campaign
        campaign = find_campaign_by_id(salesforce_client, args.campaign_id)
        
        if not campaign:
            print(f"❌ No campaign found with ID: '{args.campaign_id}'")
            print("   Please verify the campaign ID is correct and exists in Salesforce")
            return 1
        
        # Display campaign info
        print(f"\n✅ Found campaign: '{campaign['Name']}'")
        print(f"   ID: {campaign['Id']}")
        print(f"   Channel: {campaign.get('Channel__c', 'N/A')}")
        print(f"   Type: {campaign.get('Type', 'N/A')}")
        print(f"   Status: {'Active' if campaign.get('IsActive', False) else 'Inactive'}")
        
        # Generate description
        print(f"\n🤖 Generating description...")
        mode = "Preview mode" if args.no_openai else "AI generation"
        print(f"   Mode: {mode}")
        
        description, prompt_type = generate_single_description(campaign, use_openai=not args.no_openai)
        
        # Display results
        print(f"\n📝 Results:")
        print(f"   Prompt Type: {prompt_type}")
        print(f"\n" + "="*80)
        print(description)
        print("="*80)
        
        # Save to file
        filename = f"single_campaign_{campaign['Id']}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"Campaign: {campaign['Name']}\n")
            f.write(f"ID: {campaign['Id']}\n")
            f.write(f"Prompt Type: {prompt_type}\n")
            f.write(f"Generated: {mode}\n")
            f.write("\n" + "="*50 + "\n")
            f.write(description)
        
        print(f"\n💾 Results saved to: {filename}")
        
    except Exception as e:
        logging.error(f"Single campaign process failed: {e}")
        print(f"\n❌ Process failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 