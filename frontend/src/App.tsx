import { useState } from 'react';
import LandingPage from './components/LandingPage';
import SimulatorManager from './components/SimulatorManager';

function App() {
  const [showManager, setShowManager] = useState(false);

  const handleTryItClick = () => {
    setShowManager(true); // Mostra o manager quando clicar "Try it"
  };

  const handleBackToHome = () => {
    setShowManager(false); // Volta para a landing page
  };

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