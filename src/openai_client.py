import os
import logging
import time
from typing import Tuple
import openai
import pandas as pd


class OpenAIClient:
    """Handles OpenAI API interactions for generating campaign descriptions"""
    
    def __init__(self, use_openai: bool = True):
        """Initialize OpenAI client
        
        Args:
            use_openai: If False, will generate prompts without calling OpenAI
        """
        self.use_openai = use_openai
        if self.use_openai:
            self.client = self._setup_openai()
        else:
            logging.info("Running in prompt preview mode - OpenAI calls disabled")
            self.client = None
    
    def _setup_openai(self):
        """Setup OpenAI client"""
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        return openai
    
    def generate_description(self, campaign: pd.Series, context: str) -> Tuple[str, str]:
        """Generate AI description for a single campaign
        
        Args:
            campaign: Campaign data as pandas Series
            context: Enriched context string
            
        Returns:
            tuple: (description, prompt) - description is the AI response or preview text,
                   prompt is the full prompt that would be sent to OpenAI
        """
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
            response = self.client.chat.completions.create(
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
    
    def process_campaigns_batch(self, campaigns: pd.DataFrame, context_manager, batch_size: int = 10) -> pd.DataFrame:
        """Process campaigns in batches to generate AI descriptions
        
        Args:
            campaigns: DataFrame with campaign data
            context_manager: ContextManager instance for enriching context
            batch_size: Number of campaigns to process in each batch
            
        Returns:
            DataFrame with AI descriptions added
        """
        campaigns = campaigns.copy()
        campaigns['AI_Sales_Description'] = ''
        campaigns['AI_Prompt'] = ''
        
        total_campaigns = len(campaigns)
        
        logging.info(f"Processing {total_campaigns} campaigns in batches of {batch_size}")
        
        for i in range(0, total_campaigns, batch_size):
            batch_end = min(i + batch_size, total_campaigns)
            batch = campaigns.iloc[i:batch_end]
            
            logging.info(f"Processing campaigns {i+1} to {batch_end}")
            
            for idx, campaign in batch.iterrows():
                # Get enriched context
                context = context_manager.enrich_campaign_context(campaign)
                
                # Generate AI description
                description, prompt = self.generate_description(campaign, context)
                campaigns.at[idx, 'AI_Sales_Description'] = description
                campaigns.at[idx, 'AI_Prompt'] = prompt
                
                # Rate limiting - adjust as needed for your OpenAI tier
                if self.use_openai:
                    time.sleep(0.5)
            
            # Log progress every 100 campaigns
            if (i + 1) % 100 == 0:
                logging.info(f"Progress: {i + 1}/{total_campaigns} campaigns processed")
        
        return campaigns 