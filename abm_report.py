#!/usr/bin/env python3
"""
ABM Campaign Report Generator

This script generates a focused report of Account-Based Marketing campaigns
for channel leaders to review ABM campaign effectiveness and strategy.
"""

import sys
import os
import argparse
import logging
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta
from collections import Counter
from typing import List, Dict, Optional

# Add src directory to path for dynamic imports
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

# Import required components
try:
    from src.salesforce_client import SalesforceClient
    from src.openai_client import OpenAIClient
    from src.context_manager import ContextManager
    from src.excel_operations import ExcelReportGenerator
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
        logging.FileHandler('logs/abm_campaign_report.log'),
        logging.StreamHandler()
    ]
)


def extract_abm_campaign_members(salesforce_client, months_back: int = 12, limit: int = 500) -> tuple[List[str], Dict[str, int], int]:
    """Extract ABM campaign IDs from members created in last N months
    
    Args:
        salesforce_client: Salesforce client instance
        months_back: Number of months to look back for campaign members
        limit: Maximum number of campaign members to retrieve
        
    Returns:
        Tuple of (campaign_ids, member_counts, total_campaigns_queried)
    """
    try:
        # Calculate date N months ago
        months_ago = (datetime.now() - timedelta(days=months_back * 30)).strftime('%Y-%m-%dT%H:%M:%S.000+0000')
        
        # Query campaign members with ABM filtering
        member_query = f"""
        SELECT CampaignId
        FROM CampaignMember 
        WHERE CreatedDate > {months_ago}
        AND CampaignId IN (
            SELECT Id FROM Campaign WHERE (
                TCP_Program__c LIKE '%ABM%' OR
                Sub_Channel_Detail__c IN ('Target Accounts', 'POD - ABM', 'CXO', 'Field Event - CXO') OR
                TCP_Theme__c IN ('Top Target Acquisition', 'Top Target Expansion') OR
                (Channel__c IN ('Appointment Setting', 'Corporate Events', 'Field Events') AND
                 (Sub_Channel_Detail__c LIKE '%1:1%' OR Sub_Channel_Detail__c LIKE '%CXO%' OR 
                  Sub_Channel_Detail__c LIKE '%Target%')) OR
                (Channel__c = 'Upsell' AND 
                 Sub_Channel_Detail__c IN ('Upsell - 1:1', 'Upsell - 1:Few')) OR
                (Type IN ('Dinner/Lunch', 'Meetings') AND 
                 Sub_Channel_Detail__c LIKE '%CXO%')
            ) AND IsActive = true
        )
        LIMIT {limit}
        """
        
        logging.info(f"Fetching ABM campaign members from the last {months_back} months...")
        member_results = salesforce_client.sf.query_all(member_query)
        
        # Store total campaigns queried
        total_campaigns_queried = member_results.get('totalSize', 0)
        
        # Process results to get unique campaign IDs
        campaign_member_list = [record['CampaignId'] for record in member_results['records']]
        
        if not campaign_member_list:
            logging.warning(f"No ABM campaigns with members found in the last {months_back} months")
            return [], {}, total_campaigns_queried
        
        # Calculate member counts per campaign
        member_counts = Counter(campaign_member_list)
        campaign_ids = list(member_counts.keys())
        
        logging.info(f"Found {len(campaign_ids)} unique ABM campaigns with {len(campaign_member_list)} total members")
        logging.info(f"Total ABM campaigns queried: {total_campaigns_queried}")
        return campaign_ids, dict(member_counts), total_campaigns_queried
        
    except Exception as e:
        logging.error(f"Failed to extract ABM campaign members: {e}")
        raise


def classify_abm_type(campaign: pd.Series) -> str:
    """Classify the type of ABM campaign based on its characteristics
    
    Args:
        campaign: Campaign data as pandas Series
        
    Returns:
        ABM classification string
    """
    tcp_program = str(campaign.get('TCP_Program__c', '')).strip()
    sub_detail = str(campaign.get('Sub_Channel_Detail__c', '')).strip()
    tcp_theme = str(campaign.get('TCP_Theme__c', '')).strip()
    channel = str(campaign.get('Channel__c', '')).strip()
    
    # Explicit ABM programs
    if 'ABM' in tcp_program:
        return 'Explicit ABM Program'
    
    # Strategic account targeting
    if sub_detail in ['Target Accounts', 'POD - ABM']:
        return 'Strategic Account Targeting'
    
    # Executive targeting
    if 'CXO' in sub_detail:
        return 'Executive/C-Suite Targeting'
    
    # High-value themes
    if tcp_theme in ['Top Target Acquisition', 'Top Target Expansion']:
        return 'Strategic Account Acquisition/Expansion'
    
    # Personalized upsell
    if channel == 'Upsell' and ('1:1' in sub_detail or '1:Few' in sub_detail):
        return 'Personalized Account Expansion'
    
    # High-touch events
    if channel in ['Corporate Events', 'Field Events'] and any(term in sub_detail.lower() for term in ['target', 'cxo', '1:']):
        return 'High-Touch Event Targeting'
    
    return 'ABM-Aligned Campaign'


def process_abm_campaigns(salesforce_client, openai_client, context_manager, campaigns_df, batch_size: int = 5) -> pd.DataFrame:
    """Process campaigns to generate AI descriptions
    
    Args:
        salesforce_client: Salesforce client
        openai_client: OpenAI client
        context_manager: Context manager
        campaigns_df: DataFrame with campaign data
        batch_size: Number of campaigns to process in each batch
        
    Returns:
        DataFrame with AI descriptions added
    """
    try:
        logging.info(f"Processing {len(campaigns_df)} ABM campaigns in batches of {batch_size}...")
        
        # Process campaigns in batches
        processed_batches = []
        total_batches = (len(campaigns_df) + batch_size - 1) // batch_size
        
        for i in range(0, len(campaigns_df), batch_size):
            batch_num = (i // batch_size) + 1
            batch = campaigns_df.iloc[i:i+batch_size].copy()
            
            logging.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} campaigns)...")
            
            # Process each campaign in the batch
            batch_results = []
            for _, campaign in batch.iterrows():
                try:
                    enriched_context = context_manager.enrich_campaign_context(campaign)
                    description, prompt_type = openai_client.generate_description(campaign, enriched_context)
                    
                    campaign_result = campaign.copy()
                    campaign_result['AI_Sales_Description'] = description
                    campaign_result['AI_Prompt'] = prompt_type
                    batch_results.append(campaign_result)
                    
                except Exception as e:
                    logging.error(f"Error processing campaign {campaign.get('Name', 'Unknown')}: {e}")
                    campaign_result = campaign.copy()
                    campaign_result['AI_Sales_Description'] = f"Error generating description: {e}"
                    campaign_result['AI_Prompt'] = "error"
                    batch_results.append(campaign_result)
            
            batch_df = pd.DataFrame(batch_results)
            processed_batches.append(batch_df)
            
            logging.info(f"Completed batch {batch_num}/{total_batches}")
        
        # Combine all batches
        result_df = pd.concat(processed_batches, ignore_index=True)
        logging.info(f"Successfully processed all {len(result_df)} ABM campaigns")
        
        return result_df
        
    except Exception as e:
        logging.error(f"Failed to process ABM campaigns: {e}")
        raise


def main():
    """Main entry point for the ABM campaign report generator"""
    parser = argparse.ArgumentParser(
        description='Generate ABM campaign report for marketing channel leaders',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ABM Campaign Identification Criteria:
  • Explicit ABM Programs (TCP_Program__c contains 'ABM')
  • Strategic Account Targeting (Target Accounts, POD - ABM)  
  • Executive/C-Suite Targeting (CXO-related campaigns)
  • High-Value Strategic Themes (Top Target Acquisition/Expansion)
  • Personalized Account Expansion (1:1, 1:Few upsell campaigns)
  • High-Touch Event Targeting (Strategic events, executive dinners)

Examples:
  python abm_report.py                    # Generate 15 ABM campaigns report
  python abm_report.py --limit 20         # Generate 20 ABM campaigns
  python abm_report.py --months-back 18   # Look back 18 months for more campaigns
  python abm_report.py --no-openai        # Preview mode without AI descriptions
  python abm_report.py --batch-size 3     # Process 3 campaigns per batch
        """
    )
    
    parser.add_argument('--no-openai', action='store_true', 
                        help='Run in preview mode without calling OpenAI API')
    parser.add_argument('--limit', type=int, default=15,
                        help='Number of ABM campaigns to process (default: 15)')
    parser.add_argument('--batch-size', type=int, default=5,
                        help='Number of campaigns to process in each batch (default: 5)')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Directory to save ABM report (default: current directory)')
    parser.add_argument('--months-back', type=int, default=12,
                        help='Number of months to look back for campaign members (default: 12)')
    
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
    
    print("🎯 ABM Campaign Report Generator")
    print("=" * 50)
    print(f"Target ABM Campaigns: {args.limit}")
    print(f"Time Window: {args.months_back} months back")
    print(f"OpenAI Processing: {'Enabled' if not args.no_openai else 'Disabled (Preview Mode)'}")
    print(f"Batch Size: {args.batch_size}")
    print()
    
    try:
        # Initialize components
        print("🔧 Initializing components...")
        salesforce_client = SalesforceClient()
        openai_client = OpenAIClient(use_openai=not args.no_openai)
        context_manager = ContextManager()
        excel_generator = ExcelReportGenerator(output_directory=args.output_dir)
        
        print("🔍 Extracting ABM campaigns based on criteria:")
        print("   • Explicit ABM programs (TCP_Program__c)")
        print("   • Strategic account targeting")
        print("   • Executive/C-suite targeting")
        print("   • High-value strategic themes")
        print("   • Personalized account expansion")
        print("   • High-touch event targeting")
        print()
        
        # Extract ABM campaign members
        campaign_ids, member_counts, total_campaigns_queried = extract_abm_campaign_members(
            salesforce_client, 
            months_back=args.months_back,
            limit=args.limit * 10  # Increased multiplier to get more variety
        )
        
        if not campaign_ids:
            print("\n⚠️  No ABM campaigns were found with recent members")
            print("Consider adjusting criteria or checking campaign data in Salesforce")
            return 1
        
        # Extract campaign details
        logging.info("Extracting campaign details...")
        campaigns_df = salesforce_client.extract_campaigns(campaign_ids)
        
        print(f"📊 Campaign extraction details:")
        print(f"   • Campaign members found: {sum(member_counts.values())}")
        print(f"   • Unique campaigns found: {len(campaign_ids)}")
        print(f"   • Campaigns with full details: {len(campaigns_df)}")
        
        # Add member count and ABM classification
        campaigns_df['Recent_Member_Count'] = campaigns_df['Id'].map(member_counts.get)
        campaigns_df['ABM_Classification'] = campaigns_df.apply(classify_abm_type, axis=1)
        
        # Show all classifications before limiting
        if 'ABM_Classification' in campaigns_df.columns:
            all_classifications = campaigns_df['ABM_Classification'].value_counts()
            print(f"\n📋 All ABM Campaign Types Before Limiting:")
            for classification, count in all_classifications.items():
                print(f"   • {classification}: {count}")
        
        # Limit results
        if args.limit and args.limit > 0:
            print(f"\n🎯 Limiting to {args.limit} campaigns...")
            campaigns_df = campaigns_df.head(args.limit)
        
        print(f"✅ Found {len(campaigns_df)} ABM campaigns for processing")
        
        # Show ABM classification breakdown
        if 'ABM_Classification' in campaigns_df.columns:
            classification_counts = campaigns_df['ABM_Classification'].value_counts()
            print(f"\nABM Campaign Types Found:")
            for classification, count in classification_counts.items():
                print(f"  • {classification}: {count}")
        print()
        
        # Process campaigns for AI descriptions
        if not args.no_openai:
            print("🤖 Generating AI descriptions...")
            campaigns_df = process_abm_campaigns(
                salesforce_client, openai_client, context_manager, campaigns_df, args.batch_size
            )
        else:
            print("📋 Preview mode - skipping AI description generation")
            campaigns_df['AI_Sales_Description'] = "Preview mode - AI description not generated"
            campaigns_df['AI_Prompt'] = "preview"
        
        # Create report
        print("📊 Creating ABM report...")
        processing_stats = {
            'total_campaigns_queried': total_campaigns_queried,
            'processing_time': 0,  # Could add timing if needed
        }
        
        report_path = excel_generator.create_campaign_report(
            campaigns_df, 
            use_openai=not args.no_openai,
            processing_stats=processing_stats
        )
        
        # Display results
        print(f"\n✅ ABM Report completed successfully!")
        print(f"📊 ABM report saved to: {report_path}")
        
        # Print summary
        print(f"\nABM Campaign Summary:")
        print(f"Total ABM campaigns processed: {len(campaigns_df)}")
        if 'AI_Sales_Description' in campaigns_df.columns:
            ai_success = campaigns_df['AI_Sales_Description'].notna().sum()
            print(f"ABM campaigns with AI descriptions: {ai_success}")
        
        print(f"\n📋 Report ready for your marketing channel leader meeting!")
        
    except Exception as e:
        logging.error(f"ABM report generation failed: {e}")
        print(f"\n❌ ABM report generation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 