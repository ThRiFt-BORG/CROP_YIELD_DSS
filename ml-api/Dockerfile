FROM crop-python-geo-base

WORKDIR /app

COPY --from=crop-python-wheels /wheels /wheels
COPY ml-api/requirements.txt .

RUN pip install --no-index --find-links=/wheels -r requirements.txt

COPY ml-api .
COPY shared /app/shared

ENV GUNICORN_WORKERS=2

CMD gunicorn main:app \
  --workers ${GUNICORN_WORKERS} \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
