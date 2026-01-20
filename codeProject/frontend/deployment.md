# Deployment Instructions for Vercel and Render

## Problem
After deployment on Vercel and Render, the application shows:
```
404: NOT_FOUND
Code: NOT_FOUND
```

## Solution

### 1. Fix Build Process
First, ensure your application builds correctly:

```bash
npm install
npm run build
```

### 2. Vercel Configuration
Create a `vercel.json` file in your project root:

```json
{
  "rewrites": [
    {"source": "/(.*)", "destination": "/"}
  ],
  "trailingSlash": false
}
```

This configuration ensures that all routes are handled by the main index.html file, which is essential for SPA (Single Page Applications).

### 3. Render Configuration
For Render, make sure your start command serves the built files correctly. You can use the included server.js file:

```javascript
// server.js
const express = require('express');
const path = require('path');
const app = express();

// Serve static files from the dist folder
app.use(express.static(path.join(__dirname, 'dist')));

// For any route that doesn't match a static file, serve index.html
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on port ${PORT}`);
});
```

Set your Render build command to:
```
npm run build
```

And start command to:
```
node server.js
```

### 4. Key Points
- The 404 error typically occurs because client-side routing isn't properly configured on the server
- Single Page Applications need server configuration to handle all routes and serve the main index.html file
- The `try_files` directive in Nginx or catch-all route in Express ensures all routes are handled properly