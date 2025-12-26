# Industrial Factory Simulation Configuration

This configuration simulates a complete industrial manufacturing facility with realistic sensor data across all production stages.

## Factory Overview

The simulation covers **10 major areas** of a modern industrial facility:

### 1. **Raw Material Intake** (`factory/rawmaterial/intake`)
- **Update Interval**: 15 seconds
- **Metrics**:
  - Material received (kg)
  - Quality grade (85-100%)
  - Storage level (20-95%)
- **Use Case**: Monitor incoming raw materials, quality control, inventory management

### 2. **Production Lines** (`factory/production/line/1-3`)
- **Update Interval**: 5 seconds (real-time monitoring)
- **3 Parallel Production Lines** with metrics:
  - Machine temperature (65-85°C)
  - Pressure (2.0-6.5 bar)
  - Speed (800-1500 RPM)
  - Vibration (0.5-4.5 mm/s) - for predictive maintenance
  - Production count (cumulative)
  - Defect count
  - Power consumption (15-45 kW)
- **Use Case**: Real-time production monitoring, predictive maintenance, quality tracking

### 3. **Assembly Stations** (`factory/assembly/station/1-5`)
- **Update Interval**: 8 seconds
- **5 Assembly Stations** with metrics:
  - Assembly count (cumulative)
  - Cycle time (45-90 seconds)
  - Robot position (X/Y coordinates)
  - Tool usage percentage
  - Error count
- **Use Case**: Robot tracking, process optimization, bottleneck detection

### 4. **Quality Inspection** (`factory/quality/inspection/1-2`)
- **Update Interval**: 10 seconds
- **2 Inspection Stations** with metrics:
  - Inspected units (cumulative)
  - Pass rate (92-99.9%)
  - Rejected units
  - Dimension tolerance (0.01-0.15 mm)
  - Surface quality score (70-100)
- **Use Case**: Quality control, defect tracking, process improvement

### 5. **Packaging Line** (`factory/packaging/line1`)
- **Update Interval**: 12 seconds
- **Metrics**:
  - Packages completed (cumulative)
  - Packaging speed (20-60 units/min)
  - Label errors
  - Material waste (kg)
  - Conveyor speed (10-30 m/min)
- **Use Case**: Packaging efficiency, waste reduction, throughput monitoring

### 6. **Warehouse Storage** (`factory/warehouse/storage`)
- **Update Interval**: 20 seconds
- **Metrics**:
  - Finished goods inventory (500-10,000 units)
  - Storage utilization (40-95%)
  - Temperature control (18-24°C)
  - Humidity (35-65%)
  - Outbound shipments (cumulative)
- **Use Case**: Inventory management, environmental control, logistics

### 7. **Energy Monitoring** (`factory/energy/monitoring`)
- **Update Interval**: 10 seconds
- **Metrics**:
  - Total power consumption (150-450 kW)
  - Voltage (380-400V)
  - Current (200-800A)
  - Power factor (0.85-0.98)
  - Daily consumption (cumulative kWh)
- **Use Case**: Energy management, cost optimization, sustainability

### 8. **HVAC System** (`factory/hvac/system`)
- **Update Interval**: 15 seconds
- **Metrics**:
  - Ambient temperature (20-26°C)
  - Target temperature (21-23°C)
  - Humidity (40-60%)
  - Air quality index (20-80)
  - Filter pressure drop (50-250 Pa)
- **Use Case**: Environmental control, worker comfort, equipment protection

### 9. **Maintenance Alerts** (`factory/maintenance/alerts`)
- **Update Interval**: 30 seconds
- **Metrics**:
  - Active alerts count
  - Preventive maintenance due
  - Machine uptime (85-99.5%)
  - MTBF - Mean Time Between Failures (200-2000 hours)
- **Use Case**: Preventive maintenance, downtime reduction, reliability tracking

## Data Characteristics

### Sensor Behavior

The simulator uses realistic sensor patterns:

- **RETAIN_PROBABILITY**: How often values stay stable (simulates steady-state operation)
- **INCREASE_PROBABILITY**: Tendency for cumulative counters to increase
- **MAX_STEP**: Maximum change between readings (simulates realistic sensor noise)

### Example Behaviors

**Production Counter** (cumulative metric):
- INCREASE_PROBABILITY: 0.95 (almost always increasing)
- RETAIN_PROBABILITY: 0.3 (changes frequently)
- Result: Steadily increasing production count with occasional pauses

**Temperature** (stable metric):
- RETAIN_PROBABILITY: 0.85 (stable most of the time)
- MAX_STEP: 1.5°C (small variations)
- Result: Stable temperature with minor fluctuations

**Defects** (rare events):
- INCREASE_PROBABILITY: 0.15 (rarely increases)
- RETAIN_PROBABILITY: 0.9 (usually stays the same)
- Result: Occasional defects, mostly zero

## Usage

### For Local MQTT Broker

```bash
cd mqtt-simulator-master/mqtt-simulator
python main.py -f ../config/settings_industrial_factory.json -v
```

### For Azure IoT Hub

1. Update the connection string in `settings_industrial_factory_azure.json`:
   ```json
   "AZURE_CONNECTION_STRING": "HostName=your-hub.azure-devices.net;DeviceId=factory-001;SharedAccessKey=..."
   ```

2. Run the simulator:
   ```bash
   python main.py -f ../config/settings_industrial_factory_azure.json -v
   ```

## Data Volume

**Total Topics**: 18 telemetry streams
- 1 Raw material intake
- 3 Production lines
- 5 Assembly stations
- 2 Quality inspection stations
- 1 Packaging line
- 1 Warehouse
- 1 Energy monitoring
- 1 HVAC system
- 1 Maintenance alerts

**Message Frequency**:
- Fastest: Production lines (every 5 seconds)
- Slowest: Maintenance alerts (every 30 seconds)
- **Average**: ~100 messages per minute across all topics

## Monitoring Examples

### MQTT Subscription

Monitor specific areas:
```bash
# All factory data
mosquitto_sub -t "factory/#" -v

# Production lines only
mosquitto_sub -t "factory/production/#" -v

# Quality metrics
mosquitto_sub -t "factory/quality/#" -v

# Energy and utilities
mosquitto_sub -t "factory/energy/#" -t "factory/hvac/#" -v
```

### Azure IoT Hub Monitoring

```bash
# Monitor all telemetry
az iot hub monitor-events --hub-name your-hub-name

# Filter by topic property
az iot hub monitor-events --hub-name your-hub-name --properties anno sys
```

## Dashboard Visualization Ideas

### Production Dashboard
- Real-time production count from all lines
- Defect rates and quality metrics
- Machine temperature and vibration trends
- Overall Equipment Effectiveness (OEE)

### Energy Dashboard
- Real-time power consumption
- Daily/weekly energy trends
- Power factor monitoring
- Cost estimation

### Quality Dashboard
- Pass/fail rates from inspection
- Defect trending
- Dimension tolerance distribution
- Surface quality scores

### Maintenance Dashboard
- Active alerts by severity
- Machine uptime percentages
- MTBF trending
- Preventive maintenance schedule

## Customization

To adjust the simulation:

1. **Change update frequency**: Modify `TIME_INTERVAL` (in seconds)
2. **Adjust value ranges**: Modify `MIN_VALUE`, `MAX_VALUE`
3. **Change variability**: Adjust `MAX_STEP`
4. **Make more stable**: Increase `RETAIN_PROBABILITY`
5. **Add more production lines**: Increase `RANGE_END`

### Example: Add a 4th production line

Change:
```json
"PREFIX": "factory/production/line",
"RANGE_START": 1,
"RANGE_END": 3,
```

To:
```json
"PREFIX": "factory/production/line",
"RANGE_START": 1,
"RANGE_END": 4,
```

## Real-World Use Cases

1. **Training & Education**: Learn IoT/IIoT concepts without physical hardware
2. **Dashboard Development**: Test visualization tools with realistic data
3. **Algorithm Testing**: Develop anomaly detection, predictive maintenance
4. **Cloud Integration**: Test Azure IoT, AWS IoT, or other platforms
5. **Load Testing**: Simulate high-volume industrial data streams
6. **Demo & Presentations**: Show industrial IoT capabilities

## Anomaly Simulation

To simulate anomalies, you can modify the configuration:

**High temperature alert** (production line):
```json
"machine_temperature_celsius": {
  "MIN_VALUE": 80.0,  // Increased from 65
  "MAX_VALUE": 95.0,  // Increased from 85
}
```

**Quality issues**:
```json
"pass_rate_percent": {
  "MIN_VALUE": 75.0,  // Decreased from 92
  "MAX_VALUE": 90.0,  // Decreased from 99.9
}
```

**High vibration** (predictive maintenance):
```json
"vibration_mm_s": {
  "MIN_VALUE": 3.0,   // Increased from 0.5
  "MAX_VALUE": 8.0,   // Increased from 4.5
}
```

## Support

For issues or questions about the industrial factory simulation, refer to:
- Main README: `mqtt-simulator-master/README.md`
- Azure Integration: `mqtt-simulator-master/README_AZURE_INTEGRATION.md`
