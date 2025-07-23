import logging
import time
from datetime import datetime
from typing import Optional
import pandas as pd
from salesforce_client import SalesforceClient
from openai_client import OpenAIClient
from context_manager import ContextManager
from cache_manager import CacheManager
from excel_operations import ExcelReportGenerator


class CampaignProcessor:
    """Main orchestrator for campaign description generation"""
    
    def __init__(self, use_openai: bool = True, output_directory: Optional[str] = None):
        """Initialize the campaign processor
        
        Args:
            use_openai: Whether to use OpenAI for description generation
            output_directory: Directory to save output files
        """
        self.use_openai = use_openai
        self.output_directory = output_directory
        self.processing_stats = {}
        
        # Initialize components
        self.salesforce_client = SalesforceClient()
        self.openai_client = OpenAIClient(use_openai=use_openai)
        self.context_manager = ContextManager()
        self.cache_manager = CacheManager()
        self.excel_generator = ExcelReportGenerator(output_directory=output_directory)
        
        logging.info(f"Campaign processor initialized (OpenAI: {use_openai})")
    
    def extract_campaigns(self, use_cache: bool = True, member_limit: int = 1000, months_back: int = 12) -> pd.DataFrame:
        """Extract campaigns with members created in specified timeframe
        
        Args:
            use_cache: Whether to use cached campaign IDs
            member_limit: Maximum number of CampaignMembers to query (for performance)
            months_back: Number of months to look back for campaign members
            
        Returns:
            DataFrame with campaign data
        """
        try:
            # Check if cache is compatible with requested member_limit
            cache_data = None
            use_cached_data = False
            
            if use_cache:
                if self.cache_manager.is_cache_compatible(member_limit, months_back):
                    cache_data = self.cache_manager.load_campaign_cache()
                    if cache_data and 'campaign_ids' in cache_data and 'member_counts' in cache_data:
                        use_cached_data = True
                        cached_limit = cache_data.get('member_limit')
                        cached_months = cache_data.get('months_back', 12)
                        cached_limit_str = "unlimited" if cached_limit == 0 or cached_limit is None else str(cached_limit)
                        requested_limit_str = "unlimited" if member_limit == 0 else str(member_limit)
                        logging.info(f"Using compatible cache (cached: {cached_limit_str}, {cached_months}mo | requested: {requested_limit_str}, {months_back}mo)")
                else:
                    cached_data_info = self.cache_manager.load_campaign_cache()
                    if cached_data_info:
                        cached_limit = cached_data_info.get('member_limit')
                        cached_months = cached_data_info.get('months_back', 12)
                        cached_limit_str = "unlimited" if cached_limit == 0 or cached_limit is None else str(cached_limit)
                        requested_limit_str = "unlimited" if member_limit == 0 else str(member_limit)
                        logging.info(f"Cache exists but incompatible (cached: {cached_limit_str}, {cached_months}mo | requested: {requested_limit_str}, {months_back}mo) - will extract fresh data")
            
            if use_cached_data and cache_data:
                campaign_ids = cache_data['campaign_ids']
                member_counts = cache_data['member_counts']
                total_campaigns_queried = cache_data.get('total_campaigns_queried', len(campaign_ids))
                logging.info(f"Using cached campaign IDs: {len(campaign_ids)} campaigns")
            else:
                # Extract fresh campaign member data
                campaign_ids, member_counts, total_campaigns_queried = self.salesforce_client.extract_campaign_members(months_back=months_back, member_limit=member_limit)
                
                if not campaign_ids:
                    logging.warning(f"No campaigns found with recent members (last {months_back} months)")
                    return pd.DataFrame()
                
                # Save to cache with member_limit and months_back info
                self.cache_manager.save_campaign_cache(campaign_ids, member_counts, total_campaigns_queried, member_limit, months_back)
            
            # Store for reporting
            self.processing_stats['total_campaigns_queried'] = total_campaigns_queried
            
            # Extract campaign details
            df = self.salesforce_client.extract_campaigns(campaign_ids)
            
            print(f"📊 Campaign extraction details:")
            print(f"   • Campaign members found: {sum(member_counts.values())}")
            print(f"   • Unique campaigns found: {len(campaign_ids)}")
            print(f"   • Campaigns with full details: {len(df)}")
            
            # Add member count
            df['Recent_Member_Count'] = df['Id'].map(member_counts.get)
            
            # Show channel breakdown before any limiting
            if 'Channel__c' in df.columns and len(df) > 0:
                channel_counts = df['Channel__c'].value_counts().head(10)
                print(f"\n📋 Top Campaign Channels Found:")
                for channel, count in channel_counts.items():
                    print(f"   • {channel}: {count}")
            
            # Show vertical breakdown if available
            if 'Vertical__c' in df.columns and len(df) > 0:
                vertical_counts = df['Vertical__c'].value_counts().head(5)
                print(f"\n🏢 Top Industry Verticals:")
                for vertical, count in vertical_counts.items():
                    try:
                        if str(vertical).strip():
                            print(f"   • {vertical}: {count}")
                    except (AttributeError, TypeError):
                        continue
            
            logging.info(f"Successfully extracted {len(df)} campaigns")
            return df
            
        except Exception as e:
            logging.error(f"Failed to extract campaigns: {e}")
            raise
    
    def process_campaigns(self, df: pd.DataFrame, batch_size: int = 10) -> pd.DataFrame:
        """Process campaigns to generate AI descriptions
        
        Args:
            df: DataFrame with campaign data
            batch_size: Number of campaigns to process in each batch
            
        Returns:
            DataFrame with AI descriptions added
        """
        start_time = time.time()
        
        result_df = self.openai_client.process_campaigns_batch(
            df, self.context_manager, batch_size=batch_size
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        self.processing_stats['processing_time_minutes'] = round(processing_time / 60, 2)
        
        return result_df
    
    def create_reports(self, df: pd.DataFrame) -> str:
        """Create Excel report with campaign descriptions and summary
        
        Args:
            df: DataFrame with processed campaign data
            
        Returns:
            Path to the created report
        """
        # Enhanced processing stats
        processing_stats = {
            'total_members': df['Recent_Member_Count'].sum() if 'Recent_Member_Count' in df.columns else 0,
            'total_campaigns_queried': self.processing_stats.get('total_campaigns_queried', 'N/A'),
            'processing_time_minutes': self.processing_stats.get('processing_time_minutes', 'N/A')
        }
        
        # Create comprehensive report with summary included
        report_path = self.excel_generator.create_campaign_report(
            df, use_openai=self.use_openai, processing_stats=processing_stats
        )
        
        return report_path
    
    def clear_cache(self):
        """Clear the campaign cache"""
        self.cache_manager.clear_cache()
    
    def get_cache_info(self) -> Optional[dict]:
        """Get information about the current cache
        
        Returns:
            Dictionary with cache information or None if no cache
        """
        return self.cache_manager.get_cache_info()
    
    def run(self, use_cache: bool = True, batch_size: int = 10, member_limit: int = 1000, months_back: int = 12) -> Optional[str]:
        """Main execution method
        
        Args:
            use_cache: Whether to use cached campaign IDs
            batch_size: Number of campaigns to process in each batch
            member_limit: Maximum number of CampaignMembers to query (for performance, 0 for unlimited)
            months_back: Number of months to look back for campaign members
            
        Returns:
            Path to the main report file
        """
        try:
            # Extract campaigns
            logging.info("Starting campaign extraction...")
            df = self.extract_campaigns(use_cache=use_cache, member_limit=member_limit, months_back=months_back)
            
            if df.empty:
                logging.warning("No campaigns to process")
                return None
            
            print(f"✅ Found {len(df)} campaigns for processing")
            
            # Process campaigns to generate descriptions
            print(f"\n🤖 Generating AI descriptions...")
            logging.info("Generating AI descriptions...")
            df = self.process_campaigns(df, batch_size=batch_size)
            
            # Create reports
            print(f"\n📊 Creating campaign report...")
            main_report_path = self.create_reports(df)
            
            logging.info(f"Process completed successfully!")
            logging.info(f"Main report: {main_report_path}")
            
            # Display results
            print(f"\n✅ Campaign Report completed successfully!")
            print(f"📊 Campaign report saved to: {main_report_path}")
            
            # Print campaign summary
            print(f"\nCampaign Summary:")
            print(f"Total campaigns processed: {len(df)}")
            if 'AI_Sales_Description' in df.columns:
                ai_success = df['AI_Sales_Description'].notna().sum()
                print(f"Campaigns with AI descriptions: {ai_success}")
            
            # Show final channel breakdown
            if 'Channel__c' in df.columns and len(df) > 0:
                final_channel_counts = df['Channel__c'].value_counts().head(5)
                print(f"\nTop Processed Channels:")
                for channel, count in final_channel_counts.items():
                    print(f"  • {channel}: {count}")
            
            print(f"\n📋 Report ready for review!")
            
            return main_report_path
            
        except Exception as e:
            logging.error(f"Process failed: {e}")
            raise 

 