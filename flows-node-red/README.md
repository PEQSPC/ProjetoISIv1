# Production Line Monitoring System - Node-RED Flows

IoT-based monitoring system for tracking production line stations using MQTT, Node-RED, and SQLite.

## Overview

This Node-RED project implements a real-time monitoring system for an industrial production line with three stations (Estacao 1, 2, 3). The system collects sensor data via MQTT, processes and accumulates metrics, stores data persistently, and provides a web-based UI for visualization.

## System Architecture

```
MQTT Simulator → MQTT Broker (localhost:1883)
                       ↓
              Node-RED Flow Engine
                       ↓
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   CSV Files    SQLite Database   Web UI
```

## Data Flow

### MQTT Topics
- `linha_producao/estacao/1` - Station 1 data
- `linha_producao/estacao/2` - Station 2 data  
- `linha_producao/estacao/3` - Station 3 data

### Message Format
```json
{
  "producao": 100,
  "paragem": 5,
  "stock": 50,
  "defeitos": 2
}
```

After processing:
```json
{
  "codigo_produto": "1",
  "estacao": "1",
  "timestamp": "2024-10-19T10:30:00.000Z",
  "dados": {
    "producao": 100,
    "paragem": 5,
    "stock": 50,
    "defeitos": 2
  }
}
```

## Key Metrics

- **Producao** - Production units completed
- **Paragem** - Downtime/stoppage duration
- **Stock** - Current inventory level
- **Defeitos** - Defective units count

## Components

### 1. MQTT Subscribers
Three MQTT input nodes subscribed to respective station topics with QoS 2 (exactly once delivery).

### 2. Data Processing Functions
- **Timestamp Addition** - Adds ISO timestamp to incoming messages
- **Station ID Tagging** - Tags messages with station identifier
- **Product Code Mapping** - Associates data with product codes
- **Data Accumulation** - Maintains running totals for all metrics

### 3. Data Persistence

#### CSV Export
- File: `estacao1.csv`
- Format: `estacao,timestamp,producao,paragem,stock,defeitos`
- Mode: Append (preserves historical data)

#### SQLite Database
- File: `sql-db-estacao.db`
- Table: `registo_estacoes`
- Stores accumulated metrics with timestamps

Database schema:
```sql
CREATE TABLE registo_estacoes (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Producao INTEGER,
    Stock INTEGER,
    Paragem INTEGER,
    Defeitos INTEGER,
    Id_Estacao INTEGER,
    Timestamp TEXT
);
```

#### Accumulated Totals
- File: `estacao3acumulado.txt`
- Real-time accumulated metrics for Station 3
- Overwritten on each update

### 4. Web UI
- Framework: UIBuilder with Vue 3 (IIFE, no-build template)
- URL: `http://localhost:1880/uitest`
- Displays real-time station data

## Flow Versions

### flowsnodered.json / flows.json (Base Version)
- Initial implementation
- MQTT subscription setup
- Basic CSV logging
- Simple accumulation (producao, stock)

### flows181025.json (18 Oct 2024)
- Added SQLite database integration
- Comprehensive accumulation (all 4 metrics)
- Database insert functionality
- Improved data structuring

### flows191025.json (19 Oct 2024 - Latest)
- Product code tracking (`codigo_produto`)
- Refined station identification
- Prepared for API integration
- Enhanced data model

## Setup Instructions

### Prerequisites
- Node-RED installed
- Node modules:
  - `node-red-contrib-uibuilder` (v7.5.0)
  - `node-red-node-sqlite` (v1.1.1)
- MQTT broker running on localhost:1883

### Installation

1. Import the desired flow file into Node-RED:
   ```bash
   # For latest version
   flows191025.json
   ```

2. Update file paths in the flow:
   - CSV file path (currently: `D:\Escola_3ano\ISI\ProjetoISIv1\estacao1.csv`)
   - SQLite database path (currently: `D:\Escola_3ano\ISI\ProjetoISIv1\flows-node-red\data\sql-db-estacao.db`)
   - Accumulated data file path (currently: `D:\Escola_3ano\ISI\ProjetoISIv1\estacao3acumulado.txt`)

3. Deploy the flow

4. Start your MQTT simulator publishing to the configured topics

5. Access the UI at: `http://localhost:1880/uitest`

## MQTT Broker Configuration

```
Host: 127.0.0.1
Port: 1883
Protocol: MQTT v4
Keep Alive: 60s
Clean Session: true
```

## Data Accumulation Logic

The system maintains running totals in flow context:
- `producao_acc` - Total production
- `stock_acc` - Current stock level
- `paragem_acc` - Total downtime
- `defeitos_acc` - Total defects

Each incoming message increments these counters, providing cumulative metrics over the system's runtime.

## Future Enhancements (TODO)

### Planned Features
1. **Margin Reports** - Email-based performance reports
2. **Product Pricing API** - Real-time cost tracking
   - API integration for product pricing
   - Regex filtering by product ID
   - Cost calculations: `price × production_count`
3. **Alert System** - Automated notifications for anomalies
4. **Global Configuration** - Centralized settings file
5. **Time-based Metrics** - Per-minute production tracking

## Troubleshooting

### MQTT Connection Issues
- Verify MQTT broker is running: `mosquitto -v`
- Check broker address and port in MQTT broker node

### Database Errors
- Ensure SQLite database file exists
- Verify write permissions on database file
- Check database schema matches INSERT statements

### UI Not Loading
- Confirm UIBuilder is properly installed
- Check Node-RED logs for errors
- Verify URL path: `/uitest`

## File Structure

```
project-folder/
├── flows191025.json          # Latest flow (recommended)
├── flows181025.json          # Previous version with DB
├── flows.json                # Earlier version
├── flowsnodered.json         # Initial version
├── estacao1.csv              # Station 1 historical data
├── sql-db-estacao.db         # SQLite database
├── estacao3acumulado.txt     # Station 3 current totals
└── README.md                 # This file
```

## Integration with IoT Simulation Platform

This Node-RED flow demonstrates a real-world IoT data pipeline that can inform your IoT simulation platform development:

- **Data Patterns** - Realistic sensor data structures and frequencies
- **MQTT Usage** - Topic design and QoS considerations
- **Data Processing** - Timestamp injection, accumulation, transformation
- **Multi-sink Architecture** - CSV, database, and UI outputs
- **Station Isolation** - Independent data streams per physical/virtual sensor

## License

Educational project - ISI Course, 3rd Year

## Contact

Project: ProjetoISI  
Course: Integração de Sistemas de Informação (ISI)