CROP YIELD DSS - FRONTEND SETUP INSTRUCTIONS
=============================================

The folder structure has been created with placeholder files.

NEXT STEPS:
-----------

1. Copy content from the artifacts into each file:
   
   ✓ package.json
   ✓ public/index.html
   ✓ src/index.js
   ✓ src/index.css
   ✓ src/App.jsx
   ✓ src/App.css
   ✓ src/services/api.js
   ✓ src/components/Header.jsx
   ✓ src/components/Navigation.jsx
   ✓ src/components/Dashboard.jsx
   ✓ src/components/YieldChart.jsx
   ✓ src/components/FieldMap.jsx
   ✓ src/components/PredictionPanel.jsx
   ✓ src/components/DataUpload.jsx
   ✓ src/components/RasterAssets.jsx

2. Install dependencies:
   cd frontend
   npm install

3. Start the development server:
   npm start

4. OR use Docker:
   docker-compose up --build

FOLDER STRUCTURE:
-----------------
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx
│   │   ├── DataUpload.jsx
│   │   ├── FieldMap.jsx
│   │   ├── Header.jsx
│   │   ├── Navigation.jsx
│   │   ├── PredictionPanel.jsx
│   │   ├── RasterAssets.jsx
│   │   └── YieldChart.jsx
│   ├── services/
│   │   └── api.js
│   ├── App.css
│   ├── App.jsx
│   ├── index.css
│   └── index.js
└── package.json

