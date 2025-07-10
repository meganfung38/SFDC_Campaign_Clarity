import os
import json
import logging
import re
from typing import Dict
import pandas as pd


class ContextManager:
    """Manages context mappings and campaign enrichment"""
    
    def __init__(self, project_root: str = None):
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
        # Try refined mappings first, then fall back to original
        refined_path = os.path.join(self.project_root, 'data', 'context_mappings_refined.json')
        original_path = os.path.join(self.project_root, 'data', 'context_mappings.json')
        
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
    
    def enrich_campaign_context(self, campaign: pd.Series) -> str:
        """Build enriched context for a campaign using field mappings
        
        Args:
            campaign: Campaign data as pandas Series
            
        Returns:
            Enriched context string
        """
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