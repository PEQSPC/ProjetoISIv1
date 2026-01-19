import { useState } from 'react';
import { CircularProgress, Box } from '@mui/material';
import LandingPage from './components/LandingPage';
import SimulatorManager from './components/SimulatorManager';
import Login from './components/Login';
import { useAuth } from './contexts/AuthContext';

function App() {
  const { isAuthenticated, isLoading } = useAuth();
  const [showManager, setShowManager] = useState(false);

  const handleTryItClick = () => {
    setShowManager(true);
  };

  const handleBackToHome = () => {
    setShowManager(false);
  };

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  // Show login if not authenticated
  if (!isAuthenticated) {
    return <Login />;
  }

  // Show main app if authenticated
  return (
    <div style={{ minHeight: '100vh' }}>
      {!showManager ? (
        <LandingPage onTryItClick={handleTryItClick} />
      ) : (
        <SimulatorManager onBackToHome={handleBackToHome} />
      )}
    </div>
  );
}

export default App;
