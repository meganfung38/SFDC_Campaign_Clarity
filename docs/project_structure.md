# SFDC Campaign Clarity - Technical Architecture

## Overview
This document provides technical implementation details for the modular SFDC Campaign Clarity system. For user-facing documentation, see [README.md](../README.md).

## System Architecture

### Data Processing Pipeline
```
📊 Salesforce Query → 📈 Metrics Tracking → 🔄 Context Enrichment → 🤖 AI Processing → 📋 Excel Report
     ↓                     ↓                      ↓                     ↓                   ↓
CampaignMembers        Query Count         22 Field Mappings    8 Channel Prompts   Single Excel File
(configurable months)  Processing Time    BMID Translation     Critical Alerts     2 Focused Sheets
                                         Outreach Routing     max_tokens=100
                                                              temperature=0.3
```

### Directory Structure
```
SFDC_Campaign_Clarity/
├── campaign_report.py                    # Main batch processing script
├── single_campaign_report.py             # Individual campaign analysis
├── src/                                  # Core modules
│   ├── __init__.py                       # Package exports
│   ├── salesforce_client.py              # SF API with configurable time windows
│   ├── openai_client.py                  # AI generation with critical alerts & outreach routing
│   ├── context_manager.py                # 22-field context enrichment + BMID translation
│   ├── cache_manager.py                  # Exact time-window cache matching
│   ├── excel_operations.py               # RingCentral-branded reports
│   └── campaign_processor.py             # Main orchestration
├── data/                                 # Data files (see setup requirements)
│   ├── field_mappings.json              # Context transformation rules + BMID mappings (NOT IN REPO)
│   └── brian's_field_mappings.json      # Legacy field mappings
├── feedback_+_samples/                   # Campaign analysis samples with RC employee feedback
│   ├── samples/                          # Revised campaign descriptions (final versions)
│   │   ├── 701Hr000001L82yIAC_REVISED.txt      # Email campaign 
│   │   ├── 701Hr000001L8QHIA0_SAMPLE.txt       # Email campaign 
│   │   ├── 701Hr000001L9q4IAC_REVISED.txt      # SIA campaign
│   │   ├── 701TU00000ayWTJYA2_SAMPLE.txt       # Content Syndication 
│   │   └── 701TU00000ad4whYAA_SAMPLE.txt       # Additional Content 
│   └── feedback/                         # Original descriptions with RC employee feedback
│       ├── 7018000000194LtAAI_W_FEEDBACK.txt   # Feedback version
│       ├── 701Hr000001L82yIAC_W_FEEDBACK.txt   # Feedback version
│       ├── 701Hr000001L9q4IAC_W_FEEDBACK.txt   # Feedback version
│       ├── 701TU00000ad4whYAA_W_FEEDBACK.txt   # Feedback version
│       └── 701TU00000V75PKYAZ_W_FEEDBACK.txt   # Feedback version
├── cache/                                # Cache files with metadata
├── logs/                                 # Application logs
├── venv/                                 # Python virtual environment
├── requirements.txt                      # Python dependencies
├── .gitignore                           # Git ignore rules (includes sensitive docs)
└── docs/                                # Documentation
    ├── project_breakdown.md             # High-level project overview
    └── project_structure.md             # This technical architecture document
```

**⚠️ Field Mapping Files**: The file `data/field_mappings.json` contains sensitive RingCentral business information and is **not included in the public repository**. This file must be requested from [megan.fung@ringcentral.com](mailto:megan.fung@ringcentral.com) and placed in the `data/` directory before the system will function properly.

## Core Components

### 1. SalesforceClient (`src/salesforce_client.py`)

**Interface:**
```python
def extract_campaign_members(months_back: int = 12, member_limit: int = 1000) -> tuple[List[str], Dict[str, int], int]:
    """Extract campaign IDs with recent members
    
    Args:
        months_back: Lookback period for CampaignMember creation
        member_limit: Maximum members to query (0 = unlimited)
        
    Returns:
        (campaign_ids, member_counts, total_campaigns_queried)
    """

def extract_campaigns(campaign_ids: List[str]) -> pd.DataFrame:
    """Extract full campaign data for given IDs with all 21 fields"""
```

**Implementation Details:**
- Uses SOQL with dynamic date filtering: `CreatedDate >= {months_ago}`
- Conditional LIMIT clause based on member_limit parameter
- Tracks total campaigns queried vs. campaigns with sufficient members
- Batch processing within SOQL limits (2000 records)

### 2. OpenAIClient (`src/openai_client.py`)

**Current Settings:**
```python
# OpenAI API parameters (optimized for 255-character limit)
model="gpt-3.5-turbo"
max_tokens=100          # Reduced from 200 to control length
temperature=0.3         # Reduced from 0.7 for consistency
```

**Channel Mapping Logic:**
```python
def _get_prompt_type(campaign: pd.Series) -> str:
    """Map Channel__c values to prompt categories"""
    channel = campaign.get('Channel__c', '').lower()
    
    if channel == 'sales generated':
        return 'sales_generated'
    elif channel in ['var campaigns', 'var mdf', 'affiliates', 'isv', 'sia', 
                     'franchise & assoc.', 'service providers', 'amazon', 'referrals']:
        return 'partner_referral'
    elif channel == 'upsell':
        return 'existing_customer'
    # ... [continues with 8 total categories]
```

**Enhanced Features:**
- Base prompt with strict formatting rules
- Channel-specific questions in `• [Category]: Question?` format
- Critical alert detection: Automatic `• [⚠️ ALERT]` for campaigns with critical instructions
- Outreach sequence routing: Automatic `• [Outreach Sequence]` recommendations
- Explicit length controls: "under 80 characters per bullet, 255 total"
- Anti-repetition rules: "DO NOT repeat channel names in descriptions"

### 3. CacheManager (`src/cache_manager.py`)

**Exact Time-Window Matching:**
```python
def is_cache_compatible(requested_member_limit: int, requested_months_back: int = 12) -> bool:
    """Check cache compatibility with exact time-window matching
    
    Critical: Cache must have EXACT months_back match to ensure isolated datasets
    Example: 6-month request cannot use 18-month cache (different scope)
    """
    cached_months_back = cache_data.get('months_back', 12)
    
    # Must be exact match for time windows
    if cached_months_back != requested_months_back:
        return False
        
    # Member limit compatibility (cached >= requested OR both unlimited)
    return self._check_member_limit_compatibility(cached_member_limit, requested_member_limit)
```

**Cache Data Structure:**
```python
cache_data = {
    'campaign_ids': List[str],
    'member_counts': Dict[str, int],
    'total_campaigns_queried': int,
    'extraction_date': datetime,
    'member_limit': Optional[int],      # 0 = unlimited, None = legacy
    'months_back': int                  # Required for exact matching
}
```

### 4. ContextManager (`src/context_manager.py`)

**Field Processing:**
- Processes 22 Salesforce fields with intelligent mappings
- JSON-based field transformations with error-resistant parsing
- BMID enrichment for Email and Content Syndication campaigns
- Outreach sequence routing based on campaign attributes
- Handles null values and missing mappings gracefully

**Key Features:**
```python
# BMID Translation (Content Syndication uses campaign Name)
"DGSMBREXNRNFF" → "Demand Gen Small Business Email (EE Size: <= 99) RingEX Content Nurture Email Send Non Form Fills"
"MAJ_LGC_ABM_DataAxle_FY25" → "Segment - Majors, Channel - Lead Gen Content, List - ABM, Vendor - DataAxle, Fiscal Year - FY25"

# Field mappings
"Referrals" → "Customer or partner referral - high trust, warm introduction"
"Paid Search" → "Active search behavior - high buyer intent and urgency"
"Upsell" → "Existing customer exploring expansion - relationship established"
```

### 5. ExcelReportGenerator (`src/excel_operations.py`)

**Report Structure:**
```python
# Single Excel file with two sheets
Campaign_Data_Sheet = {
    'columns': [
        # Priority SF fields (frozen)
        'Name', 'Channel__c', 'Type', 'Status',
        # Additional SF fields  
        'TCP_Theme__c', 'Vendor__c', 'Territory__c',
        # AI content (highlighted)
        'AI_Prompt', 'AI_Description'
    ],
    'formatting': {
        'frozen_panes': (1, 3),          # First 3 columns + header
        'ai_columns_color': '#045A8D',    # Darker blue highlight
        'row_height': 15                  # Standard height
    }
}

Processing_Summary_Sheet = {
    'metrics': [
        'total_campaigns_queried', 'total_campaigns_processed',
        'processing_success_rate', 'average_description_length',
        'unique_channels', 'unique_verticals', 'processing_time_minutes'
        # ... 16 total metrics
    ]
}
```

### 6. CampaignProcessor (`src/campaign_processor.py`)

**Enhanced Interface:**
```python
def run(use_cache: bool = True, batch_size: int = 10, 
        member_limit: int = 1000, months_back: int = 12) -> Optional[str]:
    """Main processing workflow with configurable time windows"""
```

**Processing Flow:**
1. **Cache Check**: Exact time-window and member-limit compatibility
2. **Data Extraction**: Configurable months_back parameter
3. **Context Enrichment**: 21-field processing with mappings
4. **AI Processing**: Channel-specific prompts with optimized parameters
5. **Report Generation**: Single Excel file with metrics

## Component Interfaces

### SalesforceClient
```python
# Core extraction methods
extract_campaign_members(months_back=12, member_limit=1000) -> tuple[List[str], Dict[str, int], int]
extract_campaigns(campaign_ids: List[str]) -> pd.DataFrame

# Query building
_build_member_query(months_back: int, member_limit: int) -> str
_build_campaign_query(campaign_ids: List[str]) -> str
```

### OpenAIClient
```python
# AI generation
generate_description(campaign: pd.Series, context: str) -> tuple[str, str]
process_campaigns_batch(campaigns: pd.DataFrame, context_manager, batch_size: int) -> pd.DataFrame

# Prompt management
_get_prompt_type(campaign: pd.Series) -> str
_get_tailored_prompt(prompt_type: str, context: str) -> str
```

### CacheManager
```python
# Cache operations
load_campaign_cache() -> Optional[Dict]
save_campaign_cache(campaign_ids, member_counts, total_queried, member_limit, months_back)
is_cache_compatible(member_limit: int, months_back: int) -> bool
clear_cache() -> None

# Metadata
get_cache_info() -> Optional[Dict]
```

## Performance Optimizations

### Intelligent Caching
- **Exact Time-Window Matching**: Prevents data scope pollution
- **Member Limit Compatibility**: Cached unlimited data works for limited requests
- **Metadata Tracking**: Stores extraction parameters for validation
- **Smart Expiration**: Configurable cache lifecycle

### API Rate Limiting
```python
# OpenAI throttling
time.sleep(0.5)  # Between API calls

# Salesforce batch optimization
SOQL_LIMIT = 2000  # Maximum records per query
batch_size = min(len(campaigns), 10)  # Configurable processing batches
```

### Memory Management
- Streaming SOQL queries for large datasets
- Batch processing with configurable sizes
- Efficient pandas operations with chunking
- Garbage collection after large operations

## Error Handling

### Comprehensive Error Tracking
```python
# Processing statistics
processing_stats = {
    'campaigns_with_errors': 0,
    'error_details': [],
    'processing_success_rate': float,
    'average_description_length': float
}

# Error recovery
try:
    description = openai_client.generate_description(campaign, context)
except Exception as e:
    description = f"Error: {str(e)[:100]}..."
    processing_stats['campaigns_with_errors'] += 1
    continue  # Process remaining campaigns
```

### API Failure Handling
- Salesforce connection retry logic
- OpenAI rate limit detection and backoff
- Graceful degradation for individual campaign failures
- Comprehensive logging with structured error details

## Testing Strategies

### Development Testing
```bash
# Unit testing approach
pytest src/test_salesforce_client.py    # SF API integration
pytest src/test_cache_manager.py        # Cache compatibility logic
pytest src/test_openai_client.py        # Prompt generation and formatting

# Integration testing
python campaign_report.py --no-openai --member-limit 10    # Data flow
python campaign_report.py --member-limit 50 --months-back 1  # Minimal AI test
```

### Cache Testing
```bash
# Test exact time-window matching
python campaign_report.py --months-back 6 --member-limit 100   # Create 6mo cache
python campaign_report.py --months-back 12 --member-limit 100  # Should extract fresh
python campaign_report.py --months-back 6 --member-limit 50    # Should use cache
```

### Performance Testing
```bash
# Scalability testing
python campaign_report.py --member-limit 0 --batch-size 1     # Stress test
python campaign_report.py --member-limit 5000 --batch-size 20 # Production simulation
```

## AI Parameter Optimization

### Token Management
```python
# Current optimized settings
max_tokens=100      # Targets ~300 characters (75% of 255 limit)
temperature=0.3     # Balanced consistency vs. creativity

# Length estimation
estimated_tokens = len(prompt) // 4
if estimated_tokens > 3500:
    logging.warning("Prompt may exceed token limits")
```

### Prompt Engineering
- Explicit formatting instructions with examples
- Anti-repetition rules to prevent channel name echoing
- Length constraints: "under 80 characters per bullet"
- Category label enforcement: "use ONLY the exact label shown"

## Configuration Management

### Required Setup Files

**1. Environment Variables (.env)**
```bash
# Required Salesforce credentials
SF_USERNAME=user@company.com
SF_PASSWORD=password
SF_SECURITY_TOKEN=token
SF_DOMAIN=login  # or 'test'

# Required OpenAI credential
OPENAI_API_KEY=sk-...

# Optional performance settings
DEFAULT_BATCH_SIZE=10
DEFAULT_MEMBER_LIMIT=1000
DEFAULT_MONTHS_BACK=12
```

**2. Field Mapping Files (NOT IN PUBLIC REPO)**
- `data/field_mappings.json` - Main context transformation rules

These files contain sensitive RingCentral business information and must be requested from [megan.fung@ringcentral.com](mailto:megan.fung@ringcentral.com). The system will not function without these files.

**3. Sample Campaign Outputs**

**Final Campaign Descriptions (samples/):**
- [`feedback_+_samples/samples/701Hr000001L82yIAC_REVISED.txt`](../feedback_+_samples/samples/701Hr000001L82yIAC_REVISED.txt) - Email campaign with BMID enrichment and outreach sequence
- [`feedback_+_samples/samples/701Hr000001L8QHIA0_SAMPLE.txt`](../feedback_+_samples/samples/701Hr000001L8QHIA0_SAMPLE.txt) - Email campaign sample with outreach routing
- [`feedback_+_samples/samples/701Hr000001L9q4IAC_REVISED.txt`](../feedback_+_samples/samples/701Hr000001L9q4IAC_REVISED.txt) - Additional email campaign example
- [`feedback_+_samples/samples/701TU00000ayWTJYA2_SAMPLE.txt`](../feedback_+_samples/samples/701TU00000ayWTJYA2_SAMPLE.txt) - Content Syndication campaign with vendor detection
- [`feedback_+_samples/samples/701TU00000ad4whYAA_SAMPLE.txt`](../feedback_+_samples/samples/701TU00000ad4whYAA_SAMPLE.txt) - Additional Content Syndication example

**Original Descriptions with RC Feedback (feedback/):**
- [`feedback_+_samples/feedback/701Hr000001L82yIAC_W_FEEDBACK.txt`](../feedback_+_samples/feedback/701Hr000001L82yIAC_W_FEEDBACK.txt) - Email campaign feedback
- [`feedback_+_samples/feedback/701TU00000ad4whYAA_W_FEEDBACK.txt`](../feedback_+_samples/feedback/701TU00000ad4whYAA_W_FEEDBACK.txt) - Content Syndication feedback

### Command Line Interface
```python
# Core parameters with validation
parser.add_argument('--months-back', type=int, default=12, 
                   help='Number of months to look back for campaign members')
parser.add_argument('--member-limit', type=int, default=1000,
                   help='Maximum CampaignMembers to query (0 for unlimited)')
parser.add_argument('--batch-size', type=int, default=10,
                   help='Number of campaigns to process per batch')
```

## Future Enhancement Opportunities

### Technical Improvements
- **Parallel Processing**: Multi-threaded campaign processing
- **Database Integration**: Persistent storage for historical analytics
- **Real-time APIs**: RESTful endpoints for live campaign analysis
- **Advanced Caching**: Redis-based distributed cache

### AI Enhancements
- **Dynamic Prompts**: Context-aware prompt generation
- **Quality Scoring**: Automated description quality assessment
- **A/B Testing**: Prompt variant performance comparison
- **Custom Models**: Fine-tuned models for sales terminology

### Integration Opportunities
- **Salesforce App**: Native SF Lightning component
- **CRM Integration**: HubSpot, Pipedrive compatibility
- **Analytics Platforms**: Tableau, PowerBI connectors
- **Workflow Automation**: Zapier, Microsoft Power Automate

## Migration Notes

### Recent Technical Changes
- **BMID Enhancement**: Added intelligent translation for Email and Content Syndication campaigns
- **Critical Alert System**: Automatic detection and flagging of campaigns requiring special handling
- **Outreach Sequence Routing**: Smart sequence recommendations based on campaign attributes and EE size
- **Content Syndication Parsing**: Uses campaign Name with underscore separation for better accuracy
- **Exact Cache Matching**: Changed from `>=` to `==` for months_back compatibility
- **OpenAI Parameters**: Reduced max_tokens (200→100) and temperature (0.7→0.3)

### Breaking Changes
- Cache files from before months_back implementation may be incompatible
- OpenAI responses will be shorter due to reduced max_tokens
- Time-window requests require exact cache matches (may trigger more fresh extractions)

### Migration Commands
```bash
# Clear legacy cache
python campaign_report.py --clear-cache

# Test updated parameters
python campaign_report.py --no-openai --member-limit 10 --months-back 12
``` 