# SFDC Campaign Clarity

## Overview

SFDC Campaign Clarity is an AI-powered tool that transforms Salesforce marketing campaign data into sales-friendly prospect intelligence. Instead of seeing technical marketing jargon, salespeople get clear explanations of **why** prospects engaged with campaigns and **how** to approach them effectively.

## What It Does

The system analyzes Salesforce campaigns with recent member activity and creates **tailored AI descriptions** using 8 different prompt strategies based on channel type.

**Channel-Specific Approaches:**
- **Sales-Generated**: Cold outreach strategy (source, data origin, approach)
- **Partner Referral**: Leverage referral trust (referral source, fit/alignment, leverage)
- **Existing Customer**: Upsell opportunity framing (customer status, exploration, framing)
- **Events**: Relationship building (participation, signal, engagement style)
- **High-Intent**: Urgency emphasis (search behavior, trigger, urgency)
- **Retargeting/Nurture**: Gradual re-engagement (re-engagement, resonance, momentum)
- **Awareness Broadcast**: Light discovery touch (exposure, relevance, discovery)
- **Regular Marketing**: Buyer journey focus (engagement, intent/interest, stage)

## Example Transformation

**Before** (Raw Salesforce Data):
```
Campaign: Saasquatch_Verbal_USCA
Channel: Referrals
Type: Email Only
```

**After** (AI-Generated Sales Intelligence):
```
• [Referral Source]: Customer/partner referral with high trust and warm introduction
• [Fit/Alignment]: Strong recommendation indicates pre-qualification and product fit  
• [Leverage]: Approach confidently - likely ready for consultative conversation
• [⚠️ ALERT]: Review critical handling instructions in Campaign Description field before proceeding
• [Outreach Sequence]: [REX SMB Nurture 2025 Outreach](https://web.outreach.io/sequences/4752/overview)
```

**Enhanced Context** (BMID Translation):
```
Business Marketing ID: DGSMBREXNRNFF (Demand Gen Small Business Email 
(EE Size: <= 99) RingEX Content Nurture Email Send Non Form Fills - Campaigns for Click Scoring)
```

## Quick Start

### 1. Setup
```bash
# Clone and setup
git clone <repository-url>
cd SFDC_Campaign_Clarity
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env with your Salesforce and OpenAI credentials
```

**⚠️ Required Field Mappings**: The field mapping files (`data/field_mappings.json`) are not included in the public repository as they contain sensitive RingCentral business information. **Request these files from [megan.fung@ringcentral.com](mailto:megan.fung@ringcentral.com)** and place them in the `data/` directory before running the system.

### 2. Choose Your Use Case

#### **Full Campaign Processing**
```bash
# Test run (no costs, preview mode)
python campaign_report.py --no-openai --member-limit 100

# Small AI test (~$0.05)
python campaign_report.py --member-limit 200

# Standard production run (1000 members, 12 months)
python campaign_report.py

# Custom time window
python campaign_report.py --months-back 6          # Last 6 months only
python campaign_report.py --months-back 18         # Extended 18-month window

# Full data extraction
python campaign_report.py --member-limit 0         # No member limit
```

#### **Single Campaign Analysis**
```bash
# Analyze specific campaign
python single_campaign_report.py "0013600000XYZ123"

# Preview mode (no AI costs)
python single_campaign_report.py "0013600000ABC456" --no-openai

# Custom output location
python single_campaign_report.py "0013600000XYZ123" --output-dir ./analysis
```

### 3. Results
- **Single Excel Report**: Complete data with AI descriptions and performance metrics
- **Two Sheets**: Campaign Data + Processing Summary
- **Sample Report**: [Google Sheets Sample](https://docs.google.com/spreadsheets/d/1RsaqgahLR8YOj14IiohXO4G8K0v1C2jkpXMHJGa7ay4/edit?usp=sharing) *(RingCentral email required)*

## Key Features

### **🤖 AI-Powered Intelligence**
- **8 Specialized Prompts**: Channel-tailored descriptions for different engagement types
- **Context Enrichment**: 22 Salesforce fields transformed into business insights
- **BMID Translation**: Business Marketing IDs decoded into readable descriptions
- **Critical Alert Detection**: Automatic warnings for campaigns requiring special handling
- **Outreach Sequence Routing**: Smart recommendations for follow-up sequences
- **Flexible Time Windows**: Configurable lookback periods (6, 12, 18+ months)
- **Quality Control**: Optimized for 255-character descriptions with proper formatting

### **📊 Professional Reporting**
- **Single Excel File**: Everything in one report with RingCentral branding
- **16 Key Metrics**: Processing performance and business intelligence
- **Smart Layout**: Raw data first, then AI insights and recommendations

### **⚡ Optimized Performance**
- **Intelligent Caching**: Exact time-window matching prevents data mixing
- **Batch Processing**: Configurable sizes for optimal performance
- **Rate Limiting**: Respects API limits with proper throttling

## Command Line Options

### **Main System**
```bash
# Basic usage
python campaign_report.py                          # Standard 12-month, 1000-member run
python campaign_report.py --help                   # See all options

# Time windows
python campaign_report.py --months-back 6          # 6-month lookback
python campaign_report.py --months-back 24         # Extended 24-month window

# Data control
python campaign_report.py --member-limit 500       # Limit to 500 members
python campaign_report.py --member-limit 0         # No member limit
python campaign_report.py --no-openai              # Preview mode (no AI costs)

# Cache management
python campaign_report.py --no-cache               # Force fresh data
python campaign_report.py --clear-cache            # Clear cache and exit

# Performance tuning
python campaign_report.py --batch-size 5           # Smaller batches
python campaign_report.py --output-dir ./reports   # Custom output location
```

### **Single Campaign Analysis**
```bash
# Basic usage
python single_campaign_report.py "CAMPAIGN_ID"     # Full AI analysis
python single_campaign_report.py --help            # See all options

# Options
python single_campaign_report.py "CAMPAIGN_ID" --no-openai  # Preview mode
python single_campaign_report.py "CAMPAIGN_ID" --no-save    # Display only
python single_campaign_report.py "CAMPAIGN_ID" --output-dir ./analysis
```

## Required Credentials

Create `.env` file with:
```bash
# Salesforce
SF_USERNAME=your.email@company.com
SF_PASSWORD=your_password
SF_SECURITY_TOKEN=your_security_token
SF_DOMAIN=login  # or 'test' for sandbox

# OpenAI
OPENAI_API_KEY=sk-your-api-key
```

## Business Value

### **For Sales Teams**
- **Faster Qualification**: Understand prospect intent immediately
- **Better Conversations**: Know engagement context and approach strategy
- **Improved Conversion**: Match approach to buyer journey stage
- **Rich Context**: 21 enriched data points for deeper insights

### **For Sales Operations**
- **Scalable Processing**: Handle hundreds of campaigns automatically
- **Performance Tracking**: Monitor efficiency and success rates
- **Data Quality**: Attribution tracking and campaign effectiveness insights
- **Cost Optimization**: Single comprehensive report reduces complexity

## Testing Strategy

| Test Type | Command | Time | Cost | Purpose |
|-----------|---------|------|------|---------|
| **Structure** | `--no-openai --member-limit 50` | 30s | $0 | Verify data flow |
| **AI Sample** | `--member-limit 100` | 2-3 min | ~$0.05 | Test AI generation |
| **Medium** | `--member-limit 500` | 5-10 min | ~$0.20 | Full feature test |
| **Production** | `(default settings)` | 1-3 hours | $10-30 | Complete processing |

## Cache Behavior

The system uses intelligent caching with **exact time-window matching**:
- ✅ **Cache Hit**: Request matches cached time period (e.g., 12mo cache → 12mo request)
- ❌ **Cache Miss**: Different time periods (e.g., 12mo cache → 6mo request)
- **Why**: Ensures you get exactly the campaign scope you want, not broader datasets

## Troubleshooting

### **Common Issues**
1. **Missing Field Mappings**: Error loading `data/field_mappings.json` - Request files from [megan.fung@ringcentral.com](mailto:megan.fung@ringcentral.com)
2. **Import Errors**: Activate virtual environment (`source venv/bin/activate`)
3. **Credential Issues**: Check `.env` file format and values
4. **API Rate Limits**: Use smaller `--batch-size` or longer delays
5. **No Data Found**: Verify date ranges and campaign member creation dates
6. **Cache Issues**: Use `--clear-cache` to reset

### **Debug Commands**
```bash
# Test configuration
python campaign_report.py --no-openai --member-limit 50

# Clear stale cache
python campaign_report.py --clear-cache

# Check logs
tail -f logs/campaign_report.log
```

## Architecture

```
📊 Salesforce → 🔄 Context Enrichment → 🤖 AI Processing → 📈 Excel Report
```

**Core Components:**
- `salesforce_client.py`: Data extraction with configurable time windows
- `openai_client.py`: AI generation with channel-specific prompts
- `context_manager.py`: Field mapping and context enrichment
- `cache_manager.py`: Intelligent caching with exact time-window matching
- `excel_operations.py`: Professional report generation

## Documentation

- **Technical Details**: [`docs/project_structure.md`](docs/project_structure.md)
- **Field Mappings**: `data/field_mappings.json` *(request from [megan.fung@ringcentral.com](mailto:megan.fung@ringcentral.com))*
- **Project Overview**: [`docs/project_breakdown.md`](docs/project_breakdown.md)
- **Sample Output**: [Google Sheets Sample](https://docs.google.com/spreadsheets/d/1RsaqgahLR8YOj14IiohXO4G8K0v1C2jkpXMHJGa7ay4/edit?usp=sharing) *(RingCentral email required)*
- **Feedback Samples**: `feedback_+_samples/` - Individual campaign descriptions reviewed with RC employees
  - **Email Campaign Samples**: 
    - [`701Hr000001L82yIAC_REVISED.txt`](feedback_+_samples/samples/701Hr000001L82yIAC_REVISED.txt)
    - [`701Hr000001L8QHIA0_SAMPLE.txt`](feedback_+_samples/samples/701Hr000001L8QHIA0_SAMPLE.txt)
  - **Content Syndication Sample**: [`701TU00000ayWTJYA2_SAMPLE.txt`](feedback_+_samples/samples/701TU00000ayWTJYA2_SAMPLE.txt)

---

**Internal Use Only** - RingCentral Marketing Automation Tool
