which# SFDC_Campaign_Clarity

## Overview

SFDC_Campaign_Clarity is an AI-powered tool that transforms Salesforce marketing campaign data into sales-friendly prospect intelligence. Instead of seeing technical marketing jargon, salespeople get clear explanations of **why** prospects engaged with campaigns and **how** to approach them effectively.

## What It Does

The system analyzes Salesforce campaigns that have generated leads in the last 12 months and creates AI-generated descriptions that help sales teams understand:

- **What the prospect was doing** when they engaged with the campaign
- **Why they likely engaged** (their intent and interest level)
- **What this tells us about their buyer's journey stage**
- **How to approach them** based on their engagement context

## Example Transformation

**Before** (Raw Salesforce Data):
```
Campaign: Q4 2024 - SEM - RingEX - Non-Brand - Healthcare - Google
Channel: Paid Search
Type: Advertisement
```

**After** (AI-Generated Sales Intelligence):
```
AI Description: "Healthcare prospect actively searched 'business phone system' on Google - high intent buyer comparing UCaaS solutions, likely IT decision maker evaluating HIPAA-compliant options for small practice"
```

## Project Structure

```
SFDC_Campaign_Clarity/
├── README.md                              # 📚 Main documentation
├── requirements.txt                       # 📦 Dependencies
├── .env.example                          # 📋 Environment template (copy to .env)
├── .env                                   # 🔐 Environment variables (gitignored)
├── .gitignore                            # 🚫 Git ignore rules
├── generate_campaign_descriptions.py     # 🐍 Main Python script
├── data/                                 # 📊 Data files
│   ├── context_mappings_refined.json    #   Enhanced field mappings
│   └── context_mappings.json            #   Original field mappings
├── docs/                                 # 📖 Documentation
│   └── project_breakdown.md             #   Detailed project breakdown
├── logs/                                 # 📝 Log files
│   └── campaign_description_generation.log  #   Application logs
├── cache/                                # 💾 Cache directory (auto-created)
└── venv/                                 # 🐍 Virtual environment
```

## Architecture

### Core Components

1. **Context Mapping Files** (`data/context_mappings_refined.json`)
   - Translates technical marketing fields into business context
   - Provides prospect behavior insights for each campaign attribute
   - Enhanced version with sales-focused explanations

2. **Main Processing Script** (`generate_campaign_descriptions.py`)
   - Connects to Salesforce to extract campaign data
   - Enriches raw data with business context
   - Uses OpenAI GPT to generate sales-friendly descriptions
   - Outputs Excel reports with AI descriptions

3. **Data Pipeline Flow**
   ```
   Salesforce Data → Context Enrichment → AI Processing → Excel Report
   ```

### Key Features

- **Smart Campaign Selection**: Only processes campaigns with recent prospect engagement
- **Context Enrichment**: Transforms marketing fields into business intelligence
- **AI-Powered Descriptions**: Uses OpenAI to generate prospect-focused explanations
- **Caching System**: Avoids re-querying Salesforce for performance
- **Batch Processing**: Handles large datasets efficiently
- **Rate Limiting**: Respects OpenAI API limits

## Setup

### Prerequisites

- Python 3.7+
- Salesforce access with appropriate permissions
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SFDC_Campaign_Clarity
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Then edit the `.env` file with your actual credentials:
   ```bash
   # Edit with your preferred editor
   nano .env
   # OR
   code .env
   ```

### Required Credentials

You'll need to obtain the following credentials:

#### **Salesforce Credentials**
- **SF_USERNAME**: Your Salesforce username (email)
- **SF_PASSWORD**: Your Salesforce password
- **SF_SECURITY_TOKEN**: Get this from Salesforce:
  1. Log into Salesforce
  2. Go to **Setup** → **Personal Information** → **Reset My Security Token**
  3. Click **Reset Security Token** (will be emailed to you)
- **SF_DOMAIN**: Use `login` for production, `test` for sandbox

#### **OpenAI API Key**
- **OPENAI_API_KEY**: Get this from OpenAI:
  1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
  2. Create a new secret key
  3. Copy the key (starts with `sk-proj-` or `sk-`)

## Usage

### Basic Usage
```bash
python generate_campaign_descriptions.py
```

### Command Line Options
```bash
# Preview mode (no OpenAI calls)
python generate_campaign_descriptions.py --no-openai

# Force fresh data extraction
python generate_campaign_descriptions.py --no-cache

# Limit campaigns for testing
python generate_campaign_descriptions.py --limit 50

# Clear cache
python generate_campaign_descriptions.py --clear-cache
```

### Output

The script generates an Excel report with:
- AI-generated sales descriptions
- Original campaign data
- Enriched context prompts
- Campaign member counts

## Data Sources

### Salesforce Queries
1. **CampaignMember**: Identifies active campaigns (last 12 months)
2. **Campaign**: Extracts campaign details and attributes

### Campaign Fields Processed
- Channel, Type, Sub-Channel Details
- Intended Product, TCP Theme
- Vertical, Territory, Vendor
- Marketing Messages, Descriptions

## Business Value

### For Sales Teams
- **Faster Qualification**: Understand prospect intent immediately
- **Better Conversations**: Know why prospects engaged
- **Improved Conversion**: Match approach to buyer journey stage

### For Sales Operations
- **Scalable Intelligence**: Process hundreds of campaigns automatically
- **Consistent Messaging**: Standardized prospect insights
- **Data-Driven Coaching**: Understand campaign effectiveness

## Technical Details

### Dependencies
- `simple-salesforce`: Salesforce API integration
- `openai`: AI description generation
- `pandas`: Data processing
- `openpyxl`: Excel report generation

### Performance Considerations
- Batch processing for large datasets
- Caching to reduce Salesforce API calls
- Rate limiting for OpenAI API compliance
- Efficient memory management for large campaigns

## Contributing

1. Update context mappings in `context_mappings_refined.json` to improve business context
2. Enhance AI prompts in the `generate_ai_description` method
3. Add new campaign attributes to the enrichment process
4. Improve output formatting and reporting

## License

Internal use only - Salesforce marketing automation tool
