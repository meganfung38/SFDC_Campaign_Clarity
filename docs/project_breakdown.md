## **Project 2– SFDC Campaign Clarity Enhancement**

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
* Steps:   
1. Campaign Metadata Collection   
* Pull existing campaign records from SFDC, focusing on:   
  * Campaign name   
  * Description   
  * Type, status, dates  
  * Engagement metrics (if available)   
2. Problem Analysis   
* Identify inconsistencies or vague terms in current descriptions   
* Categorize problems: overly technical, too generic, etc.   
3. AI Driven Enhancement  
* Use an LLM pipeline to:   
  * Rewrite campaign descriptions in clear, concise, and rep friendly language   
  * Standardize format and highlight key purpose/ value of campaign   
4. Validation \+ Pilot (optional)   
* Select a subset of campaigns and show both original and AI cleaned versions to stakeholders (sales reps, managers)   
* Gather feedback on clarity \+ usefulness   
* Adjust prompt logic or formatting as needed

### **Starter Code**

* Goal– transform technical marketing campaign data into actionable sales insights to help sales understand prospect behavior and tailor their approach accordingly. This enhancement is essential for sales enablement, bridging the gap between marketing campaigns and sales conversations.   
* context\_mappings.json– basic campaign field mappings (field names : basic descriptions)  
* context\_mappings\_refined.json– comprehensive field mappings   
  * Field names map to:   
    * what each channel means for prospect behavior \+ intent  
    * Business context for different campaign types \+ themes   
    * Strategic insights about buyer journey stages   
    * Company size contexts \+ vendor information   
    * What this tells us about the prospect  
* generate\_campaign\_descriptions.py– AI driven tool that generates campaign descriptions   
  * Data pipeline– extract SFDC campaign data → call openai API endpoint with structured system prompt to generate descriptions  
    * Caches descriptions to avoid re-querying SFDC data   
  * Input– campaigns from last 12 months with recent members   
  * Output– excel reports with AI generated campaign descriptions   
    * Summarizes what the prospect was doing when they engaged with the campaign   
    * Likely intent \+ buyer journey   
    * How to approach campaigns effectively   
1. Query SFDC for campaigns with CampaignMember(s) created in the last year (only process campaigns that are actively being interacted with)   
* CampaignMember– anyone who engaged with a marketing campaign (SFDC objects: Lead, Contact, Account)   
2. For each active campaign, query SFDC for marketing data   
3. Use field mappings to enrich raw field values for business context  
4. Send enriched marketing data to openai to generate sales friendly descriptions targeting:   
* Intent recognition  
* Buyer profile  
* Pain points   
* Sales strategy   
* Conversation starter  
5. Output AI descriptions alongside original data in an excel export 