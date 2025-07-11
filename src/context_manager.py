import os
import json
import logging
from typing import Dict, Optional
import pandas as pd


class ContextManager:
    """Manages context mappings and campaign enrichment"""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize context manager
        
        Args:
            project_root: Root directory of the project (defaults to parent of this file)
        """
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(__file__))
        self.project_root = project_root
        self.context_mappings = self._load_context_mappings()
    
    def _load_context_mappings(self) -> Dict:
        """Load context mappings for field values"""
        # Load the comprehensive field mappings file
        field_mappings_path = os.path.join(self.project_root, 'data', 'field_mappings.json')
        
        if os.path.exists(field_mappings_path):
            try:
                with open(field_mappings_path, 'r') as f:
                    mappings = json.load(f)
                    logging.info(f"Loaded field mappings from {field_mappings_path}")
                    return mappings
            except Exception as e:
                logging.error(f"Error loading field mappings from {field_mappings_path}: {e}")
        
        logging.warning("No field mappings file found, using empty mappings (will fall back to raw values)")
        return {}
    
    def enrich_campaign_context(self, campaign: pd.Series) -> str:
        """Build enriched context for a campaign using comprehensive field mappings
        
        Args:
            campaign: Campaign data as pandas Series
            
        Returns:
            Enriched context string with all available field mappings
        """
        context_parts = []
        
        # Core campaign identifier (always included first)
        context_parts.append(f"Campaign: {campaign.get('Name', 'Unknown')}")
        
        # 1. Channel__c - Engagement method
        channel = campaign.get('Channel__c')
        if channel:
            if channel in self.context_mappings.get('Channel__c', {}):
                mapped_value = self.context_mappings['Channel__c'][channel]
                context_parts.append(f"Engagement method: {mapped_value}")
            else:
                context_parts.append(f"Engagement method: {channel}")
        
        # 2. Integrated_Marketing__c - Cross channel marketing integration indicator
        integrated_marketing = campaign.get('Integrated_Marketing__c')
        if integrated_marketing:
            if integrated_marketing in self.context_mappings.get('Integrated_Marketing__c', {}):
                context_parts.append(f"Cross channel marketing integration indicator: {self.context_mappings['Integrated_Marketing__c'][integrated_marketing]}")
            else:
                context_parts.append(f"Cross channel marketing integration indicator: {integrated_marketing}")
        
        # 3. Intended_Product__c - Product interest
        product = campaign.get('Intended_Product__c')
        if product and product != 'General':
            if product in self.context_mappings.get('Intended_Product__c', {}):
                context_parts.append(f"Product interest: {self.context_mappings['Intended_Product__c'][product]}")
            else:
                context_parts.append(f"Product interest: {product}")
        
        # 4. Sub_Channel__c - Secondary channel
        sub_channel = campaign.get('Sub_Channel__c')
        if sub_channel:
            if sub_channel in self.context_mappings.get('Sub_Channel__c', {}):
                context_parts.append(f"Secondary channel: {self.context_mappings['Sub_Channel__c'][sub_channel]}")
            else:
                context_parts.append(f"Secondary channel: {sub_channel}")
        
        # 5. Sub_Channel_Detail__c - Specific engagement context
        sub_detail = campaign.get('Sub_Channel_Detail__c')
        if sub_detail:
            if sub_detail in self.context_mappings.get('Sub_Channel_Detail__c', {}):
                context_parts.append(f"Specific engagement context: {self.context_mappings['Sub_Channel_Detail__c'][sub_detail]}")
            else:
                context_parts.append(f"Specific engagement context: {sub_detail}")
        
        # 6. TCP_Campaign__c - Target customer profile campaign identifier
        tcp_campaign = campaign.get('TCP_Campaign__c')
        if tcp_campaign:
            if tcp_campaign in self.context_mappings.get('TCP_Campaign__c', {}):
                context_parts.append(f"Target customer profile campaign identifier: {self.context_mappings['TCP_Campaign__c'][tcp_campaign]}")
            else:
                context_parts.append(f"Target customer profile campaign identifier: {tcp_campaign}")
        
        # 7. TCP_Program__c - Target customer profile program classification
        tcp_program = campaign.get('TCP_Program__c')
        if tcp_program:
            if tcp_program in self.context_mappings.get('TCP_Program__c', {}):
                context_parts.append(f"Target customer profile program classification: {self.context_mappings['TCP_Program__c'][tcp_program]}")
            else:
                context_parts.append(f"Target customer profile program classification: {tcp_program}")
        
        # 8. TCP_Theme__c - Target customer profile and strategy
        tcp_theme = campaign.get('TCP_Theme__c')
        if tcp_theme:
            if tcp_theme in self.context_mappings.get('TCP_Theme__c', {}):
                context_parts.append(f"Target customer profile and strategy: {self.context_mappings['TCP_Theme__c'][tcp_theme]}")
            else:
                context_parts.append(f"Target customer profile and strategy: {tcp_theme}")
        
        # 9. Type - Campaign format
        camp_type = campaign.get('Type')
        if camp_type:
            if camp_type in self.context_mappings.get('Type', {}):
                context_parts.append(f"Campaign format: {self.context_mappings['Type'][camp_type]}")
            else:
                context_parts.append(f"Campaign format: {camp_type}")
        
        # 10. Vendor__c - Lead source context
        vendor = campaign.get('Vendor__c')
        if vendor:
            if vendor in self.context_mappings.get('Vendor__c', {}):
                context_parts.append(f"Lead source context: {self.context_mappings['Vendor__c'][vendor]}")
            else:
                context_parts.append(f"Lead source context: {vendor}")
        
        # 11. Vertical__c - Industry context
        vertical = campaign.get('Vertical__c')
        if vertical:
            if vertical in self.context_mappings.get('Vertical__c', {}):
                context_parts.append(f"Industry context: {self.context_mappings['Vertical__c'][vertical]}")
            else:
                context_parts.append(f"Industry context: {vertical}")
        
        # 12. Marketing_Message__c - Value proposition focus
        marketing_msg = campaign.get('Marketing_Message__c')
        if marketing_msg:
            if marketing_msg in self.context_mappings.get('Marketing_Message__c', {}):
                context_parts.append(f"Value proposition focus: {self.context_mappings['Marketing_Message__c'][marketing_msg]}")
            else:
                context_parts.append(f"Value proposition focus: {marketing_msg}")
        
        # 13. Territory__c - Sales territory assignment
        territory = campaign.get('Territory__c')
        if territory and ';' not in str(territory):
            if territory in self.context_mappings.get('Territory__c', {}):
                context_parts.append(f"Sales territory assignment: {self.context_mappings['Territory__c'][territory]}")
            else:
                context_parts.append(f"Sales territory assignment: {territory}")
        
        # 14. Company_Size_Context - Intelligently determined company size segment
        company_size = self._determine_company_size(campaign)
        if company_size:
            if company_size in self.context_mappings.get('Company_Size_Context', {}):
                context_parts.append(f"Company size segment: {self.context_mappings['Company_Size_Context'][company_size]}")
            else:
                context_parts.append(f"Company size segment: {company_size}")
        
        # 15. Buyer_Journey_Indicators - AI-analyzed buyer journey stage
        journey_stage = self._analyze_buyer_journey(campaign)
        if journey_stage:
            context_parts.append(f"Buyer journey stage: {journey_stage}")
        
        # 16. Description - Campaign description
        description = campaign.get('Description')
        if description:
            context_parts.append(f"Campaign description: {str(description)}")
        
        # 17. Name - Campaign title
        name = campaign.get('Name')
        if name:
            context_parts.append(f"Campaign title: {name}")
        
        # 18. Intended_Country__c - Target geographic market for campaign
        intended_country = campaign.get('Intended_Country__c')
        if intended_country:
            context_parts.append(f"Target geographic market for campaign: {intended_country}")
        
        # 19. Non_Attributable__c - Indicator for campaigns without direct attribution tracking
        non_attributable = campaign.get('Non_Attributable__c')
        if non_attributable is not None:
            if str(non_attributable).lower() == 'true':
                context_parts.append(f"Attribution tracking: Cannot directly trace leads back to this campaign (lead may have been influenced by campaign)")
            else:
                context_parts.append(f"Attribution tracking: Can clearly track that a lead came from this specific campaign (clear cause + effect)")
        
        # 20. Program__c - Parent marketing program
        program = campaign.get('Program__c')
        if program:
            context_parts.append(f"Parent marketing program: {program}")
        
        # 21. Short_Description_for_Sales__c - Concise sales focused campaign summary
        short_description = campaign.get('Short_Description_for_Sales__c')
        if short_description:
            context_parts.append(f"Concise sales focused campaign summary: {short_description}")
        
        return "\n".join(context_parts)
    
    def _determine_company_size(self, campaign: pd.Series) -> str:
        """Determine company size segment based on campaign context
        
        Args:
            campaign: Campaign data as pandas Series
            
        Returns:
            Company size segment or empty string
        """
        # Check TCP Theme for size indicators
        tcp_theme = campaign.get('TCP_Theme__c')
        if tcp_theme:
            tcp_theme_str = str(tcp_theme)
            if 'SMB' in tcp_theme_str:
                return 'SMB'
            elif 'Upmarket' in tcp_theme_str:
                return 'Upmarket'
            elif 'Enterprise' in tcp_theme_str:
                return 'Enterprise'
        
        # Check campaign name for size indicators
        name = campaign.get('Name')
        if name:
            name_lower = str(name).lower()
            if 'smb' in name_lower or 'small business' in name_lower:
                return 'Small Business'
            elif 'enterprise' in name_lower or 'majors' in name_lower:
                return 'Upmarket'
            elif 'soho' in name_lower:
                return 'SOHO'
        
        return ''
    
    def _analyze_buyer_journey(self, campaign: pd.Series) -> str:
        """Analyze campaign content for buyer journey stage indicators
        
        Args:
            campaign: Campaign data as pandas Series
            
        Returns:
            Buyer journey stage description or empty string
        """
        buyer_journey = self.context_mappings.get('Buyer_Journey_Indicators', {})
        if not buyer_journey:
            return ''
        
        # Get text content to analyze
        text_content = []
        for field in ['Name', 'Description', 'Sub_Channel_Detail__c']:
            value = campaign.get(field)
            if value:
                text_content.append(str(value).lower())
        
        full_text = ' '.join(text_content)
        
        # Check for high intent keywords
        high_intent = buyer_journey.get('High_Intent_Keywords', [])
        if any(keyword in full_text for keyword in high_intent):
            return 'High intent - actively evaluating solutions (demo, trial, pricing interest)'
        
        # Check for research keywords
        research = buyer_journey.get('Research_Keywords', [])
        if any(keyword in full_text for keyword in research):
            return 'Research phase - gathering information and comparing options'
        
        # Check for awareness keywords
        awareness = buyer_journey.get('Awareness_Keywords', [])
        if any(keyword in full_text for keyword in awareness):
            return 'Awareness stage - learning about solutions and understanding needs'
        
        return '' 