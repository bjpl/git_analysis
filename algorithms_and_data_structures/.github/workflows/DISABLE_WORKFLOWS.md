# GitHub Actions Optimization Guide

## Current Issue
You're at 100% of your 3,000 included GitHub Actions minutes for the month.

## Immediate Actions Taken

### 1. Created Optimized Workflows
- `release-optimized.yml` - Reduced from ~45 min to ~5 min per run
- `ci-minimal.yml` - Quick CI that only runs essential tests

### 2. To Disable Expensive Workflows

**Option A: Rename workflow files (Recommended - Reversible)**
```bash
# Disable the expensive release workflow
mv .github/workflows/release.yml .github/workflows/release.yml.disabled

# To re-enable later:
mv .github/workflows/release.yml.disabled .github/workflows/release.yml
```

**Option B: Add workflow disable condition**
Add this to the top of any workflow:
```yaml
on:
  workflow_dispatch:  # Only manual trigger
  # Comment out other triggers
```

**Option C: Disable Actions for entire repository**
1. Go to Settings → Actions → General
2. Select "Disable Actions for this repository"
3. Can re-enable anytime

## Optimizations Made

### Old Workflow Issues:
- Matrix testing (5 Python versions × multiple OS = 15+ jobs)
- Full clone with history
- Installing dependencies multiple times
- Running all tests including slow integration tests
- No caching
- No timeouts
- No concurrency limits

### New Optimized Workflows:
- Single Python version
- Shallow clones (fetch-depth: 1)
- Dependency caching
- Only essential tests
- 5-10 minute timeouts
- Cancel previous runs
- Only run on explicit triggers

## Estimated Savings

| Workflow | Before | After | Savings |
|----------|--------|-------|---------|
| Release | ~45 min | ~5 min | 89% |
| CI | ~20 min | ~3 min | 85% |
| Per Push | ~65 min | ~8 min | 88% |

## Next Steps

1. **Immediate**: Disable or replace the expensive `release.yml`
2. **This Week**: Review all workflows in archived projects
3. **Long Term**: 
   - Use local testing before pushing
   - Use workflow_dispatch for manual control
   - Consider self-hosted runners for heavy workloads

## Monitoring Usage

Check your usage at: https://github.com/settings/billing

## Recovery Commands

```bash
# List all workflow files
find .. -path "*/.github/workflows/*.yml" -type f

# Disable all workflows in archived projects
for dir in ../archive/*/.github/workflows; do
  if [ -d "$dir" ]; then
    for file in "$dir"/*.yml; do
      mv "$file" "$file.disabled"
    done
  fi
done

# Check which workflows are active
find .. -path "*/.github/workflows/*.yml" ! -name "*.disabled" -type f
```

## Local Testing Alternative

Instead of using GitHub Actions for every test:

```bash
# Run tests locally before pushing
pytest tests/
black --check src/
flake8 src/

# Only push when tests pass locally
git push
```

Remember: Your included minutes reset in 19 days. These optimizations will help you stay within limits going forward.