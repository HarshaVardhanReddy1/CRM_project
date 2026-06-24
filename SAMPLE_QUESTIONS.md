# Sample Questions for CRM Query Testing

This file contains sample questions at different difficulty levels to test the query generation and database system.

---

## 🟡 Level 1: Medium Difficulty

These questions require basic SELECT statements with simple WHERE conditions and possibly one JOIN.

1. **List all active leads**
   - Expected: Simple SELECT with WHERE condition

2. **Show me all users in the system**
   - Expected: Basic SELECT from Users table

3. **What campaigns are currently running?**
   - Expected: SELECT with status filter

4. **Get all table names in the database**
   - Expected: Query information_schema

5. **Show me the top 10 recent leads**
   - Expected: SELECT with ORDER BY and LIMIT

6. **List all employees and their email addresses**
   - Expected: SELECT specific columns from Users

7. **How many leads do we have?**
   - Expected: SELECT COUNT(*)

8. **Show all chats from the system**
   - Expected: Basic SELECT from Chats table

9. **Get all holidays in the database**
   - Expected: SELECT from Holidays table

10. **List users who have a role assigned**
    - Expected: SELECT with WHERE and specific column

11. **Show me all notifications**
    - Expected: Simple SELECT from Notifications

12. **Get the list of all locations**
    - Expected: SELECT from locations table

---

## 🟠 Level 2: Hard Difficulty

These questions require multiple JOINs, aggregate functions, GROUP BY, or subqueries.

1. **Show me all leads with their detailed information**
   - Expected: JOIN Leads with LeadDetails, show all columns

2. **How many messages are in each chat?**
   - Expected: JOIN Chats with ChatMessages, use COUNT and GROUP BY

3. **Show employee names and their total salary from payslips**
   - Expected: JOIN Users with Payslips, use SUM aggregate

4. **List all leads that have documents attached**
   - Expected: JOIN Leads with LeadDocuments, use DISTINCT

5. **Get the attendance record for each user showing present and absent days**
   - Expected: JOIN Users with Attendances, use conditional COUNT

6. **Show leads with their stage transitions history**
   - Expected: JOIN Leads with LeadStageTransitions, ORDER BY date

7. **Which users have the most leave balance remaining?**
   - Expected: JOIN Users with LeaveBalances, ORDER BY balance DESC

8. **Get payroll information with employee names and payslip details**
   - Expected: Multiple JOINs (Users -> Payrolls -> Payslips)

9. **Show all lead co-applicants with their main lead information**
   - Expected: JOIN Leads with LeadCoApplicants

10. **List campaigns and count how many leads are associated with each**
    - Expected: JOIN Leads with Campaigns, use COUNT and GROUP BY

11. **Get users and their notification count**
    - Expected: LEFT JOIN Users with Notifications, use COUNT

12. **Show leads ordered by their latest stage transition date**
    - Expected: JOIN with subquery or complex ORDER BY

13. **Find users who haven't taken any leave**
    - Expected: LEFT JOIN with WHERE clause checking for NULLs

14. **Get payouts for each user with their payroll information**
    - Expected: Multiple JOINs with Users, Payouts, Payrolls

15. **Show all lead documents with the lead's current stage**
    - Expected: JOIN Leads, LeadDocuments, LeadStageTransitions

---

## 🔴 Level 3: Tricky Difficulty

These questions require complex logic, window functions, multiple nested JOINs, subqueries, or creative data manipulation.

1. **Show leads with all their related information (details, documents, stage, co-applicants) in a single result**
   - Expected: Complex multi-JOIN query with DISTINCT

2. **Find the lead with the longest time spent in each stage**
   - Expected: Window functions or subquery to find max duration per stage

3. **Get the average salary progression for employees based on payslip history**
   - Expected: Subquery or CTE to calculate salary changes over time

4. **Show users who have attendance above 90% in the current month**
   - Expected: Calculate attendance percentage, use HAVING clause

5. **Find leads that transitioned through all critical stages in order**
   - Expected: Complex WHERE with multiple conditions or window functions

6. **Get the top 5 most active users in chats (by message count) with their recent messages**
   - Expected: Multiple JOINs, subquery for top users, then fetch messages

7. **Show employees with performance metrics (attendance %, leave usage, payslip count)**
   - Expected: Multiple aggregates with CASE statements and GROUP BY

8. **Find leads with co-applicants that share the same location**
   - Expected: Complex JOIN with self-join or subquery on locations

9. **Calculate the cost of employees (payroll total) vs their attendance rate**
   - Expected: Multiple aggregates, division, complex JOIN

10. **Get the complete communication history for each lead (all chats and messages)**
    - Expected: Multi-table JOIN with lead information, chats, and messages

11. **Show users who have both approved leaves and active attendance records in a date range**
    - Expected: Complex date filtering with multiple table JOINs

12. **Find anomalies: users with payslips but no attendance records**
    - Expected: Subquery or NOT IN clause with multiple tables

13. **Get the timeline of lead progression (all stages with timestamps) grouped by campaign**
    - Expected: Multiple JOINs, ordering by date, GROUP BY campaign

14. **Calculate employee utilization: ratio of working days vs total payroll days**
    - Expected: Complex calculation with date functions and aggregates

15. **Show leads with their "lead score" (based on stage, documents, co-applicants, loan process status)**
    - Expected: Complex CASE statements calculating weighted score

16. **Get users who have document uploads but haven't had stage transitions recently**
    - Expected: LEFT JOIN with date filtering and subquery

17. **Find the most common transition path for leads (which stages follow each other)**
    - Expected: Window functions LAG/LEAD to find patterns in stage transitions

18. **Show the communication gap analysis: leads with no recent chat activity**
    - Expected: Complex LEFT JOIN with date comparisons and NULL checks

19. **Calculate team performance: average leads per user, conversion rate by stage**
    - Expected: Multiple aggregates, ratios, GROUP BY with multiple conditions

20. **Identify high-risk leads: those with co-applicants but incomplete loan process**
    - Expected: Multi-table JOIN with complex filtering logic
