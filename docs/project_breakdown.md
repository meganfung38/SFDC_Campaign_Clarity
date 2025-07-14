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
* Output– excel reports with AI generated campaign descriptions   
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
| Description | Campaign description |
| BMID\_\_c | Business marketing ID |
| Id | Campaign identifier  |
| Name | Campaign title |
| Intended\_Country\_\_c | Target geographic market for campaign |
| Non\_Attributable\_\_c | Attribution tracking True– Cannot directly trace leads back to this campaign (lead may have been influenced by campaign) False– Can clearly track that a lead came from this specific campaign (clear cause \+ effect) |
| Program\_\_c  | Parent marketing program |
| Short\_Description\_for\_Sales\_\_c | Concise sales focused campaign summary (TO IMPROVE)  |

2. Problem Analysis \+ Campaign Contextual Enrichment  
* Context enrichment: transform raw SFDC data into human readable context using field mappings   
* Channel analysis: determine if campaign channel is:   
  * Sales generated  
  * Regular Marketing 

    

3. AI Driven Enhancement  
* Send enriched marketing data to openai to generate sales friendly descriptions targeting: 

| Sales Generated Campaign (Special Prompt)  | Regular Marketing Campaign (Default)  |
| :---- | :---- |
| Focus: sales sourced contact (not from prospect engagement)  Explain data source \+ suggest cold outreach approach  Emphasize fit assessment  | Focus: what the prospect was doing when they engaged  Analyze prospect intent \+ buyer’s journey stage  Emphasize prospect behavior  |
| Prompt:  Help a salesperson understand:  This is a sales-sourced contact (not from prospect engagement)  The data source and why this contact was identified  What approach might work best for cold outreach  Focus on the sales context and potential fit, not prospect behavior (since they haven’t engaged).  | Prompt:  Help a salesperson understand:  What the prospect was doing when they engaged with this campaign  Why they likely engaged (their intent/ interest)  What this tells us about their buyer’s journey stage  Focus on the prospect’s perspective and intent, not marketing terminology.  |

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