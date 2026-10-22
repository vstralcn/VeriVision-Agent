# Model Deployment Guide

This project serves the repository's ForensicNet checkpoint through FastAPI. The
runtime never substitutes random probabilities, heatmaps, or analysis fields when
the model is unavailable.

## Runtime Contract

The model lifecycle is owned by `backend/app/services/detection_service.py`:

1. FastAPI loads the checkpoint once during application startup.
2. `/health` reports process liveness.
3. `/ready` returns `200` only when the model has loaded successfully.
4. Detection runs outside the async event loop and returns a model-derived
   probability and localization mask.
5. A missing checkpoint returns `503`; an inference failure returns an explicit
   server error and does not create a detection record.

The API accepts decoded JPEG, PNG, and WebP files up to 10 MB and 40 million
pixels. The service stores the original file and a heatmap only after validation.

## Checkpoint

The default path is:

```text
backend/app/ml_models/weights/best.pt
```

Override it with `MODEL_PATH`. Relative paths are resolved from the backend
working directory. The checkpoint must contain a `model` state dictionary that
matches `ForensicNet`; it is loaded with `weights_only=True`.

Record a trusted checksum before deployment:

```bash
shasum -a 256 backend/app/ml_models/weights/best.pt
```

The repository does not contain sufficient evidence to claim a particular AUC,
accuracy, or cross-dataset performance. Keep the checkpoint checksum, training
configuration, dataset split, preprocessing version, and evaluation output
together when publishing or deploying a model.

## CPU Deployment

The Docker image pins the CPU-compatible runtime used by the current checkpoint:

```text
torch==2.5.1
torchvision==0.20.1
```

Build and start the application:

```bash
docker compose build backend
docker compose up -d
docker compose logs -f backend
```

Check readiness from the host:

```bash
curl -f http://localhost:8000/health
curl -f http://localhost:8000/ready
```

Expected readiness response:

```json
{"status":"ready","model_device":"cpu"}
```

Run the backend verification suite:

```bash
docker compose exec backend python -m pytest
docker compose exec backend ruff check app tests
```

## GPU Deployment

The default image intentionally installs CPU wheels. A GPU deployment needs a
separate image based on a CUDA runtime compatible with the host driver, plus
matching PyTorch and torchvision wheels. Set `USE_GPU=true` only after the
container can run this check:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

Do not silently fall back to CPU if GPU latency is an acceptance requirement.
Expose the selected device through `/ready` and monitor inference latency and
memory use under realistic concurrency.

## Replacing ForensicNet

A replacement model must preserve these behaviors:

- return a calibrated fake probability in `[0, 1]`;
- document the decision threshold and model version;
- return a localization mask only when it is model-derived;
- use the same preprocessing in training, evaluation, and inference;
- raise an explicit unavailable or inference error on failure;
- avoid committing a database result until inference succeeds;
- keep image hashes and certification metadata attributable to the exact input.

Add an independent test dataset and compare the replacement against the current
model before changing the production default. At minimum report AUC, accuracy,
precision, recall, F1, AP, and low-FPR TPR; localization claims also need Dice or
IoU and a faithfulness check.

## Production Checklist

- Set `ENVIRONMENT=production`.
- Replace `SECRET_KEY` and set a separate `CERTIFICATION_KEY`.
- Disable `CREATE_DEFAULT_USERS`.
- Store LLM credentials in a secret manager rather than the database.
- Back up PostgreSQL and uploaded media together.
- Verify `/ready` after every image or checkpoint change.
- Retain the checkpoint checksum and deployment configuration with each result.

The current HMAC certification proves integrity only to parties that trust the
server-held key. Public third-party verification requires an asymmetric signature
scheme and a published key-management policy.
