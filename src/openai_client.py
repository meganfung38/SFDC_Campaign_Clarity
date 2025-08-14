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
        """Determine the appropriate prompt type based on BMID__c keywords first, then Channel__c value
        
        Args:
            campaign: Campaign data as pandas Series
            
        Returns:
            Prompt type string
        """
        # First check BMID__c for existing customer keywords (case insensitive)
        bmid = campaign.get('BMID__c', '') or ''
        bmid = bmid.strip()
        if bmid:
            bmid_lower = bmid.lower()
            existing_customer_keywords = ['cm', 'pendo', 'upsell', 'adoption']
            
            # Check if any existing customer keyword is contained in BMID
            for keyword in existing_customer_keywords:
                if keyword in bmid_lower:
                    return 'existing_customer'
        
        # Fall back to channel-based routing
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
                       "CRITICAL LENGTH: Each bullet should be 100-160 characters.Total response MUST BE UNDER 400 characters.\n"
                       "DO NOT use dashes (-), asterisks (*), bold formatting (**), numbers, or any other bullet style.\n"
                       "NEVER use colons (:) or dashes (-) anywhere in your descriptions - only the single colon after the category label is allowed.\n"
                       "DO NOT REPEAT raw metadata verbatim.\n"
                       "DO NOT REPEAT the campaign name.\n"
                       "Always mention the product interest if it's available.\n"
                       "Be extremely concise - every word must add value.\n"
                       "Write with the goal of helping a sales rep understand the prospect's mindset and how to follow up.\n"
                       "Example format: • [Source]: Selected from high-intent prospect database targeting US market.\n"
                       "If a third-party vendor, partner, or syndication platform is involved in the campaign, EXPLICITLY name them in the description. DO NOT USE vague phrases like “third-party sites.” Clear vendor identification improves sales rep understanding of lead context and credibility of the campaign source. The more specific the engagement details, the more actionable the output becomes. When possible, pull the exact asset name to enhance intent accuracy. This level of specificity helps reps prioritize follow-up and position the product more effectively.\n"
                       "PRIORITIZE information from the Campaign description, Concise sales focused campaign summary, and Business Marketing ID fields. Your goal is to transform technical or unclear descriptions into clear, concise, and sales-ready summaries that highlight what the campaign represents. Ensure that all relevant content from these fields is thoughtfully incorporated and reflected in the final output.\n\n"
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
            specific_prompt = ("• [Engagement]: Why did the prospect engage or how have they been nurtured over time?\n"
                             "• [Resonance]: What content or messaging likely captured their interest?\n"
                             "• [Momentum]: How can a sales rep engage them based on slow building awareness or curiosity?\n"
                             "Focus on gradual intent signals and how to move the conversation forward gently.\n")
        
        elif prompt_type == 'awareness_broadcast':
            specific_prompt = ("• [Exposure]: How was the lead passively exposed to a brand campaign or M&A update?\n"
                             "• [Relevance]: Why was the campaign relevant to them?\n"
                             "• [Discovery]: How can a sales rep gauge real interest through a light touch outreach?\n"
                             "Focus on surfacing potential relevance and inviting discovery rather than pushing product.\n")
        
        else:  # regular_marketing (default)
            specific_prompt = ("• [Engagement]: What was the prospect doing when they engaged with this campaign?\n"
                             "• [Intent/Interest]: Why did the prospect engage (their intent or product interest)?\n"
                             "• [Next Steps]: What specific action(s) should the rep take now based on this engagement (e.g., how to follow up, what angle to take, or what kind of conversation to initiate)?\n"
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
            
            # Check for critical instructions and append alert even in preview mode
            preview_description = self._append_critical_alert(campaign, preview_description)
            
            # Check for outreach sequence and append even in preview mode
            preview_description = self._append_outreach_sequence(campaign, preview_description)
            
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
                max_tokens=120,
                temperature=0.3
            )
            
            description = response.choices[0].message.content
            if description is None:
                description = "No description generated"
            else:
                description = description.strip()
            
            # Check for critical instructions and append alert if needed
            description = self._append_critical_alert(campaign, description)
            
            # Check for outreach sequence and append if needed
            description = self._append_outreach_sequence(campaign, description)
            
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
    
    def _append_critical_alert(self, campaign: pd.Series, description: str) -> str:
        """Check for critical instruction keywords and append alert if needed
        
        Args:
            campaign: Campaign data as pandas Series
            description: AI-generated description
            
        Returns:
            Description with critical alert appended if needed
        """
        # Define keywords that indicate critical instructions
        critical_keywords = [
            "MUST READ", "IMPORTANT", "CRITICAL", "ATTENTION", "WARNING",
            "***", "!!!", "REQUIRED", "MANDATORY", "URGENT"
        ]
        
        # Fields to check for critical instructions
        fields_to_check = [
            ('Description', 'Campaign Description'),
            ('Short_Description_for_Sales__c', 'Concise Sales Summary')
        ]
        
        critical_fields_found = []
        
        for field_name, display_name in fields_to_check:
            field_value = campaign.get(field_name, '')
            if field_value and isinstance(field_value, str):
                field_upper = field_value.upper()
                
                # Check if any critical keywords are present
                if any(keyword in field_upper for keyword in critical_keywords):
                    critical_fields_found.append(display_name)
                    logging.info(f"Critical instructions detected in {field_name} for campaign {campaign.get('Id', 'Unknown')}")
        
        # If critical instructions found, append alert
        if critical_fields_found:
            if len(critical_fields_found) == 1:
                alert_text = f"• [⚠️ ALERT]: Review critical handling instructions in {critical_fields_found[0]} field before proceeding"
            else:
                fields_text = " and ".join(critical_fields_found)
                alert_text = f"• [⚠️ ALERT]: Review critical handling instructions in {fields_text} fields before proceeding"
            
            # Append the alert to the description
            description = description.rstrip() + '\n' + alert_text
            
            logging.info(f"Critical alert appended to campaign {campaign.get('Id', 'Unknown')}: {alert_text}")
        
        return description
    
    def _append_outreach_sequence(self, campaign: pd.Series, description: str) -> str:
        """Check for appropriate outreach sequence and append if found
        
        Args:
            campaign: Campaign data as pandas Series
            description: AI-generated description
            
        Returns:
            Description with outreach sequence appended if found
        """
        try:
            # Import here to avoid circular imports
            from context_manager import ContextManager
            
            # Create context manager instance to determine outreach sequence
            context_manager = ContextManager()
            sequence_info = context_manager.determine_outreach_sequence(campaign)
            
            if sequence_info:
                if 'sequences' in sequence_info:
                    # Handle multiple sequences (for EE Size = 'Any')
                    sequence_texts = []
                    for seq in sequence_info['sequences']:
                        sequence_texts.append(f"• [Outreach Sequence]: [{seq['name']}]({seq['url']})")
                    sequence_text = '\n'.join(sequence_texts)
                    description = description.rstrip() + '\n' + sequence_text
                    
                    logging.info(f"Multiple outreach sequences appended to campaign {campaign.get('Id', 'Unknown')}: {len(sequence_info['sequences'])} sequences")
                else:
                    # Handle single sequence
                    sequence_text = f"• [Outreach Sequence]: [{sequence_info['name']}]({sequence_info['url']})"
                    description = description.rstrip() + '\n' + sequence_text
                    
                    logging.info(f"Outreach sequence appended to campaign {campaign.get('Id', 'Unknown')}: {sequence_info['name']}")
            else:
                logging.info(f"No outreach sequence determined for campaign {campaign.get('Id', 'Unknown')}")
                
        except Exception as e:
            logging.error(f"Error determining outreach sequence for campaign {campaign.get('Id', 'Unknown')}: {e}")
        
        return description 