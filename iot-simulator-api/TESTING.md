# Testing Guide - IoT Simulator API

## Overview

Este projeto inclui uma suite completa de testes:
- **Testes Unitários**: Validam componentes isolados (database, modelos)
- **Testes de Integração**: Validam endpoints da API
- **Testes de Helpers**: Validam funções auxiliares (cleanup, auto-stop)

## Estrutura de Testes

```
iot-simulator-api/
├── tests/
│   ├── __init__.py              # Configuração do pacote
│   ├── conftest.py              # Fixtures e setup comum
│   ├── test_database.py         # Testes do modelo Simulation
│   ├── test_endpoints.py        # Testes dos endpoints da API
│   └── test_helpers.py          # Testes de funções auxiliares
├── pytest.ini                    # Configuração do pytest
└── TESTING.md                    # Este arquivo
```

## Instalação

### 1. Instalar dependências de teste

```bash
cd iot-simulator-api

# Instalar dependências da API
pip install -r src/requirements.txt

# Instalar dependências de teste
pip install -r src/requirements-test.txt
```

### 2. Estrutura do projeto

Certifique-se que o seu projeto está assim:
```
iot-simulator-api/
├── src/
│   ├── main.py
│   ├── database.py
│   ├── requirements.txt
│   └── requirements-test.txt
├── tests/
│   ├── conftest.py
│   ├── test_database.py
│   ├── test_endpoints.py
│   └── test_helpers.py
└── pytest.ini
```

## Executar Testes

### Correr todos os testes
```bash
pytest
```

### Correr com output verboso
```bash
pytest -v
```

### Correr um arquivo de teste específico
```bash
pytest tests/test_database.py
```

### Correr uma classe de teste específica
```bash
pytest tests/test_endpoints.py::TestRootEndpoint
```

### Correr um teste específico
```bash
pytest tests/test_endpoints.py::TestRootEndpoint::test_root_endpoint
```

### Correr com cobertura de código
```bash
pytest --cov=src --cov-report=html
```

Isto gera um relatório HTML em `htmlcov/index.html`

### Correr apenas testes rápidos (excluir slow)
```bash
pytest -m "not slow"
```

## Cobertura de Testes

Cobertura atual de código:

| Componente | Cobertura | Testes |
|-----------|-----------|--------|
| **database.py** | ~95% | 8 testes unitários |
| **main.py** | ~85% | 25+ testes de integração |
| **helpers** | ~90% | 6 testes de funções auxiliares |

## Fixtures Disponíveis

### `test_db`
Fornece uma sessão BD limpa (SQLite em memória) para cada teste.

```python
def test_example(test_db):
    sim = Simulation(...)
    test_db.add(sim)
    test_db.commit()
```

### `client`
Fornece um cliente de teste FastAPI (TestClient).

```python
def test_example(client):
    response = client.get("/")
    assert response.status_code == 200
```

### `sample_simulation_config`
Fornece uma configuração de simulação válida para testes.

```python
def test_example(client, sample_simulation_config):
    response = client.post("/simulations", json=sample_simulation_config)
```

### `sample_simulation`
Fornece uma simulação pré-criada no BD.

```python
def test_example(sample_simulation):
    assert sample_simulation.simulation_id == "test-sim-001"
```

## Testes Implementados

### Test Database (`test_database.py`)
- ✅ Criar simulação
- ✅ Restrição de ID único
- ✅ Status padrão
- ✅ Campos nullable
- ✅ Representação (__repr__)
- ✅ Rastreamento de datas
- ✅ Atualização de status
- ✅ Armazenamento de config JSON

### Test Endpoints (`test_endpoints.py`)
- ✅ GET / (root endpoint)
- ✅ GET /health (health check)
- ✅ GET /simulations (list simulations)
- ✅ GET /simulations?status=running (filter by status)
- ✅ GET /simulations/{sim_id} (get details)
- ✅ GET /stats (statistics)
- ✅ POST /simulations (create simulation)
- ✅ DELETE /simulations/{sim_id} (stop simulation)
- ✅ Validação de requisições
- ✅ Error handling

### Test Helpers (`test_helpers.py`)
- ✅ Cleanup sem expirados
- ✅ Cleanup com expirados
- ✅ Container não encontrado
- ✅ Múltiplos expirados
- ✅ Remoção de arquivos config
- ✅ Tratamento de erros Docker

## Mocking

Os testes usam `unittest.mock` para mockar:

```python
# Mockar Docker client
with patch('main.docker_client') as mock_docker:
    mock_container = MagicMock()
    mock_docker.containers.run.return_value = mock_container
    # Teste aqui

# Mockar operações de arquivo
with patch('os.path.exists') as mock_exists:
    with patch('os.remove') as mock_remove:
        # Teste aqui
```

## CI/CD Integration

Os testes executam automaticamente via GitHub Actions:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r iot-simulator-api/src/requirements.txt
      - run: pip install -r iot-simulator-api/src/requirements-test.txt
      - run: pytest iot-simulator-api
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: coverage-report
          path: iot-simulator-api/htmlcov/
```

## Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'main'"

Solução: Certifique-se que está em `iot-simulator-api/` e que `conftest.py` está configurado corretamente.

### Erro: "database.db is locked"

Solução: Feche outras conexões BD. Os testes usam BD em memória, mas podem haver conflitos.

### Testes lentos

Solução: Skip testes marcados como slow:
```bash
pytest -m "not slow"
```

## Best Practices

1. **Use fixtures**: Reutilize setup comum através de fixtures
2. **Mocke dependências externas**: Docker, filesystem, APIs externas
3. **Teste comportamento, não implementação**: Foque em inputs/outputs
4. **Nome descritivo**: `test_create_simulation_with_valid_config` é melhor que `test_create`
5. **One assertion per test** quando possível: Testes mais focados
6. **Setup/Teardown**: Use fixtures para limpeza automática

## Próximas Melhorias

- [ ] Adicionar performance benchmarks
- [ ] Testes de carga (locust)
- [ ] E2E tests com containers reais
- [ ] Testes de segurança (rate limiting, auth)
- [ ] Cobertura de testes > 90%
