# Database Schema Documentation

## Overview
This CRM system uses PostgreSQL to manage customer relationships, leads, communications, and employee management. The database `sp_crm_dev` contains 25 tables organized into logical modules.

## Database Tables

### Core CRM Tables

#### **Leads**
- **Purpose**: Central table for managing potential customers
- **Key Fields**: Lead ID, status, source, stage
- **Related Tables**: LeadDetails, LeadCoApplicants, LeadDocuments, LeadStageTransitions, LeadLoanProcesses, LeadShareLinks, leadLogs, lead_otps

#### **LeadDetails**
- **Purpose**: Extended information about leads
- **Key Fields**: Lead ID (FK), contact details, additional metadata
- **Relationship**: One-to-One with Leads

#### **LeadCoApplicants**
- **Purpose**: Track co-applicants or associated persons for a lead
- **Key Fields**: Lead ID (FK), co-applicant information
- **Relationship**: One-to-Many with Leads

#### **LeadDocuments**
- **Purpose**: Store document references and metadata for leads
- **Key Fields**: Lead ID (FK), document type, file path
- **Relationship**: One-to-Many with Leads

#### **LeadStageTransitions**
- **Purpose**: Track the progression of leads through sales pipeline stages
- **Key Fields**: Lead ID (FK), stage, timestamp
- **Relationship**: One-to-Many with Leads

#### **LeadLoanProcesses**
- **Purpose**: Manage loan-related information for leads
- **Key Fields**: Lead ID (FK), loan details, status
- **Relationship**: One-to-Many with Leads

#### **LeadShareLinks**
- **Purpose**: Generate and track shared lead information links
- **Key Fields**: Lead ID (FK), share link, expiration date
- **Relationship**: One-to-Many with Leads

#### **leadLogs** (lowercase)
- **Purpose**: Audit trail for lead activities and changes
- **Key Fields**: Lead ID (FK), action, timestamp
- **Relationship**: One-to-Many with Leads

#### **lead_otps** (lowercase)
- **Purpose**: One-time passwords for lead verification
- **Key Fields**: Lead ID (FK), OTP, validity
- **Relationship**: One-to-Many with Leads

### Communication Tables

#### **Chats**
- **Purpose**: Manage chat/messaging conversations
- **Key Fields**: Chat ID, user ID (FK), metadata
- **Related Tables**: ChatMessages

#### **ChatMessages**
- **Purpose**: Individual messages within chats
- **Key Fields**: Chat ID (FK), user ID (FK), message content, timestamp
- **Relationship**: One-to-Many with Chats

### Campaign & Marketing Tables

#### **Campaigns**
- **Purpose**: Track marketing campaigns and their performance
- **Key Fields**: Campaign ID, name, status, dates
- **Related Tables**: Leads (through campaign source)

### User Management Tables

#### **Users**
- **Purpose**: Central user/employee table
- **Key Fields**: User ID, name, email, role, status
- **Related Tables**: Payrolls, Payslips, Attendances, LeaveBalances, Leaves, UserSettings, Notifications, Chats

#### **UserSettings**
- **Purpose**: Store user-specific preferences and configurations
- **Key Fields**: User ID (FK), setting key, setting value
- **Relationship**: One-to-Many with Users

### HR & Payroll Tables

#### **Payrolls**
- **Purpose**: Monthly/periodic payroll records
- **Key Fields**: User ID (FK), payroll period, total amount
- **Related Tables**: Payslips

#### **Payslips**
- **Purpose**: Individual payslip details
- **Key Fields**: User ID (FK), payroll ID (FK), gross salary, deductions, net amount
- **Relationship**: One-to-Many with Payrolls and Users

#### **Attendances**
- **Purpose**: Track employee attendance
- **Key Fields**: User ID (FK), date, status (present/absent/leave)
- **Relationship**: One-to-Many with Users

#### **Leaves**
- **Purpose**: Track leave requests and approvals
- **Key Fields**: User ID (FK), leave type, start date, end date, status
- **Relationship**: One-to-Many with Users

#### **LeaveBalances**
- **Purpose**: Maintain employee leave balance information
- **Key Fields**: User ID (FK), leave type, total, used, remaining
- **Relationship**: One-to-Many with Users

### Settings & Configuration Tables

#### **Holidays**
- **Purpose**: Store public holidays and company-specific holidays
- **Key Fields**: Date, holiday name, type (national/company)

#### **Payouts**
- **Purpose**: Track payment disbursements
- **Key Fields**: User ID (FK), amount, date, status
- **Relationship**: One-to-Many with Users

#### **Notifications**
- **Purpose**: Manage system notifications for users
- **Key Fields**: User ID (FK), message, type, read status
- **Relationship**: One-to-Many with Users

### Location Data

#### **locations** (lowercase)
- **Purpose**: Store location/geography data
- **Key Fields**: Location ID, name, coordinates, region
- **Related Tables**: Users (optional location assignment)

---

## Key Relationships Summary

### Lead-Centric Relationships
```
Leads (1) ──────── (Many) LeadDetails
     ├──────────── (Many) LeadCoApplicants
     ├──────────── (Many) LeadDocuments
     ├──────────── (Many) LeadStageTransitions
     ├──────────── (Many) LeadLoanProcesses
     ├──────────── (Many) LeadShareLinks
     ├──────────── (Many) leadLogs
     └──────────── (Many) lead_otps
```

### User-Centric Relationships
```
Users (1) ─────────── (Many) Payrolls
    ├──────────────── (Many) Attendances
    ├──────────────── (Many) Leaves
    ├──────────────── (Many) LeaveBalances
    ├──────────────── (Many) UserSettings
    ├──────────────── (Many) Notifications
    ├──────────────── (Many) Chats
    ├──────────────── (Many) Payouts
    └──────────────── (1) Payslips
```

### Communication Relationships
```
Chats (1) ─────────── (Many) ChatMessages
    └──────────────── (Many) Users
```

---

## Common Query Patterns

### Get Lead Information with Details
```sql
SELECT l."id", l."status", ld."contact_name", ld."phone", ld."email"
FROM "Leads" l
LEFT JOIN "LeadDetails" ld ON l."id" = ld."lead_id"
WHERE l."status" = 'active'
LIMIT 100;
```

### Get User Payroll Information
```sql
SELECT u."name", p."period", ps."gross_salary", ps."net_amount"
FROM "Users" u
JOIN "Payrolls" p ON u."id" = p."user_id"
JOIN "Payslips" ps ON p."id" = ps."payroll_id"
ORDER BY p."period" DESC
LIMIT 100;
```

### Get Lead Pipeline Status
```sql
SELECT l."id", lst."stage", COUNT(*) as "stage_count"
FROM "Leads" l
JOIN "LeadStageTransitions" lst ON l."id" = lst."lead_id"
GROUP BY l."id", lst."stage"
LIMIT 100;
```

### Get User Attendance Summary
```sql
SELECT u."name", COUNT(*) as "total_days", 
  SUM(CASE WHEN a."status" = 'present' THEN 1 ELSE 0 END) as "present"
FROM "Users" u
LEFT JOIN "Attendances" a ON u."id" = a."user_id"
GROUP BY u."id", u."name"
LIMIT 100;
```

---

## Naming Conventions

- **Table Names**: PascalCase for most tables (e.g., `Leads`, `Users`, `Payrolls`)
- **Exceptions**: `leadLogs` and `lead_otps` use camelCase and snake_case
- **Lowercase**: `locations` table uses lowercase
- **Identifiers**: Use double quotes around table and column names in queries
- **Strings**: Use single quotes for string values

---

## Database Access

- **Host**: Check `DB_HOST` in environment variables
- **Port**: Check `DB_PORT` in environment variables
- **Database**: `sp_crm_dev`
- **User**: Check `DB_USER` in environment variables
- **Connection**: PostgreSQL with psycopg2 driver

---

## Notes for Development

1. All lead-related queries should typically start with the `Leads` table
2. User information is centralized in the `Users` table
3. Time-series data (attendance, payroll) can be queried by date ranges
4. Use aliases for better readability in complex joins
5. Always include LIMIT clauses to prevent performance issues
6. Foreign key relationships are enforced at the database level
