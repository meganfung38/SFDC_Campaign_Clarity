import logging
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
        
        # Initialize components
        self.salesforce_client = SalesforceClient()
        self.openai_client = OpenAIClient(use_openai=use_openai)
        self.context_manager = ContextManager()
        self.cache_manager = CacheManager()
        self.excel_generator = ExcelReportGenerator(output_directory=output_directory)
        
        logging.info(f"Campaign processor initialized (OpenAI: {use_openai})")
    
    def extract_campaigns(self, use_cache: bool = True) -> pd.DataFrame:
        """Extract campaigns with members created in last 12 months
        
        Args:
            use_cache: Whether to use cached campaign IDs
            
        Returns:
            DataFrame with campaign data
        """
        try:
            # Try to load from cache first
            cache_data = None
            if use_cache:
                cache_data = self.cache_manager.load_campaign_cache()
            
            if cache_data and 'campaign_ids' in cache_data and 'member_counts' in cache_data:
                campaign_ids = cache_data['campaign_ids']
                member_counts = cache_data['member_counts']
                logging.info(f"Using cached campaign IDs: {len(campaign_ids)} campaigns")
            else:
                # Extract fresh campaign member data
                campaign_ids, member_counts = self.salesforce_client.extract_campaign_members()
                
                if not campaign_ids:
                    logging.warning("No campaigns found with recent members")
                    return pd.DataFrame()
                
                # Save to cache
                self.cache_manager.save_campaign_cache(campaign_ids, member_counts)
            
            # Extract campaign details
            df = self.salesforce_client.extract_campaigns(campaign_ids)
            
            # Add member count
            df['Recent_Member_Count'] = df['Id'].map(member_counts.get)
            
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
        return self.openai_client.process_campaigns_batch(
            df, self.context_manager, batch_size=batch_size
        )
    
    def create_reports(self, df: pd.DataFrame) -> tuple[str, str]:
        """Create Excel reports with campaign descriptions
        
        Args:
            df: DataFrame with processed campaign data
            
        Returns:
            Tuple of (main_report_path, summary_report_path)
        """
        # Create main report
        main_report_path = self.excel_generator.create_campaign_report(
            df, use_openai=self.use_openai
        )
        
        # Create summary report
        processing_stats = {
            'total_members': df['Recent_Member_Count'].sum() if 'Recent_Member_Count' in df.columns else 0
        }
        summary_report_path = self.excel_generator.create_summary_report(df, processing_stats)
        
        return main_report_path, summary_report_path
    
    def run(self, use_cache: bool = True, limit: Optional[int] = None, batch_size: int = 10) -> Optional[str]:
        """Main execution method
        
        Args:
            use_cache: Whether to use cached campaign IDs
            limit: Maximum number of campaigns to process (useful for testing)
            batch_size: Number of campaigns to process in each batch
            
        Returns:
            Path to the main report file
        """
        try:
            # Extract campaigns
            logging.info("Starting campaign extraction...")
            df = self.extract_campaigns(use_cache=use_cache)
            
            if df.empty:
                logging.warning("No campaigns to process")
                return None
            
            # Apply limit if specified
            if limit and limit > 0:
                logging.info(f"Limiting processing to {limit} campaigns")
                df = df.head(limit)
            
            # Process campaigns to generate descriptions
            logging.info("Generating AI descriptions...")
            df = self.process_campaigns(df, batch_size=batch_size)
            
            # Create reports
            main_report_path, summary_report_path = self.create_reports(df)
            
            logging.info(f"Process completed successfully!")
            logging.info(f"Main report: {main_report_path}")
            logging.info(f"Summary report: {summary_report_path}")
            
            # Print summary statistics
            print(f"\nSummary:")
            print(f"Total campaigns processed: {len(df)}")
            print(f"Campaigns with AI descriptions: {df['AI_Sales_Description'].notna().sum()}")
            print(f"Main report: {main_report_path}")
            print(f"Summary report: {summary_report_path}")
            
            return main_report_path
            
        except Exception as e:
            logging.error(f"Process failed: {e}")
            raise
    
    def clear_cache(self):
        """Clear the campaign cache"""
        self.cache_manager.clear_cache()
    
    def get_cache_info(self):
        """Get information about the current cache"""
        return self.cache_manager.get_cache_info() 