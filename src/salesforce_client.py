import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from simple_salesforce import Salesforce
from collections import Counter


class SalesforceClient:
    """Handles Salesforce connection and data extraction"""
    
    def __init__(self):
        """Initialize Salesforce connection"""
        self.sf = self._connect_salesforce()
    
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
    
    def extract_campaign_members(self, months_back: int = 12, member_limit: int = 1000) -> tuple[List[str], Dict[str, int], int]:
        """Extract campaign IDs from members created in last N months
        
        Args:
            months_back: Number of months to look back for campaign members
            member_limit: Maximum number of CampaignMembers to query (for performance control)
            
        Returns:
            Tuple of (campaign_ids, member_counts, total_campaigns_queried)
        """
        try:
            # Calculate date N months ago
            months_ago = (datetime.now() - timedelta(days=months_back * 30)).strftime('%Y-%m-%dT%H:%M:%S.000+0000')
            
            # Query campaign members with configurable limit
            limit_clause = f"LIMIT {member_limit}" if member_limit > 0 else ""
            member_query = f"""
            SELECT CampaignId
            FROM CampaignMember 
            WHERE CreatedDate > {months_ago}
            {limit_clause}
            """
            
            logging.info(f"Fetching campaign members from the last {months_back} months...")
            member_results = self.sf.query_all(member_query)
            
            # Store total campaigns queried (before any filtering)
            total_campaigns_queried = member_results.get('totalSize', 0)
            
            # Process results to get unique campaign IDs
            campaign_member_list = [record['CampaignId'] for record in member_results['records']]
            
            if not campaign_member_list:
                logging.warning(f"No campaign members found in the last {months_back} months")
                return [], {}, total_campaigns_queried
            
            # Calculate member counts per campaign
            member_counts = Counter(campaign_member_list)
            campaign_ids = list(member_counts.keys())
            
            logging.info(f"Found {len(campaign_ids)} unique campaigns with {len(campaign_member_list)} total members")
            logging.info(f"Total campaigns queried: {total_campaigns_queried}")
            return campaign_ids, dict(member_counts), total_campaigns_queried
            
        except Exception as e:
            logging.error(f"Failed to extract campaign members: {e}")
            raise
    
    def extract_campaigns(self, campaign_ids: List[str]) -> pd.DataFrame:
        """Extract campaign data for given campaign IDs
        
        Args:
            campaign_ids: List of campaign IDs to extract
            
        Returns:
            DataFrame with campaign data
        """
        try:
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
                       Name, Non_Attributable__c, Program__c, Segment__c,
                       Short_Description_for_Sales__c, Sub_Channel__c, Sub_Channel_Detail__c, 
                       TCP_Campaign__c, TCP_Program__c, TCP_Theme__c, Territory__c, Type, 
                       Vendor__c, Vertical__c 
                FROM Campaign 
                WHERE Id IN ('{campaign_ids_str}')
                """
                
                logging.info(f"Fetching campaigns batch {i//batch_size + 1} ({len(batch_ids)} campaigns)...")
                campaign_results = self.sf.query_all(campaign_query)
                all_campaigns.extend(campaign_results['records'])
            
            # Convert to DataFrame
            df = pd.DataFrame(all_campaigns)
            df.drop(columns=['attributes'], inplace=True, errors='ignore')
            
            logging.info(f"Successfully extracted {len(df)} campaigns")
            return df
            
        except Exception as e:
            logging.error(f"Failed to extract campaigns: {e}")
            raise 

 