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

Solution 

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