# Telegram Restaurant Mini App - Frontend

This is the frontend for a Telegram mini app that allows restaurants to receive orders for delivery and pickup through the Telegram messenger.

## Features

- Browse restaurant menu
- Add items to cart
- Calculate delivery fees based on distance
- Multiple payment options (card, cash)
- Bonus system integration
- Order tracking
- User profile management

## Tech Stack

- React with TypeScript
- Vite as build tool
- React Router for navigation
- Redux Toolkit for state management
- Axios for API calls

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
VITE_API_URL=http://localhost:8000/api/v1
```

For production deployments, create a `.env.production` file with your production API URL.

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run serve` - Serve production build
- `npm run preview` - Preview production build
- `npm run lint` - Run linter

## Deployment

### Building for Production
To build the application for production:
```bash
npm run build
```

This creates a `dist` folder with the optimized production build.

### Running in Production
After building, you can serve the application using:
```bash
npm run serve
```

Or deploy the `dist` folder to your preferred hosting platform (Vercel, Netlify, etc.).

## Project Structure

```
src/
├── api/              # API service functions
├── components/       # Reusable UI components
├── pages/            # Page components
├── router/           # Routing configuration
├── store/            # Redux store configuration
└── types/            # TypeScript type definitions
```