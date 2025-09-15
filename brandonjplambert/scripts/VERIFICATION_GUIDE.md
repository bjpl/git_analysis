# Spanish Accounts Verification Guide

## 🚀 Quick Start

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Run Verification
```bash
python run_verification.py
```

The script will automatically:
- Load your YAML file from `_data/spanish_accounts.yml`
- Verify each URL (Instagram, YouTube, etc.)
- Generate comprehensive reports in `_data/verification_results/`

## 📊 Generated Reports

After running, you'll find these reports in the output directory:

1. **verified_accounts_[timestamp].json** - Complete JSON with all data
2. **spanish_accounts_analysis_[timestamp].xlsx** - Multi-sheet Excel workbook
3. **category_analysis_[timestamp].json** - Analysis by category
4. **quality_assessment_[timestamp].csv** - Quality scores for each account
5. **failed_verifications_[timestamp].csv** - List of URLs that couldn't be verified

## 🎯 What Gets Verified

For each URL, the system checks:

### Basic Verification
- ✅ Account exists and is accessible
- ✅ Account status (active, private, suspended, etc.)
- ✅ Platform-specific username extraction

### Data Enrichment
- 📊 Follower/subscriber counts
- 📝 Bio/description content
- 🌍 Location information
- 🏷️ Content categories
- 📧 Email discovery
- 🔗 Cross-platform links

### Spanish Language Analysis
- 🇪🇸 Language detection in bio/description
- 📍 Spanish location markers
- 🏴 Regional indicators (flags, city names)
- 💬 Spanish linguistic patterns

### Quality Scoring
Each account receives quality scores based on:
- **Completeness** (25%): How many fields are populated
- **Accuracy** (25%): Verification confidence
- **Freshness** (15%): How recent the data is
- **Consistency** (15%): Username/name alignment
- **Relevance** (20%): Spanish market alignment

## ⚙️ Advanced Usage

### Custom Batch Size
For better rate limit management:
```python
processor = YAMLAccountsProcessor(yaml_file, output_dir)
# Modify batch size before verification
processor.verifier.batch_size = 10  # Smaller batches for cautious processing
```

### Using YouTube API Key
For enhanced YouTube verification, add your API key:
```python
processor.verifier = DatasetVerifier(youtube_api_key="YOUR_API_KEY")
```

### Processing Subset of Categories
```python
# Filter accounts by category before processing
processor.accounts_data = [
    acc for acc in processor.accounts_data 
    if acc['category'] in ['Government', 'Media']
]
```

## 📈 Understanding Results

### Verification Statuses
- **active**: Account is live and accessible
- **private**: Account exists but is private
- **not_found**: URL returns 404
- **suspended**: Account has been suspended
- **rate_limited**: Hit API limits (retry later)
- **error**: Other verification errors

### Quality Score Interpretation
- **> 0.8**: Excellent quality, highly reliable data
- **0.6 - 0.8**: Good quality, usable for most purposes
- **0.4 - 0.6**: Average quality, may need manual review
- **< 0.4**: Low quality, significant data gaps

### Language Confidence
- **> 0.7**: Strongly indicates Spanish content
- **0.5 - 0.7**: Likely Spanish content
- **0.3 - 0.5**: Possibly Spanish, needs review
- **< 0.3**: Unlikely to be Spanish content

## 🔄 Re-verification Strategy

For maintaining data quality:

1. **High-value accounts**: Re-verify weekly
2. **Active accounts**: Re-verify monthly
3. **Failed verifications**: Retry after 24 hours
4. **Rate-limited**: Retry with smaller batch size

## ⚠️ Important Notes

1. **Rate Limits**: The system respects platform rate limits. Large datasets may take time.

2. **Anonymous Limits**: Without API keys, some platforms heavily restrict anonymous access:
   - Instagram: ~200 requests/hour
   - YouTube: Better with API key (10,000 units/day)

3. **Data Freshness**: Social media data changes rapidly. Regular re-verification recommended.

4. **Network Issues**: Use a stable connection. The system will retry failed requests automatically.

## 🐛 Troubleshooting

### "Rate limit reached"
- Reduce batch size in the processor
- Wait 1 hour before retrying
- Consider using API keys where available

### "Module not found" errors
```bash
pip install -r requirements.txt --upgrade
```

### Excel file won't open
- Ensure openpyxl is installed: `pip install openpyxl`
- Check disk space for large datasets

### Partial results
- Check `verification.log` for detailed errors
- Failed URLs are saved separately for retry

## 📊 Sample Statistics Output

```
=======================================================================
SPANISH ACCOUNTS VERIFICATION SUMMARY
=======================================================================

Source File: spanish_accounts.yml
Total Accounts: 245
Total URLs: 389
Verified URLs: 375

--- Categories ---
  Government: 45
  Media: 38
  Entertainment: 32
  Sports: 28
  ...

--- Verification Status ---
  active: 341 (90.9%)
  private: 12 (3.2%)
  not_found: 18 (4.8%)
  error: 4 (1.1%)

--- Quality Metrics ---
  Spanish Confirmed: 358
  High Quality (>70%): 312
  Verified Badges: 89
  Total Followers: 45,234,891
  Average Quality Score: 0.73
=======================================================================
```