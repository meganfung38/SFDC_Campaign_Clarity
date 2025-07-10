import os
import sys
from datetime import datetime, timedelta
import pandas as pd
from simple_salesforce import Salesforce
import openai
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, PatternFill
import logging
from typing import Dict, List, Optional
import time
from dotenv import load_dotenv
import json
import pickle
from pathlib import Path
import re

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

class CampaignDescriptionGenerator:
    def __init__(self, use_openai=True):
        """Initialize the generator with Salesforce and OpenAI connections
        
        Args:
            use_openai (bool): If False, will generate prompts without calling OpenAI
        """
        self.use_openai = use_openai
        self.sf = self._connect_salesforce()
        if self.use_openai:
            self.openai_client = self._setup_openai()
        else:
            logging.info("Running in prompt preview mode - OpenAI calls disabled")
            self.openai_client = None
        self.context_mappings = self._load_context_mappings()
        
    def _connect_salesforce(self) -> Salesforce:
        """Connect to Salesforce using environment variables"""
        try:
            sf = Salesforce(
                username=os.getenv('SF_USERNAME'),
                password=os.getenv('SF_PASSWORD'),
                security_token=os.getenv('SF_SECURITY_TOKEN'),
                domain=os.getenv('SF_DOMAIN', 'login')
            )
            logging.info("Successfully connected to Salesforce")
            return sf
        except Exception as e:
            logging.error(f"Failed to connect to Salesforce: {e}")
            raise
    
    def _setup_openai(self):
        """Setup OpenAI client"""
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        return openai
    
    def _load_context_mappings(self) -> Dict:
        """Load context mappings for field values"""
        # Try refined mappings first, then fall back to original
        refined_path = os.path.join(os.path.dirname(__file__), 'data', 'context_mappings_refined.json')
        original_path = os.path.join(os.path.dirname(__file__), 'data', 'context_mappings.json')
        
        for json_path in [refined_path, original_path]:
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r') as f:
                        mappings = json.load(f)
                        logging.info(f"Loaded context mappings from {json_path}")
                        return mappings
                except Exception as e:
                    logging.error(f"Error loading context mappings from {json_path}: {e}")
        
        logging.warning("No context mappings file found, using defaults")
        return {
            'Channel__c': {},
            'Type': {},
            'TCP_Theme__c': {},
            'Intended_Product__c': {},
            'Vertical__c': {},
            'Territory__c': {}
        }
    
    def _get_cache_path(self) -> Path:
        """Get the path for the campaign cache file"""
        cache_dir = Path(__file__).parent / "cache"
        cache_dir.mkdir(exist_ok=True)
        return cache_dir / "campaign_ids_cache.pkl"
    
    def _load_campaign_cache(self) -> Optional[Dict]:
        """Load cached campaign IDs and member counts"""
        cache_path = self._get_cache_path()
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    cache_data = pickle.load(f)
                cache_date = cache_data.get('extraction_date')
                if cache_date:
                    days_old = (datetime.now() - cache_date).days
                    logging.info(f"Found campaign cache from {cache_date.strftime('%Y-%m-%d')} ({days_old} days old)")
                return cache_data
            except Exception as e:
                logging.warning(f"Failed to load cache: {e}")
        return None
    
    def _save_campaign_cache(self, campaign_ids: List[str], member_counts: Dict[str, int]):
        """Save campaign IDs and member counts to cache"""
        cache_path = self._get_cache_path()
        cache_data = {
            'campaign_ids': campaign_ids,
            'member_counts': member_counts,
            'extraction_date': datetime.now(),
            'total_campaigns': len(campaign_ids),
            'total_members': sum(member_counts.values())
        }
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            logging.info(f"Saved campaign cache with {len(campaign_ids)} campaigns")
        except Exception as e:
            logging.error(f"Failed to save cache: {e}")
    
    def extract_campaigns(self, use_cache: bool = True) -> pd.DataFrame:
        """Extract campaigns with members created in last 12 months
        
        Args:
            use_cache: If True, will use cached campaign IDs if available
        """
        try:
            # Try to load from cache first
            cache_data = None
            if use_cache:
                cache_data = self._load_campaign_cache()
            
            if cache_data and 'campaign_ids' in cache_data and 'member_counts' in cache_data:
                campaign_ids = cache_data['campaign_ids']
                member_counts = cache_data['member_counts']
                logging.info(f"Using cached campaign IDs: {len(campaign_ids)} campaigns")
            else:
                # Calculate date 12 months ago
                twelve_months_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%S.000+0000')
                
                # Query campaign members without GROUP BY to avoid aggregate query limitations
                member_query = f"""
                SELECT CampaignId
                FROM CampaignMember 
                WHERE CreatedDate > {twelve_months_ago}
                """
                
                logging.info("Fetching campaign members from the last 12 months...")
                member_results = self.sf.query_all(member_query)
                
                # Process results in Python to get unique campaign IDs and counts
                campaign_member_list = [record['CampaignId'] for record in member_results['records']]
                
                if not campaign_member_list:
                    logging.warning("No campaign members found in the last 12 months")
                    return pd.DataFrame()
                
                # Calculate member counts per campaign
                from collections import Counter
                member_counts = Counter(campaign_member_list)
                campaign_ids = list(member_counts.keys())
                
                logging.info(f"Found {len(campaign_ids)} unique campaigns with {len(campaign_member_list)} total members")
                
                # Save to cache
                self._save_campaign_cache(campaign_ids, dict(member_counts))
            
            # Process campaigns in batches to avoid SOQL limits
            batch_size = 200  # Salesforce IN clause limit
            all_campaigns = []
            
            for i in range(0, len(campaign_ids), batch_size):
                batch_ids = campaign_ids[i:i+batch_size]
                campaign_ids_str = "','".join(batch_ids)
                
                # Query campaigns with all fields
                campaign_query = f"""
                SELECT BMID__c, Channel__c, Description, Id, Integrated_Marketing__c, 
                       Intended_Country__c, Intended_Product__c, Marketing_Message__c, 
                       Name, Non_Attributable__c, Program__c, Short_Description_for_Sales__c, 
                       Sub_Channel__c, Sub_Channel_Detail__c, TCP_Campaign__c, 
                       TCP_Program__c, TCP_Theme__c, Territory__c, Type, Vendor__c, 
                       Vertical__c 
                FROM Campaign 
                WHERE Id IN ('{campaign_ids_str}')
                """
                
                logging.info(f"Fetching campaigns batch {i//batch_size + 1} ({len(batch_ids)} campaigns)...")
                campaign_results = self.sf.query_all(campaign_query)
                all_campaigns.extend(campaign_results['records'])
            
            # Convert to DataFrame
            df = pd.DataFrame(all_campaigns)
            df.drop(columns=['attributes'], inplace=True, errors='ignore')
            
            # Add member count
            df['Recent_Member_Count'] = df['Id'].map(member_counts)
            
            logging.info(f"Successfully extracted {len(df)} campaigns")
            return df
            
        except Exception as e:
            logging.error(f"Failed to extract campaigns: {e}")
            raise
    
    def enrich_campaign_context(self, campaign: pd.Series) -> str:
        """Build enriched context for a campaign using field mappings"""
        context_parts = []
        
        # Add campaign name and type
        context_parts.append(f"Campaign: {campaign.get('Name', 'Unknown')}")
        
        # Add channel context
        channel = campaign.get('Channel__c')
        if channel and channel in self.context_mappings.get('Channel__c', {}):
            context_parts.append(f"Engagement Channel: {self.context_mappings['Channel__c'][channel]}")
        elif channel:
            context_parts.append(f"Channel: {channel}")
        
        # Add type context
        camp_type = campaign.get('Type')
        if camp_type and camp_type in self.context_mappings.get('Type', {}):
            context_parts.append(f"Campaign Type: {self.context_mappings['Type'][camp_type]}")
        elif camp_type:
            context_parts.append(f"Type: {camp_type}")
        
        # Add intended product with context (skip if "General")
        product = campaign.get('Intended_Product__c')
        if product and product != 'General':
            if product in self.context_mappings.get('Intended_Product__c', {}):
                context_parts.append(f"Product Interest: {self.context_mappings['Intended_Product__c'][product]}")
            else:
                context_parts.append(f"Product Focus: {product}")
        
        # Add TCP Theme context (buyer segment and strategy)
        tcp_theme = campaign.get('TCP_Theme__c')
        if tcp_theme and tcp_theme in self.context_mappings.get('TCP_Theme__c', {}):
            context_parts.append(f"Campaign Strategy: {self.context_mappings['TCP_Theme__c'][tcp_theme]}")
        
        # Add sub-channel detail for search intent
        sub_detail = campaign.get('Sub_Channel_Detail__c')
        if sub_detail and sub_detail in self.context_mappings.get('Sub_Channel_Detail__c', {}):
            context_parts.append(f"Engagement Detail: {self.context_mappings['Sub_Channel_Detail__c'][sub_detail]}")
        
        # Add vertical context if present
        vertical = campaign.get('Vertical__c')
        if vertical and vertical in self.context_mappings.get('Vertical__c', {}):
            context_parts.append(f"Industry Focus: {self.context_mappings['Vertical__c'][vertical]}")
        
        # Add vendor context for key vendors
        vendor = campaign.get('Vendor__c')
        if vendor and vendor in self.context_mappings.get('Vendor__c', {}):
            context_parts.append(f"Lead Source: {self.context_mappings['Vendor__c'][vendor]}")
        
        # Skip territory if it contains multiple values (has semicolon)
        territory = campaign.get('Territory__c')
        if territory and ';' not in str(territory):
            context_parts.append(f"Territory: {territory}")
        
        # Add marketing message context
        marketing_msg = campaign.get('Marketing_Message__c')
        if marketing_msg and marketing_msg in self.context_mappings.get('Marketing_Message__c', {}):
            context_parts.append(f"Value Prop: {self.context_mappings['Marketing_Message__c'][marketing_msg]}")
        
        # Add description - preserve URLs and key information
        description = campaign.get('Description')
        if description:
            desc_str = str(description)
            # Check if description contains URLs
            import re
            urls = re.findall(r'https?://[^\s\)]+', desc_str)
            
            if urls:
                # If URLs present, include full description to preserve them
                context_parts.append(f"Campaign Details: {desc_str}")
            elif len(desc_str) < 300:
                # If no URLs and reasonably short, include full description
                context_parts.append(f"Campaign Details: {desc_str}")
            else:
                # For very long descriptions without URLs, truncate but preserve key info
                truncated = desc_str[:297] + "..."
                context_parts.append(f"Campaign Details: {truncated}")
        
        return "\n".join(context_parts)
    
    def generate_ai_description(self, campaign: pd.Series) -> tuple[str, str]:
        """Generate AI description for a single campaign
        
        Returns:
            tuple: (description, prompt) - description is the AI response or preview text,
                   prompt is the full prompt that would be sent to OpenAI
        """
        context = self.enrich_campaign_context(campaign)
        
        # Check if this is a Sales Generated campaign
        is_sales_generated = campaign.get('Channel__c') == 'Sales Generated'
        
        if is_sales_generated:
            prompt = f"""Based on the following campaign information, create a concise description (max 255 characters) that helps a salesperson understand:
1. This is a sales-sourced contact (not from prospect engagement)
2. The data source and why this contact was identified
3. What approach might work best for cold outreach

Focus on the sales context and potential fit, not prospect behavior (since they haven't engaged).

Campaign Information:
{context}

Description (max 255 characters):"""
        else:
            prompt = f"""Based on the following campaign information, create a concise description (max 255 characters) that helps a salesperson understand:
1. What the prospect was doing when they engaged with this campaign
2. Why they likely engaged (their intent/interest)
3. What this tells us about their buyer's journey stage

Focus on the prospect's perspective and intent, not marketing terminology.

IMPORTANT: If the campaign details mention any URLs or websites, preserve the domain name in your description.

Campaign Information:
{context}

Description (max 255 characters):"""
        
        if not self.use_openai:
            # Return preview mode response
            preview_description = f"[PROMPT PREVIEW MODE] Campaign: {campaign.get('Name', 'Unknown')[:50]}..."
            return preview_description, prompt
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a sales enablement expert who helps salespeople understand prospect intent and behavior."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            description = response.choices[0].message.content.strip()
            # Ensure it's within 255 characters
            if len(description) > 255:
                description = description[:252] + "..."
            
            return description, prompt
            
        except Exception as e:
            logging.error(f"Failed to generate description for campaign {campaign.get('Id')}: {e}")
            return "Error generating description", prompt
    
    def process_campaigns(self, df: pd.DataFrame, batch_size: int = 10) -> pd.DataFrame:
        """Process campaigns in batches to generate AI descriptions"""
        df['AI_Sales_Description'] = ''
        df['AI_Prompt'] = ''  # Always create this column
        
        total_campaigns = len(df)
        
        logging.info(f"Processing {total_campaigns} campaigns in batches of {batch_size}")
        
        for i in range(0, total_campaigns, batch_size):
            batch_end = min(i + batch_size, total_campaigns)
            batch = df.iloc[i:batch_end]
            
            logging.info(f"Processing campaigns {i+1} to {batch_end}")
            
            for idx, campaign in batch.iterrows():
                description, prompt = self.generate_ai_description(campaign)
                df.at[idx, 'AI_Sales_Description'] = description
                df.at[idx, 'AI_Prompt'] = prompt  # Always save the prompt
                
                # Rate limiting - adjust as needed for your OpenAI tier
                if self.use_openai:
                    time.sleep(0.5)
            
            # Log progress every 100 campaigns
            if (i + 1) % 100 == 0:
                logging.info(f"Progress: {i + 1}/{total_campaigns} campaigns processed")
        
        return df
    
    
    def create_final_report(self, df: pd.DataFrame) -> str:
        """Create final Excel report with AI descriptions and all fields"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if not self.use_openai:
            filename = f"campaign_descriptions_PREVIEW_{timestamp}.xlsx"
        else:
            filename = f"campaign_descriptions_{timestamp}.xlsx"
        output_path = f"/Users/brian.chiosi/Documents/Python/analytical-etl/scripts/AI Campaign Description/{filename}"
        
        # Define column order
        priority_cols = ['AI_Sales_Description']
        if 'AI_Prompt' in df.columns:
            priority_cols.append('AI_Prompt')
        
        # Fields to show after AI columns
        key_fields = [
            'Description', 
            'Short_Description_for_Sales__c', 
            'Id', 
            'Name', 
            'BMID__c',
            'Intended_Product__c', 
            'Channel__c', 
            'Sub_Channel__c', 
            'Sub_Channel_Detail__c'
        ]
        
        # Get remaining columns
        all_cols = df.columns.tolist()
        remaining_cols = [col for col in all_cols if col not in priority_cols + key_fields]
        
        # Build final column order
        final_cols = priority_cols + [col for col in key_fields if col in all_cols] + remaining_cols
        
        # Reorder dataframe
        df = df[final_cols]
        
        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Campaign Descriptions', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Campaign Descriptions']
            
            # Format header row
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        logging.info(f"Final report saved to {filename}")
        return output_path
    
    def run(self, use_cache: bool = True, limit: Optional[int] = None):
        """Main execution method
        
        Args:
            use_cache: Whether to use cached campaign IDs
            limit: Maximum number of campaigns to process (useful for testing)
        """
        try:
            # Extract campaigns
            logging.info("Starting campaign extraction...")
            df = self.extract_campaigns(use_cache=use_cache)
            
            if df.empty:
                logging.warning("No campaigns to process")
                return
            
            # Apply limit if specified
            if limit and limit > 0:
                logging.info(f"Limiting processing to {limit} campaigns")
                df = df.head(limit)
            
            # Process campaigns to generate descriptions
            logging.info("Generating AI descriptions...")
            df = self.process_campaigns(df)
            
            # Create final report
            output_path = self.create_final_report(df)
            
            logging.info(f"Process completed successfully! Report saved to: {output_path}")
            
            # Print summary statistics
            print(f"\nSummary:")
            print(f"Total campaigns processed: {len(df)}")
            print(f"Campaigns with AI descriptions: {df['AI_Sales_Description'].notna().sum()}")
            print(f"Report location: {output_path}")
            
        except Exception as e:
            logging.error(f"Process failed: {e}")
            raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate AI campaign descriptions for Salesforce')
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
    
    args = parser.parse_args()
    
    # Handle cache clearing
    if args.clear_cache:
        cache_path = Path(__file__).parent / "cache" / "campaign_ids_cache.pkl"
        if cache_path.exists():
            cache_path.unlink()
            print("Campaign ID cache cleared successfully")
        else:
            print("No cache found to clear")
        sys.exit(0)
    
    generator = CampaignDescriptionGenerator(use_openai=not args.no_openai)
    generator.run(use_cache=not args.no_cache, limit=args.limit)