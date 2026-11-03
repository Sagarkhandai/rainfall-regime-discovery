# Deploy Rainfall Atlas (GitHub + Render)

This project is one FastAPI web service: the FastAPI backend serves the dashboard in `static/index.html` and the API from `/api`.

## 1. Publish the source on GitHub

1. Extract the project folder.
2. Create a new GitHub repository (for example, `rainfall-atlas-ca`).
3. Upload/commit the contents of this folder to the repository's `main` branch. Do not upload the ZIP as a single file.
4. Keep `data/weatherAUS.csv` in the repository. Do not commit `.env`, virtual environments, or Python cache files.

## 2. Deploy on Render

1. Sign in to Render and choose **New + → Blueprint**.
2. Connect GitHub, select the Rainfall Atlas repository, and choose the branch containing `render.yaml`.
3. Review the service configuration detected from `render.yaml`, then create/deploy it.
4. Wait for the first deploy to finish successfully. The service health endpoint is `/api/info`.
5. Open the public `https://<service-name>.onrender.com` URL. The dashboard and API are served from the same origin.

The Blueprint config uses:

- Runtime: Python 3.11.11 (from `.python-version`)
- Build: `pip install -r backend/requirements.txt`
- Start: `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT`
- Health check: `/api/info`

## Important notes for an academic demonstration

- The first deployment performs data loading and model/cache initialization, so the initial startup can take longer than a simple static website.
- Render Free web services spin down after 15 minutes without inbound traffic and can take about a minute to wake on the next visit. Open the public URL shortly before your instructor's demonstration.
- The Free service filesystem is ephemeral. The checked-in dataset and initial experiment registry are part of the deployment, but new experiment-registry writes on the running service should not be treated as permanent records.
- Check the Render deploy logs and open `/api/info` and `/docs` after deployment. Share the public dashboard URL with your instructor; optionally include the GitHub repository URL for source review.
