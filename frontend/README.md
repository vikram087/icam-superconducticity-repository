# Setup of Frontend

This guide provides instructions to set up and run the frontend, which provides an interface for interacting with the ICAM Abstract Database. The frontend allows users to search and view research paper abstracts retrieved from the database.

## Table of Contents
- [Clone the Repository](#1-clone-the-repository)
- [Install Node Modules](#2-install-node-modules)
- [Run the Frontend](#3-run-the-frontend)
- [Next Steps](#next-steps)
- [Troubleshooting](#troubleshooting)

## Setup

### 1. Clone the Repository

Clone the repository containing the frontend code, then navigate to the frontend directory.

   ```bash
   git clone https://github.com/vikram087/icam-materials-database.git
   cd icam-materials-database/frontend/icam-materials-database
   ```

### 2. Setup .env File

Create a `.env` file to define environment variables required for the frontend configuration.

   ```ini
   # The url for your backend, will be http://localhost:8080 for dev
   VITE_BACKEND_URL=http://localhost:8080
   ```

### 3. Install Node Modules

Install the required dependencies for the frontend.

   ```bash
   npm install
   ```

   This command installs all necessary packages listed in `package.json`.

### 4. Run the Frontend

Start the frontend development server:

   ```bash
   npm run dev
   ```

   This will start the frontend on a local development server, typically at `http://localhost:3000`.

## Next Steps

After starting the development server:
- Open your browser and go to `http://localhost:5173` to access the application.
- Explore the search functionality to interact with the ICAM Materials Database.

## Troubleshooting

- **Modules Fail to Install**: Ensure you’re running Node.js version 14 or higher. Run `node -v` to check your version.
- **Server Not Starting**: Check if another application is using port 3000. If so, stop it or modify the port in `package.json`.
- **Frontend Not Loading Correctly**: Clear the browser cache or restart the development server with `npm run dev`.
