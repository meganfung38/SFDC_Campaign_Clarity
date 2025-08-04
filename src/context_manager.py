import os
import json
import logging
import re
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
    
    def _get_field_mapping(self, field_name: str, field_value: str) -> str:
        """Get field mapping with case-insensitive lookup and concatenation format
        
        Args:
            field_name: The Salesforce field name (e.g., 'Channel__c')
            field_value: The field value to map
            
        Returns:
            Concatenated format '<field_value>: <mapped_description>' if mapping found,
            or original value if no mapping found
        """
        if not field_value or field_name not in self.context_mappings:
            return field_value
            
        field_mappings = self.context_mappings[field_name]
        mapped_description = None
        
        # Try exact match first
        if field_value in field_mappings:
            mapped_description = field_mappings[field_value]
        else:
            # Try case-insensitive match
            field_value_lower = field_value.lower()
            for key, value in field_mappings.items():
                if key.lower() == field_value_lower:
                    mapped_description = value
                    break
        
        # Return concatenated format if mapping found, otherwise original value
        if mapped_description and mapped_description.strip():
            return f"{field_value} ({mapped_description})"
        else:
            return field_value

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
            mapped_value = self._get_field_mapping('Channel__c', channel)
            context_parts.append(f"Engagement method: {mapped_value}")
        
        # 2. Integrated_Marketing__c - Cross channel marketing integration indicator
        integrated_marketing = campaign.get('Integrated_Marketing__c')
        if integrated_marketing:
            mapped_value = self._get_field_mapping('Integrated_Marketing__c', integrated_marketing)
            context_parts.append(f"Cross channel marketing integration indicator: {mapped_value}")
                
        # 3. Intended_Product__c - Product interest
        product = campaign.get('Intended_Product__c')
        if product and product != 'General':
            mapped_value = self._get_field_mapping('Intended_Product__c', product)
            context_parts.append(f"Product interest: {mapped_value}")
        
        # 4. Sub_Channel__c - Secondary channel
        sub_channel = campaign.get('Sub_Channel__c')
        if sub_channel:
            mapped_value = self._get_field_mapping('Sub_Channel__c', sub_channel)
            context_parts.append(f"Secondary channel: {mapped_value}")
        
        # 5. Sub_Channel_Detail__c - Specific engagement context
        sub_detail = campaign.get('Sub_Channel_Detail__c')
        if sub_detail:
            mapped_value = self._get_field_mapping('Sub_Channel_Detail__c', sub_detail)
            context_parts.append(f"Specific engagement context: {mapped_value}")
        
        # 6. TCP_Campaign__c - Target customer profile campaign identifier
        tcp_campaign = campaign.get('TCP_Campaign__c')
        if tcp_campaign:
            mapped_value = self._get_field_mapping('TCP_Campaign__c', tcp_campaign)
            context_parts.append(f"Target customer profile campaign identifier: {mapped_value}")
        
        # 7. TCP_Program__c - Target customer profile program classification
        tcp_program = campaign.get('TCP_Program__c')
        if tcp_program:
            mapped_value = self._get_field_mapping('TCP_Program__c', tcp_program)
            context_parts.append(f"Target customer profile program classification: {mapped_value}")
        
        # 8. TCP_Theme__c - Target customer profile and strategy
        tcp_theme = campaign.get('TCP_Theme__c')
        if tcp_theme:
            mapped_value = self._get_field_mapping('TCP_Theme__c', tcp_theme)
            context_parts.append(f"Target customer profile and strategy: {mapped_value}")
        
        # 9. Type - Campaign format
        camp_type = campaign.get('Type')
        if camp_type:
            mapped_value = self._get_field_mapping('Type', camp_type)
            context_parts.append(f"Campaign format: {mapped_value}")
        
        # 10. Vendor__c - Lead source context
        vendor = campaign.get('Vendor__c')
        if vendor:
            mapped_value = self._get_field_mapping('Vendor__c', vendor)
            context_parts.append(f"Lead source context: {mapped_value}")
        
        # 11. Vertical__c - Industry context
        vertical = campaign.get('Vertical__c')
        if vertical:
            mapped_value = self._get_field_mapping('Vertical__c', vertical)
            context_parts.append(f"Industry context: {mapped_value}")
        
        # 12. Marketing_Message__c - Value proposition focus
        marketing_msg = campaign.get('Marketing_Message__c')
        if marketing_msg:
            mapped_value = self._get_field_mapping('Marketing_Message__c', marketing_msg)
            context_parts.append(f"Value proposition focus: {mapped_value}")
        
        # 13. Territory__c - Sales territory assignment
        territory = campaign.get('Territory__c')
        if territory and ';' not in str(territory):
            mapped_value = self._get_field_mapping('Territory__c', territory)
            context_parts.append(f"Sales territory assignment: {mapped_value}")
        
        # 14. Company_Size_Context - Intelligently determined company size segment
        company_size = self._determine_company_size(campaign)
        if company_size:
            mapped_value = self._get_field_mapping('Company_Size_Context', company_size)
            context_parts.append(f"Company size segment: {mapped_value}")
        
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
        
        # 22. BMID__c - Business Marketing ID with enrichment
        bmid_enriched = self._enrich_bmid(campaign)
        if bmid_enriched:
            context_parts.append(f"Business Marketing ID: {bmid_enriched}")
        
        return '\n'.join(context_parts)
    
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
    
    def _enrich_bmid(self, campaign: pd.Series) -> str:
        """Enrich BMID__c based on Channel__c type
        
        Args:
            campaign: Campaign data as pandas Series
            
        Returns:
            Enriched BMID string in format: <BMID__c> (<enriched_description>)
        """
        channel = campaign.get('Channel__c', '')
        bmid = campaign.get('BMID__c', '')
        
        if not bmid:
            return ""
        
        logging.info(f"Enriching BMID: {bmid} for Channel: {channel}")
        
        try:
            if channel == 'Email':
                enriched = self._enrich_email_bmid(bmid)
            elif channel == 'Content Syndication':
                enriched = self._enrich_content_syndication_bmid(bmid)
            else:
                # No enrichment for other channels, return original BMID
                logging.info(f"No BMID enrichment configured for channel: {channel}")
                return f"{bmid} (No enrichment available for this channel)"
            
            if enriched:
                result = f"{bmid} ({enriched})"
                logging.info(f"BMID enrichment successful: {result}")
                return result
            else:
                logging.warning(f"BMID enrichment returned empty for: {bmid}")
                return f"{bmid} (No enrichment mappings found)"
                
        except Exception as e:
            logging.error(f"Error enriching BMID {bmid}: {e}")
            return f"{bmid} (Enrichment error: {str(e)})"
    
    def _enrich_email_bmid(self, bmid: str) -> str:
        """Parse Email BMID using BMID_Email_Prospecting mappings
        
        Args:
            bmid: The BMID string to enrich
            
        Returns:
            Enriched description string
        """
        email_mappings = self.context_mappings.get('BMID_Email_Prospecting', {})
        if not email_mappings:
            logging.warning("BMID_Email_Prospecting mappings not found in field_mappings.json")
            return ""
        
        enriched_parts = []
        remaining_bmid = bmid.upper()
        
        logging.info(f"Parsing Email BMID: {bmid}")
        
        # Parse BMID character by character using longest match first
        while remaining_bmid:
            found_match = False
            
            # Try longest possible matches first (to handle multi-character codes)
            for length in range(min(len(remaining_bmid), 10), 0, -1):
                chunk = remaining_bmid[:length]
                if chunk in email_mappings:
                    enriched_parts.append(email_mappings[chunk])
                    remaining_bmid = remaining_bmid[length:]
                    logging.info(f"Matched Email BMID chunk: {chunk} -> {email_mappings[chunk]}")
                    found_match = True
                    break
            
            if not found_match:
                # Keep unknown character as-is and move to next
                enriched_parts.append(remaining_bmid[0])
                logging.warning(f"No mapping found for Email BMID chunk: {remaining_bmid[0]}")
                remaining_bmid = remaining_bmid[1:]
        
        result = " ".join(enriched_parts)
        logging.info(f"Email BMID enrichment result: {result}")
        return result
    
    def _enrich_content_syndication_bmid(self, bmid: str) -> str:
        """Parse Content Syndication BMID using BMID_Content_Syndication mappings
        
        Args:
            bmid: The BMID string to enrich
            
        Returns:
            Enriched description string
        """
        cs_mappings = self.context_mappings.get('BMID_Content_Syndication', {})
        if not cs_mappings:
            logging.warning("BMID_Content_Syndication mappings not found in field_mappings.json")
            return ""
        
        enriched_parts = []
        remaining_bmid = bmid.upper()
        
        logging.info(f"Parsing Content Syndication BMID: {bmid}")
        
        # Parse BMID using longest match first approach
        while remaining_bmid:
            found_match = False
            
            # Try longest possible matches first (to handle multi-character codes)
            for length in range(min(len(remaining_bmid), 20), 0, -1):
                chunk = remaining_bmid[:length]
                if chunk in cs_mappings:
                    enriched_parts.append(cs_mappings[chunk])
                    remaining_bmid = remaining_bmid[length:]
                    logging.info(f"Matched Content Syndication BMID chunk: {chunk} -> {cs_mappings[chunk]}")
                    found_match = True
                    break
            
            if not found_match:
                # Check for fiscal year pattern (FY followed by digits)
                if remaining_bmid.startswith('FY') and len(remaining_bmid) >= 4:
                    # Extract fiscal year (FY + 2-4 digits)
                    fy_match = re.match(r'FY\d{2,4}', remaining_bmid)
                    if fy_match:
                        fy_chunk = fy_match.group()
                        enriched_parts.append(f"Fiscal Year - {fy_chunk}")
                        remaining_bmid = remaining_bmid[len(fy_chunk):]
                        logging.info(f"Matched Fiscal Year pattern: {fy_chunk}")
                        found_match = True
                
                if not found_match:
                    # Keep unknown character as-is and move to next
                    enriched_parts.append(remaining_bmid[0])
                    logging.warning(f"No mapping found for Content Syndication BMID chunk: {remaining_bmid[0]}")
                    remaining_bmid = remaining_bmid[1:]
        
        result = ", ".join(enriched_parts)
        logging.info(f"Content Syndication BMID enrichment result: {result}")
        return result 