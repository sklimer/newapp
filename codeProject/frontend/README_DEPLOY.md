# Deployment Guide for Vercel and Render

## Issue
After deployment on Vercel and Render, the application shows:
```
404: NOT_FOUND
Code: NOT_FOUND
```

## Root Cause
The 404 error occurs because Single Page Applications (SPA) with client-side routing need special server configuration to handle all routes properly. Without proper configuration, navigating to any route other than the root will result in a 404 error.

## Solutions

### For Vercel Deployment

1. **Add vercel.json** to your project root:
```json
{
  "rewrites": [
    {"source": "/(.*)", "destination": "/"}
  ],
  "trailingSlash": false
}
```

2. **Build command**: `npm run build`
3. **Output directory**: `dist`
4. **Framework preset**: None/Other

### For Render Deployment

1. **Using the provided server.js**:
The project includes a properly configured Express server that handles all routes:

```javascript
// For any route that doesn't match a static file, serve index.html
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});
```

2. **Build command**: `npm run build`
3. **Start command**: `node server.js`

Alternatively, you can use the provided Dockerfile for containerized deployment.

### Key Points

- Client-side routing requires server configuration to handle all routes
- The catch-all route (`*`) ensures that all URLs serve the main index.html file
- Static assets are served separately while dynamic routes are handled by the SPA
- Make sure your build process creates the `dist` folder with all necessary files

## Files Included
- `vercel.json` - Configuration for Vercel deployments
- `server.js` - Express server with proper routing for SPA
- `Dockerfile` - Container configuration for flexible deployment
- `nginx.conf` - Sample Nginx configuration (for custom setups)