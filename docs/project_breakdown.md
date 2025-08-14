## **Project 2– [SFDC Campaign Clarity Enhancement](https://github.com/meganfung38/SFDC_Campaign_Clarity.git)** 

### **What are SFDC Campaigns?** 

* SFDC campaigns are used to track marketing touchpoints:   
  * Sponsored links   
  * Ads   
  * Outreach efforts   
* Sales reps can tag themselves to campaign records to receive credit for their influence on a lead or opportunity

### **Problem Statement** 

* There is a large volume of campaigns in SFDC that are vaguely described   
* Sales reps often do not know what individual campaigns represent, leading to:   
  * Tagging confusion or avoidance   
  * Under attribution of rep influence   
  * Lower data trust in campaign reporting 

### **Solution** 

* Use AI to clean up and clarify campaign metadata (especially descriptions)   
* Enable reps to quickly understand what a campaign represents so they can confidently tag their influence and use campaign data effectively   
* Transform technical marketing campaign data into actionable sales insights to help sales understand prospect behavior and tailor their approach accordingly. This enhancement is essential for sales enablement, bridging the gap between marketing campaigns and sales conversations   
* Input– campaigns from last 12 months with recent members   
* Output– excel reports with AI generated campaign descriptions + outreach sequencing
* Steps:   
1. Campaign Metadata Collection   
* Pull active campaign records from SFDC– campaigns with CampaignMember(s) created in the last year  
  * CampaignMember– anyone who engaged with a marketing campaign (SFDC objects: Lead, Contact, Account)   
* Query campaign data for each active campaign: 

| Field | Description |
| :---- | :---- |
| Channel\_\_c  | Engagement method  |
| Integrated\_Marketing\_\_c | Cross channel marketing integration indicator |
| Intended\_Product\_\_c  | Product interest  |
| Sub\_Channel\_\_c | Secondary channel |
| Sub\_Channel\_Detail\_\_c | Specific engagement context  |
| TCP\_Campaign\_\_c  | Target customer profile campaign identifier |
| TCP\_Program\_\_c  | Target customer profile program classification |
| TCP\_Theme\_\_c  | Target customer profile and strategy |
| Type  | Campaign format |
| Vendor\_\_c  | Lead source context  |
| Vertical\_\_c | Industry context |
| Marketing\_Message\_\_c | Value proposition focus  |
| Territory\_\_c  | Sales territory assignment |
| Segment\_\_c  | Marketing segment |
| Description | Campaign description |
| BMID\_\_c | Business marketing ID |
| Id | Campaign identifier  |
| Name | Campaign title |
| Intended\_Country\_\_c | Target geographic market for campaign |
| Non\_Attributable\_\_c | Attribution tracking True– Cannot directly trace leads back to this campaign (lead may have been influenced by campaign) False– Can clearly track that a lead came from this specific campaign (clear cause \+ effect) |
| Program\_\_c  | Parent marketing program |
| Short\_Description\_for\_Sales\_\_c | Concise sales focused campaign summary (TO IMPROVE)  |

2. Problem Analysis \+ Campaign Contextual Enrichment  
* Context enrichment: transform raw SFDC data into human readable context using [field mappings](https://docs.google.com/spreadsheets/d/1Z0iVJkz1h0ruPdTsoHWYa2bdpqLAZ643Z3UMoWWFKgg/edit?usp=sharing)
* Outreach sequence routing: inspect BMID and route appropriate outreach sequence (routing included in [field mappings](https://docs.google.com/spreadsheets/d/1Z0iVJkz1h0ruPdTsoHWYa2bdpqLAZ643Z3UMoWWFKgg/edit?usp=sharing))    
* Channel analysis: determine campaign channel and what it reveals


3. AI Driven Enhancement  
* Send enriched marketing data to openai to generate sales friendly descriptions targeting  
* Base Prompt: You are generating a campaign description for a sales rep. Use the provided Salesforce campaign metadata to infer campaign purpose, prospect behavior, and recommended rep follow-up.   
  * CRITICAL FORMATTING: Output exactly 3 lines, each starting with ‘• ‘ (bullet \+ space) followed by the EXACT category label (enclosed in \[\]), then a colon, then your description.  
  * CRITICAL LENGTH: Each bullet should be 100-160 characters. Total response MUST BE UNDER 400 characters.
  * DO NOT use dashes (-), asterisks (\*), bold formatting (\*\*), numbers, or any other bullet style.  
  * NEVER use colons (:) or dashes (-) anywhere in your descriptions– only the single colon after the category label is allowed.   
  * DO NOT REPEAT raw metadata verbatim.  
  * DO NOT repeat the campaign name.  
  * Descriptions should be clear, relevant, quick to read, and under 255 characters total.   
  * Always mention the product interest if it’s available.  
  * Be extremely concise -- every word must add value.  
  * Write with the goal of helping a sales rep understand the prospect’s mindset and how to follow up.   
  * Example format: • [Source]: Selected from high-intent prospect database targeting US market.
  * If a third-party vendor, partner, or syndication platform is involved in the campaign, EXPLICITLY name them in the description. DO NOT USE vague phrases like “third-party sites.” Clear vendor identification improves sales rep understanding of lead context and credibility of the campaign source. The more specific the engagement details, the more actionable the output becomes. When possible, pull the exact asset name to enhance intent accuracy. This level of specificity helps reps prioritize follow-up and position the product more effectively.
  * PRIORITIZE information from the Campaign description, Concise sales focused campaign summary, and Business Marketing ID fields. Your goal is to transform technical or unclear descriptions into clear, concise, and sales-ready summaries that highlight what the campaign represents. Ensure that all relevant content from these fields is thoughtfully incorporated and reflected in the final output. 

Answer these questions for a sales rep: 

| Prompt Variant  | Applicable Channels  | Reasons for Prompt Tailoring  | Tailored Prompt  |
| :---- | :---- | :---- | :---- |
| Regular Marketing Campaign Prompt (DEFAULT) | • Content Syndication<br/>• Web Partners<br/>• Vendor Qualified Leads<br/>• Email<br/>• Direct Mail | • Lead engaged with campaign, indicating interest<br/>• Prospect behavior provides insight into intent and buyer journey | **Engagement**: What was the prospect doing when they engaged with this campaign?<br/>**Intent/Interest**: Why did the prospect engage (their intent or product interest)?<br/>**Next Steps**: What specific action(s) should the rep take now based on this engagement (e.g., how to follow up, what angle to take, or what kind of conversation to initate)?<br/><br/>Focus on the prospect's perspective and intent, not marketing terminology. |
| Sales Generated Prompt | • Sales Generated<br/>• List Purchase<br/>• Appointment Setting<br/>• Sales Agents & Resellers<br/>• Default<br/>• Other | • Contact was sourced by sales not prospect engagement<br/>• Requires cold outreach framing and fit assessment | **Source**: What was the sales sourcing method? Explain why this contact was selected for outreach.<br/>**Data Origin**: What is the prospect profile and qualification criteria that made them a target?<br/>**Approach**: What are specific cold outreach tactics, timing, and personalization strategies a sales rep should take?<br/><br/>Focus on the sales context and potential fit not prospect behavior (since they haven't engaged). |
| Partner-Referral Prompt | • VAR Campaigns<br/>• VAR MDF<br/>• Affiliates<br/>• ISV<br/>• SIA<br/>• Franchise & Assoc.<br/>• Service Providers<br/>• Amazon<br/>• Referrals | • Lead referred through partner, indicating initial trust and possible ecosystem alignment<br/>• Highlight partner value and integration potential | **Referral Source**: What type of partner is this and what credibility or context does that provide?<br/>**Fit/Alignment**: What does the referral or campaign suggest about product fit, integration needs, or ecosystem alignment?<br/>**Leverage**: What is the product being promoted? Explain how to use partner credibility to guide outreach.<br/><br/>Focus on leveraging the referral trust and highlighting integration or ecosystem relevance. |
| Existing Customer Prompt | • Upsell<br/>• BMID__c contains CM, PENDO, UPSELL, OR ADOPTION | • Lead is an existing customer exploring add-ons or upgrades<br/>• Messaging should focus on value expansion | **Customer Status**: What is the current status of this existing customer?<br/>**Exploration**: What is the level of expansion readiness and what specific upsell/cross-sell products could the existing customer be interested in based on current gaps or growth needs?<br/>**Framing**: How can the conversation be framed for the conversion as an upsell or expansion opportunity?<br/><br/>Focus on growth opportunity and product fit based on existing usage. |
| Events Prompt | • Corporate Events<br/>• Field Events<br/>• Events<br/>• Walk On | • Lead engaged via live event or submitted interest directly, indicates relationship readiness or high intent | **Participation**: What did the prospect attend? A live event or self submitted interest?<br/>**Signal**: What does this action suggest about their buying stage and solution priorities based on event engagement?<br/>**Engagement Style**: How should a sales rep follow up in a relationship driven or consultative way?<br/><br/>Focus on event context and tailoring outreach around shared experience or learning goals. |
| Retargeting/Nurture Prompt | • Retargeting<br/>• Prospect Nurturing<br/>• Digital<br/>• LeadGen<br/>• Social Media | • Lead re-engaged or is part of a nurture sequence<br/>• Indicates evolving interest, slow developing intent | **Engagement**: Why did the prospect engage or how have they been nurtured over time?<br/>**Resonance**: What content or messaging likely captured their interest?<br/>**Momentum**: How can a sales rep engage them based on slow building awareness or curiosity?<br/><br/>Focus on gradual intent signals and how to move the conversation forward gently. |
| High Intent Prompt | • Paid Search<br/>• Organic Search | • Lead came through high-intent channels, indicating urgent product search or solution comparison | **Search Behavior**: What does the lead's search activity or website visit reveal about their interest or intent?<br/>**Trigger**: What keyword or campaign may have triggered the engagement?<br/>**Urgency**: How can a sales rep tailor outreach based on urgency or solution comparison?<br/><br/>Focus on urgency, buyer readiness, and solution fit. |
| Awareness Broadcast Prompt | • Media Campaigns<br/>• Mergers & Acquisitions | • Lead was exposed to high level awareness messaging<br/>• Intent is unclear, follow up should clarify interest | **Exposure**: How was the lead passively exposed to a brand campaign or M&A update?<br/>**Relevance**: Why was the campaign relevant to them?<br/>**Discovery**: How can a sales rep gauge real interest through a light touch outreach?<br/><br/>Focus on surfacing potential relevance and inviting discovery rather than pushing product. |

4. Excel Export Results   
* Output AI descriptions alongside original data in an excel export 

5. Validation \+ Pilot (optional)   
* Select a subset of campaigns and show both original and AI cleaned versions to stakeholders (sales reps, managers)   
* Gather feedback on clarity \+ usefulness   
* Adjust prompt logic or formatting as needed

### **Questions**

* Which SFDC fields provide the most meaningful context for understanding campaign intent?   
  * How can I incorporate them into more descriptive, actionable outputs?   
* Can you share examples of strong vs weak campaign descriptions, and explain what makes one more useful to sales than the other?   
* What specific insights or takeaways should every campaign description aim to surface for a sales rep?   
* What are the strategic goals behind enhancing campaign descriptions?   
  * Who is the intended audience? Just sales reps?   
  * What sales motions are they supporting?   
* What internal RC data sources, tools, or teams should I consult to improve the accuracy, depth, or relevance of campaign field mappings?   
* Which field combinations produce the most insightful descriptions when enriched together?   
  * Channel\_\_c \+ Type \+ Intended\_Product\_\_c  
* Should I have tailored prompts for specific field values?   
  * For instance, I currently have two separate prompts for:   
    * Channel\_\_c \= Sales Generated   
    * Channel\_\_c  \!= Sales Generated

### **Marketing Channel Leaders**

* Bernice Wen  
  * Appointment Setting  
  * Content Syndication  
  * Email Prospecting / Email  
  * Vendor Qualified Leads

* Marvin Varee  
  * ABM (Account Based Marketing)

* Tatiana Rybakova  
  * Paid Search

* Sarah Dommerich  
  * Field Events  
  * Corporate Events (Not Sarah, but she might point us to the right person)

* Robert Cleary  
  * Media Campaigns

* Need to Ask, who owns:  
  * Social Media  
  * Retargeting  
  * SIA (Strategic Industry Alliances \- aka other companies we partner with on lead gen like Amazon, Salesforce, Box, etc.)  
  * Upsell