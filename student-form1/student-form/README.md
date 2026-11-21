# Student Information Form (React + Node/Express + PostgreSQL)

```
student-form/
├── database/
│   ├── schema.sql     # tables, seed data, overview view
│   └── queries.sql    # inserts, reads, statistics
├── server/            # Express API (port 4000)
│   ├── .env.example
│   └── src/ index.js, db.js, routes/students.js
└── client/            # React + Vite (port 5173)
    └── src/ App.jsx, StudentForm.jsx, api.js, styles.css
```

## Setup
1. Create the database and tables
   createdb student_form
   psql -d student_form -f database/schema.sql
2. API
   cd server && cp .env.example .env   (edit DATABASE_URL and ADMIN_KEY)
   npm install && npm run dev
3. Client (new terminal)
   cd client && npm install && npm run dev
Open http://localhost:5173

## Endpoints
GET  /api/students/options   public
POST /api/students           public
GET  /api/students           header x-admin-key
GET  /api/students/stats     header x-admin-key
