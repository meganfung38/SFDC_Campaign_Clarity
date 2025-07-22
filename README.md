# SFDC Campaign Clarity

## Overview

SFDC Campaign Clarity is an AI-powered tool that transforms Salesforce marketing campaign data into sales-friendly prospect intelligence. Instead of seeing technical marketing jargon, salespeople get clear explanations of **why** prospects engaged with campaigns and **how** to approach them effectively.

## What It Does

The system analyzes Salesforce campaigns that have generated leads in the last 12 months and creates **tailored AI descriptions** with focused bullet points.

**8 Different Prompt Strategies** based on Channel type:
- **Sales-Generated**: Focus on data source and cold outreach approach (source, data origin, approach)
- **Partner Referral**: Leverage referral trust and integration potential (referral source, fit/ alignment, leverage)
- **Existing Customer**: Frame as upsell/expansion opportunity (customer status, exploration, framing)
- **Events**: Use shared experience for relationship building (participation, signal, engagement style)
- **High-Intent**: Emphasize urgency and solution comparison (re-engagement, resonance, momentum)
- **Retargeting/Nurture**: Re-engage based on gradual interest signals (search behavior, trigger, urgency)
- **Awareness Broadcast**: Light touch to gauge real interest (exposure, relevance, discovery)
- **Regular Marketing**: Focus on prospect perspective and buyer journey (engagement, intent/ interest, stage)

## Example Transformation

**Before** (Raw Salesforce Data):
```
Campaign: Saasquatch_Verbal_USCA
Channel: Referrals
Type: Email Only
```

**After** (AI-Generated Sales Intelligence):
```
AI Description: 
• Customer/partner referral with high trust level and warm introduction context
• Strong recommendation from trusted source indicates pre-qualification 
• Approach with confidence - likely ready for consultative conversation
```

## Key Features

### **🤖 AI-Powered Intelligence**
- **Smart Campaign Analysis**: Processes campaigns with recent prospect engagement (last 12 months)
- **Channel-Tailored Descriptions**: Each description uses focused bullet points optimized for the specific channel type
- **Context-Aware Descriptions**: Uses 21 Salesforce fields with intelligent field mappings
- **8 Specialized Prompt Strategies**: Different approaches based on Channel__c values (sales-generated, partner referral, existing customer, events, high-intent, retargeting/nurture, awareness broadcast, regular marketing)
- **Rich Context Mapping**: Transforms raw values like "Referrals" into business insights

### **📊 Enhanced Reporting**
- **Single Comprehensive Report**: Everything in one Excel file with two focused sheets
- **RingCentral Branding**: Professional reports with company color scheme (#0684BC)
- **Intelligent Column Layout**: Raw Salesforce data first, then AI prompt and channel-tailored description
- **16 Comprehensive Metrics**: Processing performance and business intelligence tracking

### **⚡ Performance Optimized**
- **Intelligent Caching**: Avoids re-querying Salesforce with smart cache management
- **Batch Processing**: Configurable batch sizes for optimal performance
- **Rate Limiting**: Respects OpenAI API limits with proper throttling
- **Processing Time Tracking**: Monitor performance and cost efficiency

### **🛠️ Developer Friendly**
- **Modular Architecture**: 7 focused modules with clear responsibilities
- **Fixed Field Mappings**: Robust JSON parsing and context enrichment
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Flexible Configuration**: Command-line options for testing and production

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

### 2. Choose Your Use Case

#### **Full Campaign Processing**
```bash
# Quick test (no OpenAI cost, limited data)
python campaign_report.py --no-openai --member-limit 100

# Small AI test (~$0.05, limited data)  
python campaign_report.py --member-limit 200

# Production run (default 1000 member limit)
python campaign_report.py

# Full data extraction (unlimited)
python campaign_report.py --member-limit 0
```

#### **Single Campaign Analysis**
```bash
# Analyze specific campaign by ID
python single_campaign_report.py "0013600000XYZ123"

# Preview mode (no OpenAI cost)
python single_campaign_report.py "0013600000ABC456" --no-openai

# Using 18-character campaign ID
python single_campaign_report.py "0013600000XYZ123456"
```

### 3. View Results
- **Single Excel Report**: Complete campaign data with channel-tailored AI descriptions and processing summary
- **Two Focused Sheets**: Campaign Data + Processing Summary with 16 key metrics
- **Sample Reports**: 
  - Campaign reports: [`docs/sample_report.xlsx`](docs/sample_report.xlsx)

## Architecture

```
📊 Salesforce Data → 🔄 Context Enrichment → 🤖 AI Processing → 📈 Professional Report
```

### Core Components
- **`salesforce_client.py`**: Salesforce API operations and data extraction
- **`openai_client.py`**: AI description generation with rate limiting
- **`context_manager.py`**: Field mapping and business context enrichment (21 fields)
- **`excel_operations.py`**: Professional single-file report generation
- **`campaign_processor.py`**: Main orchestration and workflow management
- **`cache_manager.py`**: Performance optimization through intelligent caching

## Enhanced Metrics & Analytics

The system tracks comprehensive metrics for business intelligence:

### **Processing Performance (8 Metrics)**
- Total campaigns queried vs processed
- Processing time and throughput  
- AI success rate and error tracking
- Average description quality metrics

### **Business Intelligence (8 Metrics)**
- Campaign distribution by channel, vertical, and territory
- Attribution tracking analysis (direct vs indirect)
- Sales-generated vs marketing campaign breakdown
- Product focus and geographic targeting insights

## Report Structure

### **Campaign Data Sheet**
```
Raw Salesforce Data (Priority Fields) → Additional SF Fields → AI Content
Name, Channel, Type, Status...    →    TCP, Vendor, Territory...  →  Prompt → Tailored Description
```

### **Processing Summary Sheet**
- 16 comprehensive performance metrics
- Processing time, success rates, error tracking
- Business intelligence insights (channels, verticals, territories)
- RingCentral professional formatting

## Specialized Tools

### **🔍 Single Campaign Analysis (`single_campaign_report.py`)**
Targeted analysis for specific campaigns by Salesforce ID with direct lookup:

```bash
# Single Campaign Options  
python single_campaign_report.py "0013600000XYZ123"       # 15-character campaign ID
python single_campaign_report.py "0013600000XYZ123456"    # 18-character campaign ID
python single_campaign_report.py "0013600000ABC789" --no-openai  # Preview mode
```

## Command Line Options

### **Main System (`campaign_report.py`)**
```bash
# Testing & Development  
python campaign_report.py --no-openai              # Preview mode (no API costs)
python campaign_report.py --member-limit 100       # Process limited data (faster)
python campaign_report.py --batch-size 5           # Custom batch size

# Production & Performance
python campaign_report.py --member-limit 0         # Process all available data (unlimited)
python campaign_report.py --no-cache               # Force fresh data extraction
python campaign_report.py --output-dir ./reports   # Custom output directory
python campaign_report.py --clear-cache            # Clear cached data

# Advanced Usage
python campaign_report.py --member-limit 500 --batch-size 5 --output-dir ./test_reports
```

## Required Credentials

### **Salesforce**
- `SF_USERNAME`: Your Salesforce username
- `SF_PASSWORD`: Your Salesforce password
- `SF_SECURITY_TOKEN`: From Salesforce Setup → Personal Information → Reset Security Token
- `SF_DOMAIN`: `login` for production, `test` for sandbox

### **OpenAI**
- `OPENAI_API_KEY`: From [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

## Business Value

### **For Sales Teams**
- **Faster Qualification**: Understand prospect intent immediately with channel-tailored insights
- **Better Conversations**: Know why prospects engaged with campaigns using 8 different approach strategies
- **Improved Conversion**: Match approach to buyer journey stage based on channel type
- **Rich Context**: Leverage 21 enriched data points for deeper insights

### **For Sales Operations**
- **Scalable Intelligence**: Process hundreds of campaigns automatically
- **Performance Metrics**: Track processing efficiency and success rates
- **Data Quality**: Monitor attribution tracking and campaign effectiveness
- **Cost Optimization**: Single comprehensive report reduces complexity

## Testing Strategy

| Test Type | Command | Time | Cost | Purpose |
|-----------|---------|------|------|---------|
| **Structure Test** | `--no-openai --member-limit 50` | 30s | $0 | Verify data flow |
| **AI Test** | `--member-limit 100` | 2-3 min | ~$0.05 | Test channel-tailored AI generation |
| **Medium Test** | `--member-limit 500` | 5-10 min | ~$0.20 | Full feature test |
| **Production** | `(no flags or --member-limit 0)` | 1-3 hours | $10-30 | Complete processing |

**Reference Output**: Compare your results with [`docs/sample_report.xlsx`](docs/sample_report.xlsx) to verify proper formatting and structure.

## Recent Enhancements

### **v2.1 Features**
- ✅ **Channel-Tailored Descriptions**: AI descriptions now use 8 different prompt strategies optimized for each channel type
- ✅ **Specialized Prompt Strategy**: Different approaches for sales-generated, partner referral, existing customer, events, high-intent, retargeting/nurture, awareness broadcast, and regular marketing channels
- ✅ **Simplified Excel Export**: Single comprehensive file with 2 focused sheets
- ✅ **Fixed Field Mappings**: Robust context enrichment with proper JSON parsing
- ✅ **Enhanced Context**: "Referrals" → "Customer or partner referral - high trust, warm introduction"
- ✅ **Improved Layout**: Standard row heights and optimal column widths
- ✅ **Processing Integration**: Summary metrics embedded in main report
- ✅ **Error Resolution**: Fixed import issues and package structure

### **v2.0 Features**
- ✅ **RingCentral Branding**: Professional color scheme and formatting
- ✅ **16 Comprehensive Metrics**: Processing performance and business intelligence
- ✅ **Processing Time Tracking**: Monitor efficiency and costs
- ✅ **Intelligent Column Layout**: Raw data first, AI content appended
- ✅ **Package Structure**: Proper imports and modular architecture

## Troubleshooting

### **Common Issues**
1. **Import Errors**: Ensure virtual environment is activated
2. **Credential Issues**: Verify `.env` file configuration
3. **Field Mapping Issues**: Check `data/field_mappings.json` syntax
4. **API Rate Limits**: Use smaller batch sizes or longer delays
5. **No Data Found**: Check date ranges and campaign member creation

### **Debug Commands**
```bash
# Test configuration  
python campaign_report.py --no-openai --member-limit 50

# Clear cache if data seems stale
python campaign_report.py --clear-cache

# Check detailed logs
tail -f logs/campaign_report.log
```

## Technical Specifications

- **Python**: 3.7+
- **Dependencies**: simple-salesforce, openai, pandas, openpyxl
- **Performance**: Processes 100+ campaigns/hour
- **Memory**: Optimized for large datasets
- **Output**: Single Excel file with comprehensive data and metrics

## Documentation

- **Architecture**: [`docs/project_structure.md`](docs/project_structure.md)
- **Field Mappings**: [`data/field_mappings.json`](data/field_mappings.json)
- **Project Details**: [`docs/project_breakdown.md`](docs/project_breakdown.md)
- **Sample Report**: [`docs/sample_report.xlsx`](docs/sample_report.xlsx) - Example of generated output

---

**Internal Use Only** - RingCentral Marketing Automation Tool
