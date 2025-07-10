# SFDC_Campaign_Clarity

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
├── main.py                               # 🚀 Main entry point
├── src/                                  # 📦 Source code modules
│   ├── __init__.py                       #   Package initialization
│   ├── salesforce_client.py              #   Salesforce API operations
│   ├── openai_client.py                  #   OpenAI API operations  
│   ├── context_manager.py                #   Context mapping & enrichment
│   ├── cache_manager.py                  #   Data caching operations
│   ├── excel_operations.py               #   Excel report generation
│   └── campaign_processor.py             #   Main orchestration class
├── data/                                 # 📊 Data files
│   ├── context_mappings_refined.json     #   Enhanced field mappings
│   └── context_mappings.json             #   Original field mappings
├── docs/                                 # 📖 Documentation
│   ├── project_breakdown.md              #   Detailed project breakdown
│   └── project_structure.md              #   Architecture documentation
├── logs/                                 # 📝 Application logs
├── cache/                                # 💾 Cache files (auto-created)
├── README.md                             # 📚 Main documentation
├── requirements.txt                      # 📦 Python dependencies
├── .env.example                          # 📋 Environment template
├── .env                                  # 🔐 Environment variables (gitignored)
├── .gitignore                            # 🚫 Git ignore rules
└── venv/                                 # 🐍 Virtual environment
```

## Architecture

### Modular Design

The system is built with a modular architecture where each component has a single responsibility:

1. **Context Mapping Files** (`data/context_mappings_refined.json`)
   - Translates technical marketing fields into business context
   - Provides prospect behavior insights for each campaign attribute
   - Enhanced version with sales-focused explanations
   - **📊 Complete Field Mappings**: [View all Salesforce field mappings](https://docs.google.com/spreadsheets/d/1Z0iVJkz1h0ruPdTsoHWYa2bdpqLAZ643Z3UMoWWFKgg/edit?usp=sharing)

2. **Salesforce Client** (`src/salesforce_client.py`)
   - Handles Salesforce authentication and data extraction
   - Manages SOQL queries and API rate limits
   - Extracts campaign members and campaign details

3. **OpenAI Client** (`src/openai_client.py`)
   - Manages OpenAI API interactions
   - Generates AI descriptions with proper prompting
   - Handles rate limiting and batch processing

4. **Context Manager** (`src/context_manager.py`)
   - Loads and manages field mappings
   - Enriches campaign data with business context
   - Transforms technical fields into sales intelligence

5. **Cache Manager** (`src/cache_manager.py`)
   - Optimizes performance with intelligent caching
   - Manages campaign ID cache with expiration
   - Provides cache utilities and information

6. **Excel Operations** (`src/excel_operations.py`)
   - Generates formatted Excel reports
   - Creates summary reports with statistics
   - Handles column ordering and styling

7. **Campaign Processor** (`src/campaign_processor.py`)
   - Main orchestration and workflow management
   - Coordinates all components
   - Handles error management and status reporting

8. **Main Entry Point** (`main.py`)
   - Command-line interface
   - Argument parsing and validation
   - Environment variable checking
   - Process execution and user feedback

### Data Pipeline Flow
```
Salesforce Data → Context Enrichment → AI Processing → Excel Report
```

### Key Features

- **Smart Campaign Selection**: Only processes campaigns with recent prospect engagement
- **Context Enrichment**: Transforms marketing fields into business intelligence
- **AI-Powered Descriptions**: Uses OpenAI to generate prospect-focused explanations
- **Intelligent Caching**: Avoids re-querying Salesforce for performance
- **Batch Processing**: Handles large datasets efficiently
- **Rate Limiting**: Respects OpenAI API limits
- **Modular Architecture**: Easy to maintain and extend

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
python main.py
```

### Command Line Options
```bash
# Preview mode (no OpenAI calls)
python main.py --no-openai

# Force fresh data extraction
python main.py --no-cache

# Limit campaigns for testing
python main.py --limit 50

# Custom batch size
python main.py --batch-size 5

# Custom output directory
python main.py --output-dir ./reports

# Clear cache
python main.py --clear-cache
```

### Advanced Usage Examples
```bash
# Fast testing with limited campaigns
python main.py --limit 10 --batch-size 2

# Full production run with custom output
python main.py --output-dir /path/to/reports --batch-size 20

# Debug mode with fresh data
python main.py --no-cache --limit 5 --no-openai
```

### Output

The script generates two Excel reports:
- **Main Report**: AI-generated sales descriptions with all campaign data
- **Summary Report**: Processing statistics and breakdowns by channel/vertical

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
- `python-dotenv`: Environment variable management

### Performance Considerations
- **Intelligent Caching**: Campaign IDs cached to avoid repeated API calls
- **Batch Processing**: AI descriptions generated in configurable batches
- **Rate Limiting**: OpenAI API calls properly rate-limited
- **Memory Optimization**: Efficient processing of large datasets
- **Error Recovery**: Graceful handling of API failures

## Migration from Legacy Script

The original monolithic script has been refactored into a modular structure:

- **Before**: 537 lines in a single file
- **After**: 7 focused modules with clear responsibilities
- **Benefits**: Better maintainability, testability, and extensibility

## Contributing

### Code Organization
1. **Salesforce changes**: Update `src/salesforce_client.py`
2. **AI improvements**: Modify `src/openai_client.py`
3. **Context enhancements**: Update `src/context_manager.py` and mapping files
4. **Report formatting**: Modify `src/excel_operations.py`

### Adding New Features
1. Create new modules in `src/` directory
2. Update `src/campaign_processor.py` for orchestration
3. Add command-line options to `main.py`
4. Update documentation in `docs/`

### Testing
- Each module can be tested independently
- Use `--no-openai` flag for testing without API calls
- Use `--limit` flag for testing with small datasets

## Troubleshooting

### Common Issues
1. **Missing environment variables**: Check `.env` file
2. **Salesforce connection**: Verify credentials and security token
3. **OpenAI API errors**: Check API key and rate limits
4. **No campaigns found**: Check date range and campaign member data

### Debug Mode
```bash
# Test without OpenAI calls
python main.py --no-openai --limit 5

# Check cache status
python main.py --clear-cache
```

## Testing the Program

The program queries **all campaigns with CampaignMembers created in the last 12 months**. For faster testing:

### **Recommended Testing Sequence**

1. **Quick Structure Test** (30 seconds, $0 cost):
   ```bash
   python main.py --no-openai --limit 5
   ```

2. **Small AI Test** (2-3 minutes, ~$0.05 cost):
   ```bash
   python main.py --limit 3 --batch-size 1
   ```

3. **Medium Test** (5-10 minutes, ~$0.20 cost):
   ```bash
   python main.py --limit 20 --batch-size 5
   ```

4. **Production Run** (hours, $10-30+ cost):
   ```bash
   python main.py --batch-size 20
   ```

### **Testing Performance**

| Test Type | Campaigns | Expected Time | OpenAI Cost |
|-----------|-----------|---------------|-------------|
| Preview Mode | 10 | 30 seconds | $0 |
| Small AI Test | 5 | 2-3 minutes | ~$0.05 |
| Medium Test | 20 | 5-10 minutes | ~$0.20 |
| Production | 1000+ | 1-3 hours | ~$10-30 |

Use `--limit` parameter to process only the first N campaigns for testing!

## License

Internal use only - Salesforce marketing automation tool

## Architecture Documentation

For detailed technical documentation, see:
- [`docs/project_structure.md`](docs/project_structure.md) - Complete architecture overview
- [`docs/project_breakdown.md`](docs/project_breakdown.md) - Detailed project breakdown
