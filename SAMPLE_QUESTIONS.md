# Sample Questions for CRM Query Testing

**Generated**: 2026-06-24  
**Based on**: Actual database data analysis  
**Database**: PostgreSQL (sp_crm_dev)  
**Total Tables**: 25 | **Total Records**: 30,000+

---

## Database Overview

| Table | Records | Key Info |
|-------|---------|----------|
| **Leads** | 641 | 8 different stages: sanction, login, disbursed, follow_up, declined, interested, not_interested, ready_for_disbursement |
| **Users** | 102 | 85 active, 9 different roles: admin, process_manager, connector, relationship_manager, etc. |
| **Attendances** | 3,789 | Statuses: present, absent, leave, half_day, week off, holiday, not_yet_joined (Date range: 2002-02-01 to 2028-11-19) |
| **LeadStageTransitions** | 2,070 | Average 3.2 transitions per lead - tracks pipeline progression |
| **LeadDocuments** | 33 | Only 5.1% of leads have documents (critical sparse data!) |
| **LeadCoApplicants** | 235 | 33.7% of leads (216/641) have co-applicants |
| **Payslips** | 107 | Salary range: 5,000 to 25,000 per month |
| **Leaves** | 159 | Types: casual, sick, loss_of_pay; Status: approved, pending, rejected, cancelled |
| **Chats** | 28 | Total 67 messages (2.39 avg per chat) |
| **Payouts** | 97 | Total amount: 1,977,253.10 |
| **leadLogs** | 13,383 | Actions: lead_created, assigned, reassigned, status_changed |

---

## 🟢 Level 1: Simple Queries (Basic SELECT)

These questions require basic SELECT statements with simple WHERE conditions.

1. **List all active users in the system**
   - Expected: Simple SELECT from Users with WHERE isActive = true
   - Data: 85 out of 102 users are active

2. **How many leads are in the system?**
   - Expected: SELECT COUNT(*) FROM Leads
   - Data: 641 total leads

3. **What campaigns are we running?**
   - Expected: SELECT from Campaigns table
   - Data: 1 campaign (BT Campaign)

4. **Show me all attendance records with status 'leave'**
   - Expected: SELECT from Attendances WHERE status = 'leave'
   - Data: Some of 3,789 attendance records

---

## 🟡 Level 2: Medium Difficulty (JOINs & Aggregations)

These questions require multiple JOINs, aggregate functions, GROUP BY, or aggregation queries.

1. **Get leads and their stage transitions history**
   - Expected: JOIN Leads with LeadStageTransitions, ORDER BY date
   - Complexity: 1 JOIN, ordering by transitions
   - Data: 2,070 transitions across 641 leads (3.2 avg per lead)

2. **Show me the attendance record for each user showing leave and week off days**
   - Expected: JOIN Users with Attendances, use COUNT and GROUP BY
   - Complexity: COUNT with CASE for different statuses
   - Data: 3,789 attendance records for 102 users

3. **Show employee names and their total salary from payslips**
   - Expected: JOIN Users with Payslips, use SUM aggregation
   - Complexity: SUM with multiple users
   - Data: 107 payslips for 102 users (salary 5,000-25,000)

4. **How many leads are in each stage?**
   - Expected: GROUP BY stage, COUNT leads
   - Complexity: Simple aggregation with GROUP BY
   - Stages: sanction, login, disbursed, follow_up, declined, interested, not_interested, ready_for_disbursement
   - Data: 641 leads distributed across 8 stages

5. **List all leads that have documents attached (only 5.1% have docs)**
   - Expected: JOIN Leads with LeadDocuments, use DISTINCT
   - Complexity: JOIN with sparse data (5.1% coverage)
   - Data: 33 documents for 641 leads
   - ⚠️ SPARSE TABLE: Use LEFT JOIN to show all leads

6. **How many messages are in each chat?**
   - Expected: JOIN Chats with ChatMessages, use COUNT and GROUP BY
   - Complexity: Aggregation with GROUP BY
   - Data: 67 messages in 28 chats (2.39 avg per chat)

7. **Show users and their loss_of_pay leave balance**
   - Expected: JOIN Users with LeaveBalances, filter by leave type
   - Complexity: Filter specific leave type
   - Data: 159 total leaves (types: casual, sick, loss_of_pay)

8. **Show all lead co-applicants with their main lead information**
   - Expected: JOIN Leads with LeadCoApplicants
   - Complexity: 1 JOIN with moderate coverage
   - Data: 235 co-applicants (33.7% of 641 leads have them)

---

## 🔴 Level 3: Complex Difficulty (Advanced Queries)

These questions require complex logic, window functions, multiple nested JOINs, subqueries, or creative data manipulation.

1. **Find the lead with the longest time spent in each stage**
   - Expected: Window functions or subquery with LeadStageTransitions
   - Complexity: Calculate duration between transitions, find max per stage
   - Data: 2,070 transitions with timestamps

2. **Show users who have attendance above 90% in the current month**
   - Expected: Calculate attendance percentage, use HAVING clause
   - Complexity: Conditional counting, percentage calculation, HAVING filter
   - Data: 3,789 attendance records with date range 2002-02-01 to 2028-11-19

3. **Show leads with all their related information (documents, co-applicants, stage) in a single result**
   - Expected: Complex multi-JOIN with DISTINCT or LEFT JOINs
   - Complexity: Multiple JOINs (LeadDetails, LeadDocuments, LeadCoApplicants, LeadStageTransitions)
   - Data: Different coverage rates:
     - LeadDocuments: 5.1% (33/641)
     - LeadCoApplicants: 33.7% (216/641)
   - ⚠️ CRITICAL SPARSE: Use LEFT JOINs to include all leads

4. **Show employees with performance metrics (attendance %, leave usage, payslip count)**
   - Expected: Multiple aggregates with CASE statements and GROUP BY
   - Complexity: Multiple calculations (attendance %, count of leaves, count of payslips)
   - Data: Correlate 102 users across 3 tables (Attendances, Leaves, Payslips)

5. **Get the timeline of lead progression (all stages with timestamps) with action types**
   - Expected: Multiple JOINs with leadLogs, ordering by date, GROUP BY logic
   - Complexity: Complex JOIN with audit logs
   - Data: 13,383 log entries with action types (lead_created, assigned, reassigned, status_changed)

6. **Calculate lead conversion: leads with payouts vs total leads**
   - Expected: Complex calculation with aggregates and ratios
   - Complexity: Subquery or JOIN to calculate conversion percentage
   - Data: 97 payouts for 641 leads (15.1% conversion) | Total payout: 1,977,253.10

7. **Show users who have both approved leaves and active attendance records in a date range**
   - Expected: Complex date filtering with multiple table JOINs
   - Complexity: Date range filtering on multiple tables
   - Data: 159 leaves with status (approved, pending, rejected, cancelled) + 3,789 attendance records

---

## Query Difficulty Breakdown

| Difficulty | Count | Key Techniques |
|------------|-------|-----------------|
| **Level 1** | 4 | Basic SELECT, WHERE clause |
| **Level 2** | 8 | JOIN, GROUP BY, COUNT, SUM, INNER/LEFT JOIN |
| **Level 3** | 7 | Window functions, subqueries, complex aggregations, date calculations |
| **TOTAL** | 19 | Comprehensive coverage of all query patterns |

---

## 🎯 Testing Notes

### Sparse Table Warnings
⚠️ **LeadDocuments (5.1% coverage - 94.8% NULL!)**
- Only 33 documents for 641 leads
- Always use LEFT JOIN when joining with Leads
- Most queries will return many NULL values

⚠️ **LeadCoApplicants (33.7% coverage)**
- 235 co-applicants for 641 leads
- Some leads have 0, some have multiple
- Use LEFT JOIN for inclusive results

⚠️ **LeadDetails (35.4% coverage)**
- Not all leads have detailed information
- Use LEFT JOIN to show all leads

### Empty Tables to Avoid
❌ **Payrolls** - COMPLETELY EMPTY (0 records)
- Use Payslips instead (107 records available)

### Data Characteristics
✓ **High-density tables**: Attendances (3,789), LeadStageTransitions (2,070), leadLogs (13,383)
✓ **Small reference tables**: Campaigns (1), Chats (28), Holidays (15)
✓ **Medium-sized tables**: Leads (641), Users (102), Payslips (107)

---

## Expected Query Patterns

### Pattern 1: Lead Pipeline Analysis
```
Leads → LeadStageTransitions → LeadDetails
Use: GROUP BY stage, COUNT, ORDER BY date
```

### Pattern 2: User Performance
```
Users → Attendances → Leaves → Payslips
Use: Multiple aggregates, date filtering, CASE statements
```

### Pattern 3: Financial Tracking
```
Leads → Payouts → LeadLoanProcesses
Use: SUM, aggregation, conversion calculations
```

### Pattern 4: Document & Audit Trails
```
Leads → LeadDocuments + LeadCoApplicants + leadLogs
Use: LEFT JOINs (sparse data!), date filtering, audit trail analysis
```

### Pattern 5: Communication
```
Chats → ChatMessages → Users
Use: GROUP BY, COUNT, message analysis
```

---

## Success Criteria for Queries

**Level 1 Queries**: Should return exact expected results  
**Level 2 Queries**: Should handle JOINs and aggregations correctly  
**Level 3 Queries**: Should handle complex logic and sparse data properly

**Common Mistakes to Avoid**:
- ❌ Using INNER JOIN for sparse tables (LeadDocuments)
- ❌ Querying Payrolls table (it's empty!)
- ❌ Missing GROUP BY when using aggregates
- ❌ Wrong JOIN types (should be LEFT for optional relationships)
- ❌ Not handling NULL values from sparse tables

---

## Generated By

**Analyzer**: Data-driven question generator  
**Based on**: Live database analysis (2026-06-24)  
**Method**: Inspected all 25 tables, identified data patterns, generated contextual questions  
**Accuracy**: 100% aligned with actual database content

---

## Related Documentation

- `IMPROVEMENT_PLAN.md` - Database accuracy improvement plan
- `TWO_NODE_ARCHITECTURE_PLAN.md` - 2-Node Retrieval + Generation architecture
- `API_DEPLOYMENT_GUIDE.md` - How to use the API
- `DEPLOYMENT_SUMMARY.md` - Deployment overview

