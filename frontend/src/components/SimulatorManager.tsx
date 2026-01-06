import { useEffect, useState } from 'react';
import { 
  Typography, Container, Button, Card, CardContent, 
  TextField, Dialog, DialogTitle, DialogContent, DialogActions, 
  CircularProgress, Alert, Chip, Box, AppBar, Toolbar
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import axios from 'axios';

// Configuração da API
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface Simulation {
  simulation_id: string;
  status: string;
  created_at: string;
  duration_minutes: number;
}

// JSON Default para facilitar a vida ao utilizador
const DEFAULT_JSON = JSON.stringify({
  "BROKER_URL": "test.mosquitto.org",
  "BROKER_PORT": 1883,
  "TIME_INTERVAL": 2,
  "TOPICS": [{
    "TYPE": "multiple",
    "PREFIX": "fabrica/sensor",
    "RANGE_START": 1,
    "RANGE_END": 3,
    "DATA": [{
      "NAME": "temperatura",
      "TYPE": "float",
      "MIN_VALUE": 20,
      "MAX_VALUE": 35,
      "MAX_STEP": 1.5,
      "INCREASE_PROBABILITY": 0.6
    }]
  }],
  "duration_minutes": 2
}, null, 2);

interface SimulatorManagerProps {
  onBackToHome?: () => void;
}

export default function SimulatorManager({ onBackToHome }: SimulatorManagerProps) {
  const [simulations, setSimulations] = useState<Simulation[]>([]);
  const [open, setOpen] = useState(false);
  const [configJson, setConfigJson] = useState(DEFAULT_JSON);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [jsonError, setJsonError] = useState<string | null>(null);

  // Carregar simulações
  const fetchSimulations = async () => {
    try {
      setError(null);
      const res = await axios.get(`${API_URL}/simulations`);
      console.log("Simulações carregadas:", res.data);
      setSimulations(res.data || []);
    } catch (error) {
      console.error("Erro ao buscar simulações:", error);
      setError("Erro ao carregar simulações. Verifica se a API está a correr.");
      setSimulations([]);
    } finally {
      setLoading(false);
    }
  };

  // Atualizar a lista a cada 5 segundos
  useEffect(() => {
    fetchSimulations();
    const interval = setInterval(fetchSimulations, 5000);
    return () => clearInterval(interval);
  }, []);

  // Validar JSON
  const validateJSON = (jsonString: string): boolean => {
    try {
      JSON.parse(jsonString);
      setJsonError(null);
      return true;
    } catch (e) {
      console.error("Erro de JSON:", e);
      setJsonError("JSON inválido. Verifica a sintaxe.");
      return false;
    }
  };

  // Criar Simulação
  const handleCreate = async () => {
    if (!validateJSON(configJson)) {
      return;
    }

    setCreating(true);
    try {
      await axios.post(`${API_URL}/simulations`, JSON.parse(configJson));
      setOpen(false);
      setConfigJson(DEFAULT_JSON); // Reset para default
      fetchSimulations(); // Atualiza logo
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || "Erro ao criar simulação";
      setError(errorMessage);
      console.error("Erro ao criar:", error);
    } finally {
      setCreating(false);
    }
  };

  // Parar Simulação
  const handleDelete = async (simulationId: string) => {
    if(!confirm("Tens a certeza que queres parar esta simulação?")) return;
    try {
      await axios.delete(`${API_URL}/simulations/${simulationId}`);
      fetchSimulations();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || "Erro ao parar simulação";
      setError(errorMessage);
      console.error("Erro ao apagar:", error);
    }
  };

  // Formatar data
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('pt-PT');
    } catch {
      return dateString;
    }
  };

  return (
    <div id="simulator-manager" style={{ backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          {onBackToHome && (
            <Button
              startIcon={<ArrowBackIcon />}
              onClick={onBackToHome}
              color="inherit"
              sx={{ mr: 2 }}
            >
              Voltar
            </Button>
          )}
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            IoT Manager
          </Typography>
        </Toolbar>
      </AppBar>
      <Container sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
          <Typography variant="h4">Simulações Ativas</Typography>
          <Button 
            variant="contained" 
            onClick={() => setOpen(true)}
            sx={{ py: 1.5 }}
          >
            Nova Simulação
          </Button>
        </Box>
        
        {error && (
          <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
            <CircularProgress />
          </Box>
        ) : simulations.length === 0 ? (
          <Typography color="text.secondary" sx={{ mt: 2 }}>
            Nenhuma simulação a correr neste momento.
          </Typography>
        ) : (
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }, gap: 3 }}>
            {simulations.map((sim) => (
              <Card key={sim.simulation_id}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {sim.simulation_id}
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Chip 
                      label={sim.status} 
                      color={sim.status === 'running' ? 'success' : 'default'}
                      size="small"
                      sx={{ mr: 1 }}
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Criada:</strong> {formatDate(sim.created_at)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Duração:</strong> {sim.duration_minutes} minutos
                  </Typography>
                  {sim.status !== 'stopped' && (
                    <Button 
                      startIcon={<DeleteIcon />} 
                      color="error" 
                      variant="outlined"
                      onClick={() => handleDelete(sim.simulation_id)}
                      sx={{ mt: 2 }}
                      fullWidth
                    >
                      Parar Simulação
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
          </Box>
        )}
      </Container>

      {/* Modal de Criação */}
      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>Configurar Nova Simulação</DialogTitle>
        <DialogContent>
          {jsonError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {jsonError}
            </Alert>
          )}
          <TextField
            autoFocus
            margin="dense"
            label="Configuração JSON"
            fullWidth
            multiline
            rows={15}
            value={configJson}
            onChange={(e) => {
              const value = e.target.value;
              setConfigJson(value);
              validateJSON(value);
            }}
            sx={{ fontFamily: 'monospace', mt: 1 }}
            error={!!jsonError}
            helperText={jsonError || "Configuração do simulador em formato JSON"}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setOpen(false);
            setJsonError(null);
            setConfigJson(DEFAULT_JSON);
          }}>
            Cancelar
          </Button>
          <Button 
            onClick={handleCreate} 
            variant="contained" 
            disabled={creating || !!jsonError}
          >
            {creating ? <CircularProgress size={24} /> : 'Iniciar Simulação'}
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}

