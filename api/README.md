PHASE 2 

USING WSL to create the api


# Instalar
pip install -r requirements.txt

# Rodar (cria simulations.db automaticamente)
uvicorn main:app --reload --port 8000

# Testar
http://localhost:8000/docs


## testar o mqtt simulator

### Ver containers ativos
docker ps

### Ver logs do simulador
docker logs sim-abc123

### Subscrever ao broker público para ver dados
mosquitto_sub -h test.mosquitto.org -t "fabrica/sensor/1"