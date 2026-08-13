# Atlas Runtime

`atlas-runtime` is a tiny container entrypoint for Project Atlas services. It keeps application code unaware of Atlas or Google Cloud Secret Manager.

## Behavior

- If `ATLAS_CONFIG` is absent, the runtime does nothing and starts the command normally. This preserves ordinary Docker/Compose `.env` workflows.
- If `ATLAS_CONFIG` is present, it must contain a JSON object whose values are strings. Each key is exported as a normal process environment variable.
- `ATLAS_CONFIG` is removed before the application process starts.
- The configured command is executed as a child process and receives normal stdin/stdout/stderr and exit-code propagation.

Example:

```bash
ATLAS_CONFIG='{"DATABASE_URL":"postgres://...","API_KEY":"secret"}' atlas-runtime uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The application sees only `DATABASE_URL` and `API_KEY`; it does not need Atlas-specific code.

## Container integration

A service can use the runtime as its entrypoint:

```dockerfile
COPY --from=ghcr.io/Bobbyjsx/atlas-runtime:TAG /usr/local/bin/atlas-runtime /usr/local/bin/atlas-runtime
ENTRYPOINT ["atlas-runtime"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Locally, keep using `env_file` / `.env`. In Cloud Run, inject `ATLAS_CONFIG` from one Secret Manager secret containing the service's JSON configuration.

The runtime intentionally does not fetch Secret Manager itself. The platform supplies `ATLAS_CONFIG`, keeping cloud credentials and secret-provider logic out of application containers.
