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

    def _enrich_semicolon_separated_field(self, field_name: str, field_value: str) -> str:
        """Enrich semicolon-separated field values using field mappings
        
        Args:
            field_name: The Salesforce field name (e.g., 'Segment__c')
            field_value: The semicolon-separated field value
            
        Returns:
            Enriched field value with each segment mapped and formatted
        """
        if not field_value:
            return field_value
        
        # Split by semicolons and process each segment
        segments = [segment.strip() for segment in field_value.split(';') if segment.strip()]
        enriched_segments = []
        
        for segment in segments:
            enriched_segment = self._get_field_mapping(field_name, segment)
            enriched_segments.append(enriched_segment)
        
        # Join the enriched segments back with semicolons
        return '; '.join(enriched_segments)

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
        
        # 14. Segment__c - Marketing segment
        segment = campaign.get('Segment__c')
        if segment:
            enriched_segment = self._enrich_semicolon_separated_field('Segment__c', segment)
            context_parts.append(f"Marketing segment: {enriched_segment}")
        
        # 15. Company_Size_Context - Intelligently determined company size segment
        company_size = self._determine_company_size(campaign)
        if company_size:
            mapped_value = self._get_field_mapping('Company_Size_Context', company_size)
            context_parts.append(f"Company size segment: {mapped_value}")
        
        # 16. Buyer_Journey_Indicators - AI-analyzed buyer journey stage
        journey_stage = self._analyze_buyer_journey(campaign)
        if journey_stage:
            context_parts.append(f"Buyer journey stage: {journey_stage}")
        
        # 17. Description - Campaign description
        description = campaign.get('Description')
        if description:
            context_parts.append(f"Campaign description: {str(description)}")
        
        # 18. Name - Campaign title
        name = campaign.get('Name')
        if name:
            context_parts.append(f"Campaign title: {name}")
        
        # 19. Intended_Country__c - Target geographic market for campaign
        intended_country = campaign.get('Intended_Country__c')
        if intended_country:
            context_parts.append(f"Target geographic market for campaign: {intended_country}")
        
        # 20. Non_Attributable__c - Indicator for campaigns without direct attribution tracking
        non_attributable = campaign.get('Non_Attributable__c')
        if non_attributable is not None:
            if str(non_attributable).lower() == 'true':
                context_parts.append(f"Attribution tracking: Cannot directly trace leads back to this campaign (lead may have been influenced by campaign)")
            else:
                context_parts.append(f"Attribution tracking: Can clearly track that a lead came from this specific campaign (clear cause + effect)")
        
        # 21. Program__c - Parent marketing program
        program = campaign.get('Program__c')
        if program:
            context_parts.append(f"Parent marketing program: {program}")
        
        # 22. Short_Description_for_Sales__c - Concise sales focused campaign summary
        short_description = campaign.get('Short_Description_for_Sales__c')
        if short_description:
            context_parts.append(f"Concise sales focused campaign summary: {short_description}")
        
        # 23. BMID__c - Business Marketing ID with enrichment
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
        """Enrich BMID__c based on customer keywords first, then Channel__c type
        
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
            # First check for customer keywords in BMID
            bmid_lower = bmid.lower()
            customer_keywords = ['cm', 'pendo', 'upsell', 'adoption', 'rt', 'lcm']
            
            for keyword in customer_keywords:
                if keyword in bmid_lower:
                    logging.info(f"Customer keyword '{keyword}' found in BMID: {bmid}")
                    enriched = self._enrich_customer_bmid(bmid)
                    if enriched:
                        result = f"{bmid} ({enriched})"
                        logging.info(f"Customer BMID enrichment successful: {result}")
                        return result
                    else:
                        logging.warning(f"Customer BMID enrichment returned empty for: {bmid}")
                        return f"{bmid} (Customer campaign - no specific mapping found)"
            
            # Fall back to channel-based enrichment
            if channel == 'Email':
                enriched = self._enrich_email_bmid(bmid)
            elif channel == 'Content Syndication':
                enriched = self._enrich_content_syndication_bmid(campaign)
            elif channel == 'Social Media':
                enriched = self._enrich_social_media_bmid(campaign)
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
    
    def _enrich_content_syndication_bmid(self, campaign: pd.Series) -> str:
        """Parse Content Syndication campaign using Name field with underscores
        
        Args:
            campaign: Campaign data containing Name field
            
        Returns:
            Enriched description string
        """
        cs_mappings = self.context_mappings.get('BMID_Content_Syndication', {})
        if not cs_mappings:
            logging.warning("BMID_Content_Syndication mappings not found in field_mappings.json")
            return ""
        
        campaign_name = campaign.get('Name', '')
        if not campaign_name:
            logging.warning("Campaign Name is empty for Content Syndication enrichment")
            return ""
        
        # Split campaign name by underscores
        name_parts = campaign_name.split('_')
        enriched_parts = []
        
        logging.info(f"Parsing Content Syndication Name: {campaign_name}")
        logging.info(f"Name parts: {name_parts}")
        
        for part in name_parts:
            if not part:  # Skip empty parts
                continue
                
            part_upper = part.upper()
            found_match = False
            
            # Check if this part matches any of our mappings (try both original case and uppercase)
            if part in cs_mappings:
                enriched_parts.append(cs_mappings[part])
                logging.info(f"Mapped Content Syndication part '{part}' -> {cs_mappings[part]}")
                found_match = True
            elif part_upper in cs_mappings:
                enriched_parts.append(cs_mappings[part_upper])
                logging.info(f"Mapped Content Syndication part '{part}' -> {cs_mappings[part_upper]}")
                found_match = True
            else:
                # Check for fiscal year pattern (FY followed by digits)
                if part_upper.startswith('FY') and len(part_upper) >= 4:
                    fy_match = re.match(r'FY\d{2,4}', part_upper)
                    if fy_match:
                        enriched_parts.append(f"Fiscal Year - {part_upper}")
                        logging.info(f"Matched Fiscal Year pattern: {part_upper}")
                        found_match = True
                
                if not found_match:
                    # Check if this might be a vendor (longer unmapped part)
                    if len(part) >= 4:  # Assume vendors are at least 4 characters
                        enriched_parts.append(f"Vendor - {part}")
                        logging.info(f"Identified vendor: {part}")
                    else:
                        # Keep short unmapped parts as-is
                        enriched_parts.append(part)
                        logging.warning(f"No mapping found for Content Syndication part: {part}")
        
        result = ", ".join(enriched_parts)
        logging.info(f"Content Syndication Name enrichment result: {result}")
        return result
    
    def _enrich_social_media_bmid(self, campaign: pd.Series) -> str:
        """Parse Social Media campaign using structured Name field format
        
        Expected format: Channel_Country_Product_Vendor_Objective1_CampaignType_Objective2_BusinessSize_MediaObjective_AdType
        
        Args:
            campaign: Campaign data containing Name field
            
        Returns:
            Enriched description string with parsed components
        """
        campaign_name = campaign.get('Name', '')
        if not campaign_name:
            logging.warning("Campaign Name is empty for Social Media enrichment")
            return ""
        
        # Split campaign name by underscores
        name_parts = campaign_name.split('_')
        
        logging.info(f"Parsing Social Media Name: {campaign_name}")
        logging.info(f"Name parts: {name_parts} (count: {len(name_parts)})")
        
        # Expected format has 10 components
        expected_labels = [
            "Channel", "Country", "Product", "Vendor", "Objective 1", 
            "Campaign Type", "Objective 2", "Business Size", "Media Objective", "Ad Type"
        ]
        
        enriched_parts = []
        
        # Parse each component based on position and expected label
        for i, part in enumerate(name_parts):
            if not part:  # Skip empty parts
                continue
                
            # Get the expected label for this position
            label = expected_labels[i] if i < len(expected_labels) else f"Component {i+1}"
            
            # Apply specific transformations based on position and existing mappings
            enriched_value = self._transform_social_media_component(part, i, label)
            
            enriched_parts.append(f"{label}: {enriched_value}")
            logging.info(f"Social Media component {i+1} - {label}: '{part}' -> '{enriched_value}'")
        
        # Handle case where we have fewer parts than expected
        if len(name_parts) < len(expected_labels):
            logging.warning(f"Social Media campaign has {len(name_parts)} parts, expected {len(expected_labels)}")
        
        result = " | ".join(enriched_parts)
        logging.info(f"Social Media BMID enrichment result: {result}")
        return result
    
    def _transform_social_media_component(self, part: str, position: int, label: str) -> str:
        """Transform individual Social Media campaign component using BMID_Social_Media mappings
        
        Args:
            part: The component value to transform
            position: Position in the campaign name (0-based)
            label: Expected label for this position
            
        Returns:
            Formatted component value with mapping: "<value> - <mapping>" or just "<value>" for unmapped items
        """
        # Get Social Media mappings
        sm_mappings = self.context_mappings.get('BMID_Social_Media', {})
        
        # Special handling for Business Size (position 7) - skip mapping as requested
        if position == 7:  # Business Size
            if part.lower() == 'all':
                return "All"
            else:
                return part.title()
        
        # Country formatting (position 1)
        elif position == 1:  # Country
            if part.upper() == 'US':
                return "United States"
            elif part.upper() == 'UK':
                return "United Kingdom"
            elif part.upper() == 'CA':
                return "Canada"
            else:
                return part.upper()
        
        # Vendor formatting (position 3) - use existing vendor mappings first, then Social Media mappings
        elif position == 3:  # Vendor
            vendor_mappings = self.context_mappings.get('Vendor__c', {})
            if part in vendor_mappings:
                return f"{part} - {vendor_mappings[part]}"
            elif part in sm_mappings:
                return f"{part} - {sm_mappings[part]}"
            else:
                return part  # Just return the vendor name without mapping
        
        # Product formatting (position 2) - use existing product mappings first, then Social Media mappings
        elif position == 2:  # Product
            product_mappings = self.context_mappings.get('Intended_Product__c', {})
            if part in product_mappings:
                return f"{part} - {product_mappings[part]}"
            elif part in sm_mappings:
                return f"{part} - {sm_mappings[part]}"
            else:
                return part
        
        # For all other positions, use Social Media mappings if available
        else:
            if part in sm_mappings:
                # Format the display value for specific components
                display_value = part
                if position == 5 and part.lower() == 'demandgen':  # Campaign Type
                    display_value = "Demand Gen"
                elif position == 8 and part.lower() == 'accountslist':  # Media Objective
                    display_value = "Accounts List"
                
                return f"{display_value} - {sm_mappings[part]}"
            else:
                # Format unmapped components nicely
                if position == 0:  # Channel
                    if part.lower() == 'paidsocial':
                        return "Paid Social Media"
                    else:
                        return part.title()
                elif position == 5:  # Campaign Type
                    if part.lower() == 'demandgen':
                        return "Demand Gen"
                    else:
                        return part.replace('_', ' ').title()
                else:
                    return part.replace('_', ' ').title()
        
        # Default fallback
        return part.title()
    
    def _enrich_customer_bmid(self, bmid: str) -> str:
        """Parse Customer BMID using BMID_Customer mappings
        
        Args:
            bmid: The BMID string to enrich
            
        Returns:
            Enriched description string
        """
        customer_mappings = self.context_mappings.get('BMID_Customer', {})
        if not customer_mappings:
            logging.warning("BMID_Customer mappings not found in field_mappings.json")
            return ""
        
        enriched_parts = []
        bmid_upper = bmid.upper()
        
        logging.info(f"Parsing Customer BMID: {bmid}")
        
        # Check for each customer keyword mapping
        for keyword, description in customer_mappings.items():
            if keyword.upper() in bmid_upper:
                enriched_parts.append(description)
                logging.info(f"Matched Customer BMID keyword: {keyword} -> {description}")
        
        if enriched_parts:
            result = ", ".join(enriched_parts)
            logging.info(f"Customer BMID enrichment result: {result}")
            return result
        else:
            logging.warning(f"No customer mappings found in BMID: {bmid}")
            return ""
    
    def determine_outreach_sequence(self, campaign: pd.Series) -> Optional[dict]:
        """Determine appropriate outreach sequence based on campaign attributes
        
        Args:
            campaign: Campaign data as pandas Series
            
        Returns:
            Dict with 'name' and 'url' keys if sequence found, None otherwise
        """
        channel = campaign.get('Channel__c', '')
        sub_channel = campaign.get('Sub_Channel__c', '')
        bmid = campaign.get('BMID__c', '')
        intended_product = campaign.get('Intended_Product__c', '')
        
        # Get enriched BMID context to extract EE Size
        bmid_enriched = self._enrich_bmid(campaign)
        ee_size = self._extract_ee_size_from_enriched_bmid(bmid_enriched)
        
        logging.info(f"Determining outreach sequence for campaign {campaign.get('Id', 'Unknown')}: Channel={channel}, Sub_Channel={sub_channel}, BMID={bmid}, Product={intended_product}, EE_Size={ee_size}")
        
        # Route based on channel type
        if channel == 'Content Syndication' and sub_channel == 'Content':
            return self._route_content_syndication(campaign, bmid_enriched, ee_size)
        elif channel == 'Email':
            return self._route_email_campaign(bmid, intended_product, ee_size)
        else:
            logging.info(f"No outreach sequence routing configured for Channel={channel}, Sub_Channel={sub_channel}")
            return None
    
    def _extract_ee_size_from_enriched_bmid(self, enriched_bmid: str) -> Optional[str]:
        """Extract EE Size from enriched BMID context
        
        Args:
            enriched_bmid: Enriched BMID string containing EE Size in parentheses
            
        Returns:
            EE Size string (e.g., '<= 99', '>= 100', 'Any') or None if not found
        """
        import re
        
        if not enriched_bmid:
            return None
        
        # Look for patterns like (EE Size: <= 99), (EE Size: >= 100), or (EE Size: Any)
        ee_size_pattern = r'\(EE Size:\s*([^)]+)\)'
        match = re.search(ee_size_pattern, enriched_bmid)
        
        if match:
            ee_size = match.group(1).strip()
            logging.info(f"Extracted EE Size from enriched BMID: {ee_size}")
            return ee_size
        else:
            logging.warning(f"Could not extract EE Size from enriched BMID: {enriched_bmid}")
            return None
    
    def _extract_integrated_campaigns_from_enriched_bmid(self, enriched_bmid: str) -> list:
        """Extract integrated marketing campaigns from enriched BMID context
        
        Args:
            enriched_bmid: Enriched BMID string with parsed components
            
        Returns:
            List of integrated marketing campaign names
        """
        if not enriched_bmid:
            return []
        
        campaigns = []
        
        # Look for "Integrated Marketing Campaign - " patterns
        import re
        campaign_pattern = r'Integrated Marketing Campaign - ([^,)]+)'
        matches = re.findall(campaign_pattern, enriched_bmid)
        
        for match in matches:
            campaign_name = match.strip()
            campaigns.append(campaign_name)
            logging.info(f"Found integrated marketing campaign: {campaign_name}")
        
        return campaigns
    
    def _route_content_syndication(self, campaign: pd.Series, enriched_bmid: str, ee_size: Optional[str]) -> Optional[dict]:
        """Route Content Syndication campaigns to outreach sequences using enriched BMID
        
        Args:
            campaign: Campaign data as pandas Series
            enriched_bmid: Enriched BMID string with parsed components
            ee_size: Employee size extracted from enriched BMID
            
        Returns:
            Dict with sequence info or None (or multiple sequences if EE Size is 'Any')
        """
        if not enriched_bmid:
            return None
        
        # Parse integrated marketing campaigns from enriched BMID
        integrated_campaigns = self._extract_integrated_campaigns_from_enriched_bmid(enriched_bmid)
        
        # Parse channel from enriched BMID
        has_lead_gen_content = 'Channel - Lead Gen Content' in enriched_bmid
        
        logging.info(f"Content Syndication routing - Integrated Campaigns: {integrated_campaigns}, Lead Gen Content: {has_lead_gen_content}, EE Size: {ee_size}")
        
        # Define routing rules based on the specification
        routing_rules = []
        
        # Rule: RingEX + NOT Public Sector + EE Size <= 99
        if 'RingEX' in integrated_campaigns and 'Public Sector (vertical)' not in integrated_campaigns:
            if ee_size == '<= 99':
                routing_rules.append({
                    'conditions': ['RingEX', 'NOT Public Sector', '<= 99'],
                    'name': 'RingEX Sequence - SBG CPL Q1FY25',
                    'url': 'https://web.outreach.io/sequences/4614/overview',
                    'score': 3
                })
            elif ee_size == '>= 100':
                routing_rules.append({
                    'conditions': ['RingEX', 'NOT Public Sector', '>= 100'],
                    'name': 'RingEX Sequence - MME CPL - BDR - Q1FY25',
                    'url': 'https://web.outreach.io/sequences/4613/overview',
                    'score': 3
                })
            elif ee_size == 'Any':
                # Return both sequences for Any size
                return {
                    'name': 'Multiple sequences based on EE Size',
                    'sequences': [
                        {'name': 'RingEX Sequence - SBG CPL Q1FY25 (EE Size <= 99)', 'url': 'https://web.outreach.io/sequences/4614/overview'},
                        {'name': 'RingEX Sequence - MME CPL - BDR - Q1FY25 (EE Size >= 100)', 'url': 'https://web.outreach.io/sequences/4613/overview'}
                    ]
                }
        
        # Rule: RingCX + NOT Public Sector + EE Size <= 99
        if 'RingCX' in integrated_campaigns and 'Public Sector (vertical)' not in integrated_campaigns:
            if ee_size == '<= 99':
                routing_rules.append({
                    'conditions': ['RingCX', 'NOT Public Sector', '<= 99'],
                    'name': 'BDR - RingCX Sequence - CPL Q1FY25',
                    'url': 'https://web.outreach.io/sequences/4626/overview',
                    'score': 3
                })
            elif ee_size == '>= 100':
                routing_rules.append({
                    'conditions': ['RingCX', 'NOT Public Sector', '>= 100'],
                    'name': 'BDR - RingCX Sequence - CPL Q1FY25',
                    'url': 'https://web.outreach.io/sequences/4626/overview',
                    'score': 3
                })
            elif ee_size == 'Any':
                # Return both sequences for Any size (same sequence name for both sizes)
                return {
                    'name': 'BDR - RingCX Sequence - CPL Q1FY25 (All EE Sizes)',
                    'url': 'https://web.outreach.io/sequences/4626/overview'
                }
        
        # Rule: Financial Services + Lead Gen Content
        if 'Financial Services (vertical)' in integrated_campaigns and has_lead_gen_content:
            routing_rules.append({
                'conditions': ['Financial Services', 'Lead Gen Content'],
                'name': 'BDR FinServ Q12025',
                'url': 'https://web.outreach.io/sequences/4700/overview',
                'score': 2
            })
        
        # Rule: Healthcare + Lead Gen Content
        if 'Healthcare (vertical)' in integrated_campaigns and has_lead_gen_content:
            routing_rules.append({
                'conditions': ['Healthcare', 'Lead Gen Content'],
                'name': 'BDR Healthcare CPL Q12025',
                'url': 'https://web.outreach.io/sequences/4701/overview',
                'score': 2
            })
        
        # Rule: Public Sector + RingEX
        if 'Public Sector (vertical)' in integrated_campaigns and 'RingEX' in integrated_campaigns:
            routing_rules.append({
                'conditions': ['Public Sector', 'RingEX'],
                'name': 'SLED - RingEX - Q4FY24',
                'url': 'https://web.outreach.io/sequences/4494/overview',
                'score': 2
            })
        
        # Rule: Public Sector + RingCX
        if 'Public Sector (vertical)' in integrated_campaigns and 'RingCX' in integrated_campaigns:
            routing_rules.append({
                'conditions': ['Public Sector', 'RingCX'],
                'name': 'SLED - RingCX - Q4FY24',
                'url': 'https://web.outreach.io/sequences/4493/overview',
                'score': 2
            })
        
        # Find the rule with the highest score (most conditions satisfied)
        if routing_rules:
            best_rule = max(routing_rules, key=lambda x: x['score'])
            logging.info(f"Selected Content Syndication sequence: {best_rule['name']} (score: {best_rule['score']})")
            return {
                'name': best_rule['name'],
                'url': best_rule['url']
            }
        else:
            logging.info(f"No Content Syndication routing rules matched for enriched BMID: {enriched_bmid}")
            return None
    
    def _route_email_campaign(self, bmid: str, intended_product: Optional[str], ee_size: Optional[str]) -> Optional[dict]:
        """Route Email campaigns to outreach sequences
        
        Args:
            bmid: Campaign BMID
            intended_product: Intended product from campaign
            ee_size: Employee size extracted from enriched BMID
            
        Returns:
            Dict with sequence info or None
        """
        if not bmid:
            return None
        
        bmid_upper = bmid.upper()
        product_upper = (intended_product or '').upper()
        
        # Define routing rules with priority (more conditions = higher priority)
        routing_rules = [
            # 4-condition rules (highest priority)
            {
                'conditions': ['DGSMBNONNRNFF' in bmid_upper, 'SLED' not in bmid_upper, product_upper == 'RINGEX', ee_size == '<= 99'],
                'name': 'RingEX Sequence - SBG CPL Q1FY25',
                'url': 'https://web.outreach.io/sequences/4614/overview'
            },
            {
                'conditions': ['DGSMBNONNRNFF' in bmid_upper, 'SLED' not in bmid_upper, product_upper == '', ee_size == '<= 99'],
                'name': 'RingEX Sequence - SBG CPL Q1FY25',
                'url': 'https://web.outreach.io/sequences/4614/overview'
            },
            {
                'conditions': ['DGSMBNONNRNFF' in bmid_upper, 'SLED' not in bmid_upper, product_upper == 'GENERAL', ee_size == '<= 99'],
                'name': 'RingEX Sequence - SBG CPL Q1FY25',
                'url': 'https://web.outreach.io/sequences/4614/overview'
            },
            {
                'conditions': ['DGSMBNONNRNFF' in bmid_upper, 'SLED' not in bmid_upper, product_upper == 'RINGCX', ee_size == '<= 99'],
                'name': 'BDR - RingCX Sequence - CPL Q1FY25',
                'url': 'https://web.outreach.io/sequences/4626/overview'
            },
            {
                'conditions': ['DGSMBNONNRNFF' in bmid_upper, 'SLED' not in bmid_upper, product_upper == 'RINGEX', ee_size == '>= 100'],
                'name': 'RingEX Sequence - MME CPL - BDR - Q1FY25',
                'url': 'https://web.outreach.io/sequences/4613/overview'
            },
            {
                'conditions': ['DGSMBNONNRNFF' in bmid_upper, 'SLED' not in bmid_upper, product_upper == 'RINGCX', ee_size == '>= 100'],
                'name': 'BDR - RingCX Sequence - CPL Q1FY25',
                'url': 'https://web.outreach.io/sequences/4626/overview'
            },
            # 2-condition rules
            {
                'conditions': ['SLED' in bmid_upper, product_upper == 'RINGEX'],
                'name': 'SLED - RingEX - Q4FY24',
                'url': 'https://web.outreach.io/sequences/4494/overview'
            },
            {
                'conditions': ['SLED' in bmid_upper, product_upper == 'RINGCX'],
                'name': 'SLED - RingCX - Q4FY24',
                'url': 'https://web.outreach.io/sequences/4493/overview'
            },
            # 1-condition rules (exact BMID matches)
            {
                'conditions': ['DGUPMHCNRNFF' in bmid_upper],
                'name': 'HC Nurture 2025 Outreach',
                'url': 'https://web.outreach.io/sequences/4747/overview'
            },
            {
                'conditions': ['DGUPMREXNR' in bmid_upper],
                'name': 'REX MME Nurture 2025 Outreach',
                'url': 'https://web.outreach.io/sequences/4748/overview'
            },
            {
                'conditions': ['DGUPMREXNRNFF' in bmid_upper],
                'name': 'REX MME Nurture 2025 Outreach',
                'url': 'https://web.outreach.io/sequences/4748/overview'
            },
            {
                'conditions': ['DGUPMRCXNR' in bmid_upper],
                'name': 'RCX MME Nurture 2025 Outreach',
                'url': 'https://web.outreach.io/sequences/4749/overview'
            },
            {
                'conditions': ['DGUPMRCXNRNFF' in bmid_upper],
                'name': 'RCX MME Nurture 2025 Outreach',
                'url': 'https://web.outreach.io/sequences/4749/overview'
            },
            {
                'conditions': ['DGSMBRCXNR' in bmid_upper],
                'name': 'RCX SMB Nurture 2025 Outreach',
                'url': 'https://web.outreach.io/sequences/4750/overview'
            },
            {
                'conditions': ['DGSMBRCXNRNFF' in bmid_upper],
                'name': 'RCX SMB Nurture 2025 Outreach',
                'url': 'https://web.outreach.io/sequences/4750/overview'
            },
            {
                'conditions': ['LGENTFINSERV' in bmid_upper],
                'name': 'FS Nurture 2025 Outreach',
                'url': 'https://web.outreach.io/sequences/4751/overview'
            },
            {
                'conditions': ['DGUPMFINSERVNRNFF' in bmid_upper],
                'name': 'FS Nurture 2025 Outreach',
                'url': 'https://web.outreach.io/sequences/4751/overview'
            },
            {
                'conditions': ['DGSMBREXNR' in bmid_upper],
                'name': 'REX SMB Nurture 2025 Outreach',
                'url': 'https://web.outreach.io/sequences/4752/overview'
            },
            {
                'conditions': ['DGSMBREXNRNFF' in bmid_upper],
                'name': 'REX SMB Nurture 2025 Outreach',
                'url': 'https://web.outreach.io/sequences/4752/overview'
            }
        ]
        
        return self._find_best_matching_rule(routing_rules, bmid_upper)
    
    def _find_best_matching_rule(self, routing_rules: list, bmid_upper: str) -> Optional[dict]:
        """Find the rule that matches the most conditions
        
        Args:
            routing_rules: List of routing rule dictionaries
            bmid_upper: BMID in uppercase for logging
            
        Returns:
            Dict with best matching sequence info or None
        """
        best_match = None
        best_score = 0
        
        for rule in routing_rules:
            # Count how many conditions are met
            conditions_met = sum(1 for condition in rule['conditions'] if condition)
            
            # All conditions must be True for the rule to apply
            if conditions_met == len(rule['conditions']) and all(rule['conditions']):
                if conditions_met > best_score:
                    best_match = rule
                    best_score = conditions_met
                    logging.info(f"Found better matching rule with {conditions_met} conditions: {rule['name']}")
        
        if best_match:
            logging.info(f"Selected outreach sequence for BMID {bmid_upper}: {best_match['name']} (score: {best_score})")
            return {
                'name': best_match['name'],
                'url': best_match['url']
            }
        else:
            logging.info(f"No outreach sequence rules matched for BMID {bmid_upper}")
            return None 