# SFDC Campaign Clarity

## Overview

SFDC Campaign Clarity is an AI-powered tool that transforms Salesforce marketing campaign data into sales-friendly prospect intelligence. Instead of seeing technical marketing jargon, salespeople get clear explanations of **why** prospects engaged with campaigns and **how** to approach them effectively.

## What It Does

The system analyzes Salesforce campaigns that have generated leads in the last 12 months and creates AI-generated descriptions that help sales teams understand:

- **What the prospect was doing** when they engaged with the campaign
- **Why they likely engaged** (their intent and interest level)
- **What this tells us about their buyer's journey stage**
- **How to approach them** based on their engagement context

## Example Transformation

**Before** (Raw Salesforce Data):
```
Campaign: Saasquatch_Verbal_USCA
Channel: Referrals
Type: Email Only
```

**After** (AI-Generated Sales Intelligence):
```
AI Description: "Customer or partner referral - high trust, warm introduction. Prospect engaged through verbal referral program, indicating strong recommendation from trusted source. Approach with confidence - they're already pre-qualified and likely ready for consultative conversation."
```

## Key Features

### **🤖 AI-Powered Intelligence**
- **Smart Campaign Analysis**: Processes campaigns with recent prospect engagement (last 12 months)
- **Context-Aware Descriptions**: Uses 21 Salesforce fields with intelligent field mappings
- **Tailored Prompt Strategy**: 8 specialized AI prompts based on Channel__c values with numbered bullet points for clarity (sales-generated, partner referral, existing customer, events, high-intent, retargeting/nurture, awareness broadcast, regular marketing)
- **Rich Context Mapping**: Transforms raw values like "Referrals" into business insights

### **📊 Enhanced Reporting**
- **Single Comprehensive Report**: Everything in one Excel file with two focused sheets
- **RingCentral Branding**: Professional reports with company color scheme (#0684BC)
- **Intelligent Column Layout**: Raw Salesforce data first, then AI prompt and description
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

### 2. Test Run
```bash
# Quick test (no OpenAI cost)
python main.py --no-openai --limit 5

# Small AI test (~$0.05)
python main.py --limit 3

# Production run
python main.py
```

### 3. View Results
- **Single Excel Report**: Complete campaign data with AI descriptions and processing summary
- **Two Focused Sheets**: Campaign Data + Processing Summary with 16 key metrics
- **Sample Output**: See [`docs/sample_report.xlsx`](docs/sample_report.xlsx) for example report structure

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
Name, Channel, Type, Status...    →    TCP, Vendor, Territory...  →  Prompt → Description
```

### **Processing Summary Sheet**
- 16 comprehensive performance metrics
- Processing time, success rates, error tracking
- Business intelligence insights (channels, verticals, territories)
- RingCentral professional formatting

## Command Line Options

```bash
# Testing & Development
python main.py --no-openai              # Preview mode (no API costs)
python main.py --limit 10               # Process only 10 campaigns
python main.py --batch-size 5           # Custom batch size

# Production & Performance
python main.py --no-cache               # Force fresh data extraction
python main.py --output-dir ./reports   # Custom output directory
python main.py --clear-cache            # Clear cached data

# Advanced Usage
python main.py --limit 20 --batch-size 5 --output-dir ./test_reports
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
- **Faster Qualification**: Understand prospect intent immediately
- **Better Conversations**: Know why prospects engaged with campaigns
- **Improved Conversion**: Match approach to buyer journey stage
- **Rich Context**: Leverage 21 enriched data points for deeper insights

### **For Sales Operations**
- **Scalable Intelligence**: Process hundreds of campaigns automatically
- **Performance Metrics**: Track processing efficiency and success rates
- **Data Quality**: Monitor attribution tracking and campaign effectiveness
- **Cost Optimization**: Single comprehensive report reduces complexity

## Testing Strategy

| Test Type | Command | Time | Cost | Purpose |
|-----------|---------|------|------|---------|
| **Structure Test** | `--no-openai --limit 5` | 30s | $0 | Verify data flow |
| **AI Test** | `--limit 3` | 2-3 min | ~$0.05 | Test AI generation |
| **Medium Test** | `--limit 20` | 5-10 min | ~$0.20 | Full feature test |
| **Production** | `(no flags)` | 1-3 hours | $10-30 | Complete processing |

**Reference Output**: Compare your results with [`docs/sample_report.xlsx`](docs/sample_report.xlsx) to verify proper formatting and structure.

## Recent Enhancements

### **v2.1 Features**
- ✅ **Tailored Prompt Strategy**: 8 specialized AI prompts based on Channel__c values with intelligent fallback
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
python main.py --no-openai --limit 2

# Clear cache if data seems stale
python main.py --clear-cache

# Check detailed logs
tail -f logs/campaign_description_generation.log
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
