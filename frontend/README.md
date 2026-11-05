# Frontend

React + Vite. Consume la API de `api/` (contrato C8).

```bash
npm install
npm run dev        # http://localhost:5173
```

La URL de la API se toma de `VITE_API_URL` (ver `.env.example`); por defecto `http://localhost:8000`. La API tiene que estar corriendo: `uvicorn api.main:app --reload` desde la raíz del repo.
