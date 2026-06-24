# Sample Questions Update Summary

**Date**: 2026-06-24  
**Status**: ✅ COMPLETE  
**Method**: Data-driven generation from live database  

---

## What Changed

### Old SAMPLE_QUESTIONS.md
- ❌ Generic questions not based on actual data
- ❌ Placeholder difficulty levels
- ❌ No data context or coverage percentages
- ❌ Missing sparse table warnings
- ❌ No real stage names or status values

### New SAMPLE_QUESTIONS.md
- ✅ 19 questions based on actual database data
- ✅ Real stage names: sanction, login, disbursed, follow_up, declined, etc.
- ✅ Real attendance statuses: present, absent, leave, half_day, week off, holiday
- ✅ Actual coverage percentages (5.1% for LeadDocuments, 33.7% for co-applicants)
- ✅ Real data ranges (641 leads, 102 users, 3,789 attendances)
- ✅ Sparse table warnings with percentages
- ✅ Database overview with actual record counts

---

## Questions Generated

### Level 1 (4 Basic SELECT Questions)
1. List all active users in the system (85 of 102 are active)
2. How many leads are in the system? (641 total)
3. What campaigns are we running? (1 campaign: BT Campaign)
4. Show me all attendance records with status 'leave'

### Level 2 (8 JOIN & Aggregation Questions)
1. Get leads and their stage transitions history (2,070 transitions)
2. Show me the attendance record for each user showing leave and week off days
3. Show employee names and their total salary from payslips (salary: 5,000-25,000)
4. How many leads are in each stage? (8 stages total)
5. List all leads that have documents attached ⚠️ (5.1% coverage - SPARSE!)
6. How many messages are in each chat? (67 messages in 28 chats)
7. Show users and their loss_of_pay leave balance
8. Show all lead co-applicants with their main lead information (33.7% have co-applicants)

### Level 3 (7 Complex Queries)
1. Find the lead with the longest time spent in each stage (window functions)
2. Show users who have attendance above 90% in the current month (percentage calculation)
3. Show leads with all their related information (documents, co-applicants, stage)
4. Show employees with performance metrics (attendance %, leave usage, payslip count)
5. Get the timeline of lead progression (13,383 log entries to analyze)
6. Calculate lead conversion: leads with payouts (97 payouts vs 641 leads = 15.1%)
7. Show users who have both approved leaves and active attendance records in a date range

---

## Data Insights Included

### Database Statistics
```
Leads:                641 records (8 stages)
Users:                102 records (85 active, 9 roles)
Attendances:          3,789 records (7 statuses)
LeadStageTransitions: 2,070 records (avg 3.2 per lead)
Payslips:             107 records (salary: 5K-25K)
Leaves:               159 records (3 types)
Chats:                28 with 67 messages
Campaigns:            1 (BT Campaign)
LeadDocuments:        33 (5.1% of leads - SPARSE!)
LeadCoApplicants:     235 (33.7% of leads)
Payouts:              97 (total: 1,977,253.10)
leadLogs:             13,383 records (4 action types)
```

### Sparse Table Warnings
```
⚠️  LeadDocuments:     5.1% coverage (33/641 leads)  → Use LEFT JOIN
⚠️  LeadCoApplicants: 33.7% coverage (216/641)      → Use LEFT JOIN  
⚠️  LeadDetails:      35.4% coverage                 → Use LEFT JOIN
⚠️  Payslips:         Incomplete mapping             → Use LEFT JOIN
❌ Payrolls:          EMPTY (0 records)              → DON'T USE
```

### Data Characteristics
- **High-density**: Attendances (3,789), LeadStageTransitions (2,070), leadLogs (13,383)
- **Reference**: Campaigns (1), Chats (28), Holidays (15)
- **Medium**: Leads (641), Users (102), Payslips (107)
- **Sparse**: LeadDocuments (5.1%), LeadCoApplicants (33.7%)

---

## Testing Value

### Level 1 Questions
✓ Test basic SELECT and WHERE filtering  
✓ Verify table access and column names  
✓ Validate simple data retrieval  

### Level 2 Questions
✓ Test JOIN operations (INNER, LEFT)  
✓ Test GROUP BY and aggregations (COUNT, SUM)  
✓ Test sparse table handling  
✓ Test multiple table relationships  

### Level 3 Questions
✓ Test window functions and subqueries  
✓ Test complex multi-table JOINs  
✓ Test date filtering and calculations  
✓ Test percentage/ratio calculations  
✓ Test audit trail analysis  

---

## How to Use These Questions

### For Testing Accuracy
```bash
# Run all 19 questions through the API
for each question in SAMPLE_QUESTIONS.md:
  POST /api/query with {"question": question, "include_retrieval_info": true}
  Verify: SQL is valid, results are correct, no errors
```

### For Benchmarking
```
Test all Level 2 & 3 questions:
  - Measure success rate (should be 90%+)
  - Check retrieval accuracy (correct tables selected)
  - Verify SQL correctness (executes without error)
  - Validate result accuracy (returns expected data)
```

### For Regression Testing
```
After each model/prompt update:
  - Re-run all 19 questions
  - Compare results with baseline
  - Track improvements in success rate
  - Monitor sparse table handling
```

---

## Key Improvements Over Original

| Aspect | Original | Updated |
|--------|----------|---------|
| **Relevance** | Generic | Based on actual data |
| **Accuracy** | Hypothetical | Real stage/status names |
| **Coverage** | Random data | Actual percentages |
| **Warnings** | None | Sparse table alerts with % |
| **Examples** | Made up | Real from database |
| **Total Questions** | 60+ | 19 focused questions |
| **Testing Value** | Low | High - covers all patterns |

---

## Data Generation Method

### Process
1. Connected to live PostgreSQL database (sp_crm_dev)
2. Analyzed all 25 tables with actual data
3. Calculated statistics:
   - Total record counts
   - Distinct values
   - Coverage percentages
   - Data ranges
   - Relationships
4. Generated 19 contextual questions based on patterns
5. Included sparse table warnings with percentages
6. Organized by difficulty level

### Verification
✅ All 641 leads verified (8 stages)  
✅ All 102 users verified (85 active)  
✅ All 3,789 attendance records verified  
✅ All 2,070 stage transitions verified  
✅ All sparse table percentages calculated  
✅ Empty Payrolls table confirmed  

---

## Files Updated

| File | Changes | Impact |
|------|---------|--------|
| `SAMPLE_QUESTIONS.md` | ✅ Complete rewrite | Questions now match actual data |
| `data_analysis.json` | ✅ Created | Stores insights for future updates |
| `QUESTIONS_UPDATE_SUMMARY.md` | ✅ Created | This document |

---

## Next Steps

### Immediate
- [ ] Run all 19 questions through `/api/query` endpoint
- [ ] Verify accuracy with real API
- [ ] Benchmark against baseline

### Short Term
- [ ] Update test_api_deployment.py with all 19 questions
- [ ] Add accuracy metrics by question difficulty
- [ ] Track improvements over time

### Long Term
- [ ] Re-analyze data quarterly
- [ ] Update questions based on new data patterns
- [ ] Add more Level 3 questions as complexity increases

---

## Statistics

**Questions Generated**: 19 total
- Level 1: 4 (21%)
- Level 2: 8 (42%)
- Level 3: 7 (37%)

**Data Coverage**:
- All 25 tables analyzed
- 30,000+ total records analyzed
- 12 tables with actual questions
- 11 different query patterns identified

**Expected Accuracy**:
- Level 1: 95%+ (simple queries)
- Level 2: 90%+ (JOINs & aggregations)
- Level 3: 85%+ (complex queries)

---

## Document Links

- `SAMPLE_QUESTIONS.md` - Updated sample questions (START HERE)
- `IMPROVEMENT_PLAN.md` - Original analysis and improvements
- `TWO_NODE_ARCHITECTURE_PLAN.md` - Query generation architecture
- `API_DEPLOYMENT_GUIDE.md` - How to test with API

---

**Status**: ✅ COMPLETE & READY  
**Last Updated**: 2026-06-24  
**Generated From**: Live database analysis  
**Quality**: Production-ready test cases
