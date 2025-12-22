# Deployment Guide

This project is configured for deployment with **Render (Backend)** and **Vercel (Frontend)**.

## Prerequisites

- GitHub account (where this repo is pushed).
- Render.com account.
- Vercel.com account.

## 1. Deploy Backend to Render

We use a PostgreSQL database and a Python web service.

1.  Log in to [Render](https://dashboard.render.com/).
2.  Click **New +** -> **Blueprint**.
3.  Connect to your GitHub repository `project-management-app`.
4.  Render will detect `render.yaml` and propose to create:
    -   `project-management-db` (PostgreSQL Database)
    -   `project-management-backend` (Web Service)
5.  Click **Apply**.
6.  Wait for the deployment to finish.
7.  Copy the URL of the deployed backend (e.g., `https://project-management-backend.onrender.com`).

## 2. Deploy Frontend to Vercel

1.  Log in to [Vercel](https://vercel.com).
2.  Click **Add New...** -> **Project**.
3.  Import `project-management-app` from GitHub.
4.  **Important Configuration**:
    -   **Framework Preset**: Vite (should be auto-detected).
    -   **Root Directory**: Click `Edit` and select `frontend`.
    -   **Environment Variables**:
        -   Name: `VITE_API_URL`
        -   Value: `https://<YOUR-RENDER-BACKEND-URL>/api` (Make sure to include `/api` at the end).
5.  Click **Deploy**.

## 3. Final Step: Connect Frontend to Backend

1.  Once Vercel deployment is complete, copy your frontend domain (e.g., `https://project-management-app.vercel.app`).
2.  Go back to **Render Dashboard** -> **Env Groups** or directly to your Web Service settings.
3.  Update the `CORS_ORIGINS` environment variable to match your Vercel URL (e.g., `https://project-management-app.vercel.app`).
    -   *Note: In the Blueprint `render.yaml`, we set a placeholder. You must update this for the frontend to access the backend.*
4.  Redeploy the backend (Manual Deploy -> Deploy latest commit) if you changed env vars.

## Troubleshooting

-   **CORS Errors**: Ensure `CORS_ORIGINS` in Render exactly matches your Vercel URL (no trailing slash usually, or check browser console).
-   **Database**: The `render.yaml` sets up a managed PostgreSQL. The code automatically uses `DATABASE_URL`.
