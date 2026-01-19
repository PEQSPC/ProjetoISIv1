# PHASE 2 Project (API REST + Docker Local + SQLite)

## Instalar

pip install -r requirements.txt

## Rodar (cria simulations.db automaticamente)
(Adicionar env variables) -> SIMULATOR_IMAGE=ghcr.io/peqspc/mqtt-simulator:latest
uvicorn main:app --reload --port 8000

## Testar

[URL TO TEST](http://localhost:8000/docs)

## Ver containers ativos

docker ps

## Ver logs do simulador

docker logs sim-abc123

### Subscrever ao broker público para ver dados

mosquitto_sub -h test.mosquitto.org -t "fabrica/sensor/1"
