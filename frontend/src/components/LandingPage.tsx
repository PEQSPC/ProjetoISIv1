import { Box, Container, Typography, Button, Card, CardContent, Stepper, Step, StepLabel } from '@mui/material';
import { PlayArrow, Speed, Security, Autorenew } from '@mui/icons-material';

interface LandingPageProps {
  onTryItClick: () => void;
}

export default function LandingPage({ onTryItClick }: LandingPageProps) {
  return (
    <>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          py: { xs: 8, md: 12 },
          minHeight: { xs: '60vh', md: '70vh' },
          display: 'flex',
          alignItems: 'center'
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', maxWidth: '800px', mx: 'auto' }}>
            <Typography
              variant="h1"
              component="h1"
              sx={{
                fontSize: { xs: '2.5rem', md: '4rem' },
                fontWeight: 700,
                mb: 3,
                lineHeight: 1.2
              }}
            >
              Testa Aplicações IoT Sem Hardware
            </Typography>
            <Typography
              variant="h5"
              component="h2"
              sx={{
                fontSize: { xs: '1.25rem', md: '1.5rem' },
                mb: 4,
                opacity: 0.9,
                fontWeight: 300
              }}
            >
              Plataforma SaaS para criar sensores virtuais via API REST
            </Typography>
            <Typography
              variant="body1"
              sx={{
                fontSize: { xs: '1rem', md: '1.125rem' },
                mb: 5,
                opacity: 0.8,
                maxWidth: '600px',
                mx: 'auto'
              }}
            >
              Cria simulações IoT em segundos, configura sensores via JSON e recebe dados MQTT em tempo real. 
              Sem necessidade de hardware físico ou configurações complexas.
            </Typography>
            <Button
              variant="contained"
              size="large"
              onClick={onTryItClick}
              sx={{
                px: 4,
                py: 1.5,
                fontSize: '1.125rem',
                bgcolor: 'white',
                color: 'primary.main',
                '&:hover': {
                  bgcolor: 'rgba(255, 255, 255, 0.9)',
                  transform: 'translateY(-2px)',
                  boxShadow: 4
                },
                transition: 'all 0.3s ease'
              }}
            >
              Try it now
            </Button>
          </Box>
        </Container>
      </Box>

      {/* Features Section */}
      <Box sx={{ py: { xs: 6, md: 10 }, bgcolor: 'background.paper' }}>
        <Container maxWidth="lg">
          <Typography
            variant="h2"
            component="h2"
            sx={{
              textAlign: 'center',
              mb: 6,
              fontSize: { xs: '2rem', md: '2.5rem' },
              fontWeight: 600
            }}
          >
            Porquê Escolher a Nossa Plataforma?
          </Typography>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(4, 1fr)' },
              gap: 3
            }}
          >
            <Card sx={{ height: '100%', '&:hover': { boxShadow: 6, transform: 'translateY(-4px)' }, transition: 'all 0.3s ease' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                  <Speed sx={{ fontSize: 48, color: 'primary.main' }} />
                </Box>
                <Typography variant="h6" gutterBottom sx={{ textAlign: 'center', fontWeight: 600 }}>
                  API REST Simples
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
                  Cria simulações com um simples POST request. Sem configurações complexas ou dependências pesadas.
                </Typography>
              </CardContent>
            </Card>

            <Card sx={{ height: '100%', '&:hover': { boxShadow: 6, transform: 'translateY(-4px)' }, transition: 'all 0.3s ease' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                  <PlayArrow sx={{ fontSize: 48, color: 'primary.main' }} />
                </Box>
                <Typography variant="h6" gutterBottom sx={{ textAlign: 'center', fontWeight: 600 }}>
                  Configuração JSON
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
                  Setup completo em minutos, não horas. Configura sensores, tópicos e dados com JSON simples.
                </Typography>
              </CardContent>
            </Card>

            <Card sx={{ height: '100%', '&:hover': { boxShadow: 6, transform: 'translateY(-4px)' }, transition: 'all 0.3s ease' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                  <Security sx={{ fontSize: 48, color: 'primary.main' }} />
                </Box>
                <Typography variant="h6" gutterBottom sx={{ textAlign: 'center', fontWeight: 600 }}>
                  Isolamento Kubernetes
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
                  Cada simulação corre isolada e segura em pods Kubernetes. Totalmente isolada de outras simulações.
                </Typography>
              </CardContent>
            </Card>

            <Card sx={{ height: '100%', '&:hover': { boxShadow: 6, transform: 'translateY(-4px)' }, transition: 'all 0.3s ease' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                  <Autorenew sx={{ fontSize: 48, color: 'primary.main' }} />
                </Box>
                <Typography variant="h6" gutterBottom sx={{ textAlign: 'center', fontWeight: 600 }}>
                  Auto-cleanup
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
                  Sem custos ocultos. As simulações expiram automaticamente após a duração configurada.
                </Typography>
              </CardContent>
            </Card>
          </Box>
        </Container>
      </Box>

      {/* How It Works Section */}
      <Box sx={{ py: { xs: 6, md: 10 }, bgcolor: '#f5f5f5' }}>
        <Container maxWidth="lg">
          <Typography
            variant="h2"
            component="h2"
            sx={{
              textAlign: 'center',
              mb: 6,
              fontSize: { xs: '2rem', md: '2.5rem' },
              fontWeight: 600
            }}
          >
            Como Funciona
          </Typography>
          <Box sx={{ maxWidth: '700px', mx: 'auto' }}>
            <Stepper orientation="vertical" sx={{ '& .MuiStepLabel-root': { py: 2 } }}>
              <Step active={true}>
                <StepLabel>
                  <Typography variant="h6" gutterBottom>
                    Configura Sensores em JSON
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Define tipos de sensores, valores mínimos/máximos, intervalos e padrões de dados num ficheiro JSON simples.
                  </Typography>
                </StepLabel>
              </Step>
              <Step active={true}>
                <StepLabel>
                  <Typography variant="h6" gutterBottom>
                    POST para /simulations
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Envia a configuração via API REST. A plataforma cria automaticamente um pod Kubernetes com o simulador.
                  </Typography>
                </StepLabel>
              </Step>
              <Step active={true}>
                <StepLabel>
                  <Typography variant="h6" gutterBottom>
                    Recebe Dados MQTT em Tempo Real
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Conecta a tua aplicação ao broker MQTT e começa a receber dados sintéticos realistas instantaneamente.
                  </Typography>
                </StepLabel>
              </Step>
              <Step active={true}>
                <StepLabel>
                  <Typography variant="h6" gutterBottom>
                    Limpeza Automática
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    A simulação para e é removida automaticamente após a duração configurada. Sem intervenção necessária.
                  </Typography>
                </StepLabel>
              </Step>
            </Stepper>
          </Box>
          <Box sx={{ textAlign: 'center', mt: 6 }}>
            <Button
              variant="contained"
              size="large"
              onClick={onTryItClick}
              sx={{
                px: 4,
                py: 1.5,
                fontSize: '1.125rem'
              }}
            >
              Começar Agora
            </Button>
          </Box>
        </Container>
      </Box>
    </>
  );
}

