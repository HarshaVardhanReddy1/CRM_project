# Analytics Query Chat Frontend

A clean, minimal React frontend for the NL-to-SQL analytics agent.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will open at http://localhost:3000

## Features

- **Chat Interface**: Send natural language questions about your data
- **Live Results**: Displays query results as clean tables inline in the chat
- **SQL Visibility**: Collapsible "View SQL" blocks to inspect generated SQL
- **Clear History**: Button to reset conversation and clear backend history
- **Responsive Design**: Works on desktop and tablet

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000`:

- **POST /query**: Send a natural language question
- **DELETE /history**: Clear conversation history

Both operations are fully integrated into the chat UI.

## Build

To build for production:
```bash
npm run build
```

Output files will be in the `dist/` directory.
