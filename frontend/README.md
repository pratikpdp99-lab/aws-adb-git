# frontend/

Next.js / React frontend for the TDM Deckers platform.

## Structure

```
src/
  pages/
    index.tsx        Dataset browser (fetches from /datasets)
    requests.tsx     Test data request form
  components/
    DatasetCard.tsx  Dataset summary card
public/              Static assets
.env.local.example   Environment variable template
package.json
```

## Local run

```bash
cd frontend
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL

npm install
npm run dev
```

App runs at: http://localhost:3000

## Pages

| Path        | Description                                  |
|-------------|----------------------------------------------|
| `/`         | Dataset browser — lists available TDM datasets |
| `/requests` | Submit a new test data request               |

## Environment variables

| Variable                | Description                        |
|-------------------------|------------------------------------|
| `NEXT_PUBLIC_API_URL`   | FastAPI backend URL (default: http://localhost:8000) |
