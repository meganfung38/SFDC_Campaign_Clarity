import os
import logging
import time
from typing import Tuple, Optional
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
        self.client: Optional[openai.OpenAI] = None
        if self.use_openai:
            self.client = self._setup_openai()
        else:
            logging.info("Running in prompt preview mode - OpenAI calls disabled")
    
    def _setup_openai(self) -> openai.OpenAI:
        """Setup OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        return openai.OpenAI(api_key=api_key)
    
    def _get_prompt_type(self, campaign: pd.Series) -> str:
        """Determine the appropriate prompt type based on Channel__c value
        
        Args:
            campaign: Campaign data as pandas Series
            
        Returns:
            Prompt type string
        """
        channel = campaign.get('Channel__c', '') or ''
        channel = channel.strip()
        if not channel:
            return 'regular_marketing'
        
        # Use case-insensitive matching
        channel_lower = channel.lower()
        
        # Define channel mappings
        sales_generated_channels = [
            "sales generated", "list purchase", "appointment setting", 
            "sales agents & resellers", "default", "other"
        ]
        
        partner_referral_channels = [
            "var campaigns", "var mdf", "affiliates", "isv", "sia", 
            "franchise & assoc.", "service providers", "amazon", "referrals"
        ]
        
        existing_customer_channels = ["upsell"]
        
        events_channels = ["corporate events", "field events", "events", "walk-on"]
        
        high_intent_channels = ["paid search", "organic search"]
        
        retargeting_nurture_channels = [
            "retargeting", "prospect nurturing", "digital", "leadgen", "social media"
        ]
        
        awareness_broadcast_channels = ["media campaigns", "mergers & acquisitions"]
        
        regular_marketing_channels = [
            "content syndication", "web partners", "vendor qualified leads", 
            "email", "direct mail"
        ]
        
        # Check each category in order
        if channel_lower in sales_generated_channels:
            return 'sales_generated'
        elif channel_lower in partner_referral_channels:
            return 'partner_referral'
        elif channel_lower in existing_customer_channels:
            return 'existing_customer'
        elif channel_lower in events_channels:
            return 'events'
        elif channel_lower in high_intent_channels:
            return 'high_intent'
        elif channel_lower in retargeting_nurture_channels:
            return 'retargeting_nurture'
        elif channel_lower in awareness_broadcast_channels:
            return 'awareness_broadcast'
        elif channel_lower in regular_marketing_channels:
            return 'regular_marketing'
        else:
            # Default fallback
            return 'regular_marketing'
    
    def _get_tailored_prompt(self, prompt_type: str, context: str) -> str:
        """Get the appropriate prompt based on prompt type
        
        Args:
            prompt_type: Type of prompt to use
            context: Enriched campaign context
            
        Returns:
            Formatted prompt string
        """
        base_prompt = ("You are generating a campaign description for a sales rep. "
                       "Use the provided Salesforce campaign metadata to infer campaign purpose, prospect behavior, and recommended rep follow-up. "
                       "CRITICAL FORMATTING: Output exactly 3 lines, each starting with '• ' (bullet + space) followed by the EXACT category label (enclosed in []), then a colon, then your description.\n"
                       "DO NOT use dashes (-), asterisks (*), bold formatting (**), numbers, or any other bullet style.\n"
                       "NEVER use colons (:) or dashes (-) anywhere in your descriptions - only the single colon after the category label is allowed.\n"
                       "DO NOT REPEAT raw metadata verbatim.\n"
                       "DO NOT REPEAT the campaign name.\n"
                       "Always mention the product interest if it's available.\n"
                       "Write with the goal of helping a sales rep understand the prospect's mindset and how to follow up.\n"
                       "Example format: • [Source]: Selected from high-intent prospect database targeting US market.\n\n"
                       "Answer these questions for a sales rep:\n")
        
        if prompt_type == 'sales_generated':
            specific_prompt = ("• [Source]: What was the sales sourcing method? Explain why this contact was selected for outreach.\n"
                             "• [Data Origin]: What is the prospect profile and qualification criteria that made them a target?\n"
                             "• [Approach]: What are specific cold outreach tactics, timing, and personalization strategies a sales rep should take?\n"
                             "Focus on the sales context and potential fit not prospect behavior (since they haven't engaged).\n")
        
        elif prompt_type == 'partner_referral':
            specific_prompt = ("• [Referral Source]: What type of partner is this and what credibility or context does that provide?\n"
                             "• [Fit/Alignment]: What does the referral or campaign suggest about product fit, integration needs, or ecosystem alignment?\n"
                             "• [Leverage]: What is the product being promoted? Explain how to use partner credibility to guide outreach.\n"
                             "Focus on leveraging the referral trust and highlighting integration or ecosystem relevance.\n")
        
        elif prompt_type == 'existing_customer':
            specific_prompt = ("• [Customer Status]: What is the current status of this existing customer?\n"
                             "• [Exploration]: What is the level of expansion readiness and what specific upsell/cross-sell products could the existing customer be interested in based on current gaps or growth needs?\n"
                             "• [Framing]: How can the conversation be framed for the conversion as an upsell or expansion opportunity?\n"
                             "Focus on growth opportunity and product fit based on existing usage.\n")
        
        elif prompt_type == 'events':
            specific_prompt = ("• [Participation]: What did the prospect attend? A live event or self submitted interest?\n"
                             "• [Signal]: What does this action suggest about their buying stage and solution priorities based on event engagement?\n"
                             "• [Engagement Style]: How should a sales rep follow up in a relationship driven or consultative way?\n"
                             "Focus on event context and tailoring outreach around shared experience or learning goals.\n")
        
        elif prompt_type == 'high_intent':
            specific_prompt = ("• [Search Behavior]: What does the lead's search activity or website visit reveal about their interest or intent?\n"
                             "• [Trigger]: What keyword or campaign may have triggered the engagement?\n"
                             "• [Urgency]: How can a sales rep tailor outreach based on urgency or solution comparison?\n"
                             "Focus on urgency, buyer readiness, and solution fit.\n")
        
        elif prompt_type == 'retargeting_nurture':
            specific_prompt = ("• [Re-Engagement]: Why did the prospect re-engage or how have they been nurtured over time?\n"
                             "• [Resonance]: What content or messaging likely captured their interest?\n"
                             "• [Momentum]: How can a sales rep re-engage them based on slow building awareness or curiosity?\n"
                             "Focus on gradual intent signals and how to move the conversation forward gently.\n")
        
        elif prompt_type == 'awareness_broadcast':
            specific_prompt = ("• [Exposure]: How was the lead passively exposed to a brand campaign or M&A update?\n"
                             "• [Relevance]: Why was the campaign relevant to them?\n"
                             "• [Discovery]: How can a sales rep gauge real interest through a light touch outreach?\n"
                             "Focus on surfacing potential relevance and inviting discovery rather than pushing product.\n")
        
        else:  # regular_marketing (default)
            specific_prompt = ("• [Engagement]: What was the prospect doing when they engaged with this campaign?\n"
                             "• [Intent/Interest]: Why did the prospect engage (their intent or product interest)?\n"
                             "• [Stage]: What does this reveal about the buyer's journey stage?\n"
                             "Focus on the prospect's perspective and intent, not marketing terminology.\n")
        
        # Add URL preservation instruction for all prompts
        url_instruction = "\n\nIMPORTANT: If the campaign details mention any URLs or websites, preserve the domain name in your description."
        
        return f"{base_prompt}{specific_prompt}{url_instruction}\n\nCampaign Information:\n{context}"

    def generate_description(self, campaign: pd.Series, context: str) -> Tuple[str, str]:
        """Generate AI description for a single campaign
        
        Args:
            campaign: Campaign data as pandas Series
            context: Enriched context string
            
        Returns:
            tuple: (description, prompt) - description is the AI response or preview text,
                   prompt is the full prompt that would be sent to OpenAI
        """
        # Determine prompt type based on Channel__c
        prompt_type = self._get_prompt_type(campaign)
        
        # Get tailored prompt
        prompt = self._get_tailored_prompt(prompt_type, context)
        
        if not self.use_openai or self.client is None:
            # Return preview mode response
            campaign_name = campaign.get('Name', 'Unknown')
            if campaign_name is not None:
                preview_description = f"[PROMPT PREVIEW MODE - {prompt_type.upper()}] Campaign: {campaign_name[:50]}..."
            else:
                preview_description = f"[PROMPT PREVIEW MODE - {prompt_type.upper()}] Campaign: Unknown..."
            return preview_description, prompt
        
        # Check if prompt is too long (rough estimate: 1 token ≈ 4 characters)
        estimated_tokens = len(prompt) // 4
        if estimated_tokens > 3500:  # Leave room for response tokens
            logging.warning(f"Prompt may be too long ({estimated_tokens} estimated tokens). Consider reducing campaign context.")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sales enablement expert who helps salespeople understand prospect intent and behavior."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=80,
                temperature=0.3
            )
            
            description = response.choices[0].message.content
            if description is None:
                description = "No description generated"
            else:
                description = description.strip()
            
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
        total_batches = (total_campaigns + batch_size - 1) // batch_size
        
        logging.info(f"Processing {total_campaigns} campaigns in batches of {batch_size}...")
        
        for i in range(0, total_campaigns, batch_size):
            batch_num = (i // batch_size) + 1
            batch_end = min(i + batch_size, total_campaigns)
            batch = campaigns.iloc[i:batch_end]
            
            logging.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} campaigns)...")
            
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
            
            logging.info(f"Completed batch {batch_num}/{total_batches}")
            
            # Log progress for large batches every 5 batches
            if batch_num % 5 == 0 and total_batches > 5:
                logging.info(f"Progress: {batch_num}/{total_batches} batches completed ({i + len(batch)}/{total_campaigns} campaigns)")
        
        logging.info(f"Successfully processed all {total_campaigns} campaigns")
        
        return campaigns 