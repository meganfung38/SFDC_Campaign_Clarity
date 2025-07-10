# SFDC Campaign Clarity - Project Structure

## Overview
This document describes the refactored project structure with modular components for better maintainability and organization.

## Directory Structure

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
├── generate_campaign_descriptions.py     # 📜 Legacy script (deprecated)
└── venv/                                 # 🐍 Virtual environment
```

## Architecture

### Modular Design

The system is built with a modular architecture where each component has a single responsibility:

1. **Salesforce Client** (`src/salesforce_client.py`)
   - Handles Salesforce authentication and data extraction
   - Manages SOQL queries and API rate limits
   - Extracts campaign members and campaign details

2. **OpenAI Client** (`src/openai_client.py`)
   - Manages OpenAI API interactions
   - Generates AI descriptions with proper prompting
   - Handles rate limiting and batch processing

3. **Context Manager** (`src/context_manager.py`)
   - Loads and manages field mappings
   - Enriches campaign data with business context
   - Transforms technical fields into sales intelligence

4. **Cache Manager** (`src/cache_manager.py`)
   - Optimizes performance with intelligent caching
   - Manages campaign ID cache with expiration
   - Provides cache utilities and information

5. **Excel Operations** (`src/excel_operations.py`)
   - Generates formatted Excel reports
   - Creates summary reports with statistics
   - Handles column ordering and styling

6. **Campaign Processor** (`src/campaign_processor.py`)
   - Main orchestration and workflow management
   - Coordinates all components
   - Handles error management and status reporting

7. **Main Entry Point** (`main.py`)
   - Command-line interface
   - Argument parsing and validation
   - Environment variable checking
   - Process execution and user feedback

## Benefits of Refactored Structure

### 1. **Separation of Concerns**
- Each module has a single, well-defined responsibility
- Easier to test individual components
- Reduced complexity in each file

### 2. **Maintainability**
- Changes to one system (e.g., Salesforce API) don't affect others
- Easier to add new features or modify existing ones
- Clear interfaces between components

### 3. **Testability**
- Each module can be unit tested independently
- Mock objects can be easily created for testing
- Better error isolation

### 4. **Scalability**
- Components can be optimized independently
- Easier to add new data sources or output formats
- Modular architecture supports future enhancements

### 5. **Reusability**
- Individual components can be reused in other projects
- Clear APIs for each module
- Reduced code duplication

## Migration from Legacy Script

The original `generate_campaign_descriptions.py` has been refactored into the modular structure:

| Legacy Component | New Module | Purpose |
|------------------|------------|---------|
| `CampaignDescriptionGenerator.__init__` | `campaign_processor.py` | Main orchestration |
| `_connect_salesforce` | `salesforce_client.py` | Salesforce operations |
| `_setup_openai` | `openai_client.py` | OpenAI operations |
| `_load_context_mappings` | `context_manager.py` | Context management |
| `_load_campaign_cache` | `cache_manager.py` | Cache operations |
| `create_final_report` | `excel_operations.py` | Excel generation |
| `enrich_campaign_context` | `context_manager.py` | Context enrichment |
| `generate_ai_description` | `openai_client.py` | AI description generation |
| Command-line interface | `main.py` | Entry point |

## Usage Examples

### Basic Usage
```bash
python main.py
```

### Advanced Usage
```bash
# Preview mode without OpenAI calls
python main.py --no-openai

# Process limited number of campaigns
python main.py --limit 50

# Force fresh data extraction
python main.py --no-cache

# Custom batch size and output directory
python main.py --batch-size 5 --output-dir ./reports
```

## Environment Setup

The refactored structure maintains the same environment requirements:

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

Required environment variables:
- `SF_USERNAME`: Salesforce username
- `SF_PASSWORD`: Salesforce password  
- `SF_SECURITY_TOKEN`: Salesforce security token
- `SF_DOMAIN`: Salesforce domain (login/test)
- `OPENAI_API_KEY`: OpenAI API key

## Component Interfaces

### SalesforceClient
```python
# Main methods
extract_campaign_members(months_back=12) -> (List[str], Dict[str, int])
extract_campaigns(campaign_ids) -> pd.DataFrame
```

### OpenAIClient
```python
# Main methods
generate_description(campaign, context) -> (str, str)
process_campaigns_batch(campaigns, context_manager, batch_size) -> pd.DataFrame
```

### ContextManager
```python
# Main methods
enrich_campaign_context(campaign) -> str
```

### CacheManager
```python
# Main methods
load_campaign_cache() -> Optional[Dict]
save_campaign_cache(campaign_ids, member_counts)
clear_cache()
get_cache_info() -> Optional[Dict]
```

### ExcelReportGenerator
```python
# Main methods
create_campaign_report(df, use_openai) -> str
create_summary_report(df, processing_stats) -> str
```

### CampaignProcessor
```python
# Main methods
extract_campaigns(use_cache) -> pd.DataFrame
process_campaigns(df, batch_size) -> pd.DataFrame
create_reports(df) -> (str, str)
run(use_cache, limit, batch_size) -> str
```

## Error Handling

Each module implements proper error handling:
- Specific exception types for different failure modes
- Detailed logging for debugging
- Graceful degradation when possible
- Clear error messages for users

## Performance Optimizations

- **Caching**: Campaign IDs cached to avoid repeated Salesforce queries
- **Batch Processing**: AI descriptions generated in configurable batches
- **Rate Limiting**: OpenAI API calls properly rate-limited
- **Memory Management**: Large datasets processed efficiently
- **Parallel Processing**: Components designed for future parallel execution

## Testing Strategy

Each module can be tested independently:
- Unit tests for individual methods
- Integration tests for component interactions
- Mock objects for external dependencies
- Test data fixtures for consistent testing

## Future Enhancements

The modular structure supports easy additions:
- New data sources (other CRMs, marketing platforms)
- Additional AI models (Claude, Gemini)
- New output formats (PowerBI, Tableau)
- Advanced analytics and reporting
- API endpoints for real-time processing 