# CRM Query Generation Accuracy Improvement Plan

**Database Analysis Date**: 2026-06-24  
**Total Tables**: 25  
**Total Records**: ~30,000+ records across all tables

---

## 1. DATA DISTRIBUTION INSIGHTS

### High-Density Tables (Primary Focus for Accuracy)
| Table | Records | Primary Use | Complexity |
|-------|---------|------------|-----------|
| leadLogs | 13,383 | Audit trail for all lead activities | High |
| Attendances | 3,789 | Employee attendance tracking | High |
| LeadStageTransitions | 2,070 | Lead pipeline progression | High |
| Leads | 641 | Core CRM entity | High |
| LeadDetails | 227 | Lead extended info (1-1 with Leads) | Medium |
| LeadCoApplicants | 235 | Co-applicants per lead (Many-Many) | Medium |
| LeadLoanProcesses | 226 | Loan details (1-1 with Leads) | Medium |
| Leaves | 159 | Leave requests (1-Many with Users) | Medium |
| Payslips | 107 | Employee payroll data | Medium |
| Payouts | 97 | Lead-based payouts | Medium |

### Low-Density Tables (Edge Cases)
| Table | Records | Issue |
|-------|---------|-------|
| Payrolls | **0** | EMPTY - No records, but Payslips has 107 |
| Campaigns | **1** | Only 1 record - Hardcoded test data |
| locations | **4** | Minimal location data |
| LeadShareLinks | **15** | Rarely used |
| Holidays | **15** | Static reference data |

---

## 2. CRITICAL SCHEMA ISSUES TO ADDRESS

### A. Foreign Key Relationships Missing from Prompts
**Current Problem**: Prompt doesn't explicitly state which tables link to which

**Required Linkages**:
```
Leads (641) → has ONE LeadDetails (227)
         → has MANY LeadCoApplicants (235) [often 0-2 per lead]
         → has MANY LeadDocuments (33)
         → has ONE LeadLoanProcesses (226)
         → has MANY LeadStageTransitions (2,070)
         → has MANY in leadLogs (13,383)
         → has MANY Payouts (97)

Users (102) → has MANY Attendances (3,789) [37-40 per user avg]
         → has MANY Payslips (107) [~1 per user]
         → has MANY Leaves (159)
         → has ONE LeaveBalances (41)
         → has MANY Notifications (605) [~6 per user]
         → has MANY in Payouts (97)

Chats (28) → has MANY ChatMessages (67)
Users → participate in Chats (M:M relationship)
```

### B. Column Naming Inconsistencies
**Problem**: Some tables use non-obvious column names
```
Users table:
- Multiple date columns: joiningDate, dateOfJoining, lastSeen
- Payroll fields directly in Users table

Leads table:
- has BOTH "assignedTo" (userId) and "generatedById" (userId)
- has BOTH "branchId" and "leadGeneratorBranchId"

Attendances table:
- Status column but also fields: isLate, isHalfDay, isRegularized
- Has geographic coordinates (latitude/longitude for clock in/out)
```

### C. Type Mismatches
```
LeadStageTransitions.loanAmount - decimal but not formatted consistently
Payslips columns include both string and numeric versions
```

---

## 3. ACTUAL QUERY PATTERNS FROM DATA

### A. Top 10 Most Common Query Types (Based on Column Usage)

1. **Attendance-based**: Filter by date range, userId, status
   - 3,789 records → complex WHERE clauses needed
   - Multiple status values to handle

2. **Lead Pipeline**: GROUP BY stage, aggregate by LeadStageTransitions
   - 2,070 transitions across 641 leads = 3.2 avg transitions per lead
   - Need LEFT JOIN for leads without transitions

3. **Audit Logs**: JOIN leadLogs with Leads for tracking
   - 13,383 log entries can be huge result sets
   - Need LIMIT or date range filters

4. **Payroll/Attendance Correlation**: Users → Attendances + Payslips
   - Only 102 users, 107 payslips = incomplete payroll data
   - 3,789 attendance records for 102 users = high density

5. **Leave Management**: Users → Leaves + LeaveBalances
   - 159 leaves across unknown users = sparse data
   - Only 41 LeaveBalances = incomplete tracking

6. **Co-applicants Analysis**: Leads → LeadCoApplicants
   - 235 co-applicants for 641 leads = 0.37 ratio
   - Some leads have 0, some have multiple

7. **Document Tracking**: Leads → LeadDocuments
   - Only 33 documents for 641 leads = 5.1% coverage
   - Mostly NULL values expected

8. **Notifications**: Users → Notifications
   - 605 notifications for 102 users = 5.9 avg per user
   - Need GROUP BY with COUNT

9. **Chat Communications**: Chats → ChatMessages + Users
   - Only 67 messages in 28 chats = low usage
   - Good for testing but small result sets

10. **Financial**: Leads → LeadLoanProcesses → Payouts
    - 226 loan processes, 97 payouts = 43% payout conversion
    - Complex numeric aggregations needed

### B. Query Patterns That Will FAIL With Current Prompt
1. Leads without LeadDetails (414 out of 641 = 64.6%) → Needs LEFT JOIN
2. Leads without LeadCoApplicants → Need LEFT JOIN
3. Leads without documents (608 out of 641 = 94.8%) → Critical for LEFT JOIN
4. Users without Payslips → Need LEFT JOIN
5. Users without Leaves → Need LEFT JOIN

---

## 4. SPECIFIC IMPROVEMENTS NEEDED

### Phase 1: Prompt Enhancements
**Items**:
- [ ] Add explicit FK relationship diagram with record counts
- [ ] Document NULL prevalence rates for each relationship
- [ ] Add examples of LEFT JOIN queries (not just INNER JOIN)
- [ ] Clarify which tables are "sparse" vs "complete"
- [ ] Add example queries for each of the 10 common patterns above

### Phase 2: Column Name Clarification
**Items**:
- [ ] Document exact column name for each concept (e.g., clock_in vs clockIn)
- [ ] List all date column names and their purposes
- [ ] Create mapping table: "User ID" → userId/assignedTo/createdById/etc
- [ ] Document status/state column values for each table

### Phase 3: Test Coverage
**Items**:
- [ ] Test all Level 2 questions from SAMPLE_QUESTIONS.md (GROUP BY, JOINs)
- [ ] Test all Level 3 questions (window functions, subqueries, complex filters)
- [ ] Create test cases for edge cases:
  - Leads WITHOUT co-applicants
  - Leads WITHOUT documents
  - Leads WITHOUT loan processes
  - Users WITHOUT attendance
  - Users WITHOUT leaves

### Phase 4: LLM & Model Selection
**Items**:
- [ ] Use Claude 3.5 Sonnet for complex queries (Group By, Window Functions)
- [ ] Use Claude 3 Haiku for simple queries (single table, basic WHERE)
- [ ] Add query complexity detection before choosing model

### Phase 5: Validation Layer
**Items**:
- [ ] Check if query would return >10k rows → suggest LIMIT
- [ ] Validate all JOIN columns exist in FK relationships
- [ ] Verify GROUP BY columns are properly aggregated
- [ ] Check for missing DISTINCT in multi-JOIN scenarios

---

## 5. PRIORITY-RANKED IMPROVEMENTS

**🔴 CRITICAL (Implement First)**:
1. Add LEFT JOIN examples to prompt (64.6% of lead queries need this)
2. Document NULL prevalence in relationships
3. Add "sparse table" label to LeadDocuments (94.8% NULL)
4. Fix Payroll-related queries (empty Payrolls table issue)

**🟠 HIGH (Quick Wins)**:
5. Add GROUP BY + COUNT examples
6. Document all date column names and their purposes
7. Create exhaustive column name reference in prompt
8. Test against Level 2 SAMPLE_QUESTIONS.md

**🟡 MEDIUM (Should Do)**:
9. Add window function examples
10. Test against Level 3 SAMPLE_QUESTIONS.md
11. Create model selection logic (Sonnet vs Haiku)
12. Add query complexity detection

**🟢 LOW (Nice to Have)**:
13. Optimize for readability in complex queries
14. Add performance hints for large tables
15. Document aggregation best practices

---

## 6. QUICK REFERENCE: Table Summary

```
COMPLETE FK CHAINS (Tested & Working):
✓ Leads → LeadStageTransitions (2070 records, 3.2 avg per lead)
✓ Users → Attendances (3789 records, 37 avg per user)
✓ Chats → ChatMessages (67 records, 2.4 avg per chat)
✓ Users → Leaves (159 records, incomplete coverage)

PROBLEMATIC FK CHAINS (Sparse/NULL):
⚠ Leads → LeadDocuments (33/641 = 5.1%, needs LEFT JOIN)
⚠ Users → Payslips (107/102 = 105%, inconsistent)
⚠ Users → Payrolls (0/102 = EMPTY!)
⚠ Leads → LeadCoApplicants (235/641 = 36.7%, many with 0)

ONE-TO-ONE RELATIONSHIPS (Not 1:1):
⚠ Leads → LeadDetails (227/641 = 35.4% coverage)
⚠ Leads → LeadLoanProcesses (226/641 = 35.2% coverage)

TINY REFERENCE TABLES:
⚠ locations (4 rows)
⚠ Campaigns (1 row)
⚠ Holidays (15 rows)
```

---

## 7. METRICS TO TRACK IMPROVEMENT

**Before Implementing Plan**:
- Run all SAMPLE_QUESTIONS.md Level 2 & 3 queries
- Record: Success Rate, SQL Errors, Logic Errors

**After Each Phase**:
- Re-test same queries
- Track improvement % for each difficulty level
- Monitor average error rate per query pattern

**Success Criteria**:
- Level 2 queries: 95% accuracy
- Level 3 queries: 85% accuracy
- No runtime errors for valid questions
