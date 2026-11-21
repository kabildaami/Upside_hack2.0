import { useState } from 'react';

function App() {
  const [counter, setCounter] = useState(0);

  return (
    <div style={{
      padding: '40px',
      fontFamily: 'system-ui, sans-serif',
      background: 'linear-gradient(135deg, #f7f8fc 0%, #f0edff 100%)',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      <div style={{
        background: 'white',
        padding: '40px',
        borderRadius: '20px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
        textAlign: 'center',
        maxWidth: '500px',
      }}>
        <h1 style={{ color: '#7659e8', marginTop: 0 }}>✨ BrightPath</h1>
        <p style={{ color: '#666', fontSize: '18px' }}>Your learning adventure awaits!</p>
        
        <div style={{
          background: '#f7f8fc',
          padding: '20px',
          borderRadius: '12px',
          marginY: '20px',
        }}>
          <p style={{ color: '#24253c', fontSize: '16px' }}>
            React is working! Counter: <strong>{counter}</strong>
          </p>
          <button
            onClick={() => setCounter(c => c + 1)}
            style={{
              background: '#7659e8',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: 'pointer',
              marginRight: '10px',
            }}
          >
            Click me
          </button>
          <button
            onClick={() => setCounter(0)}
            style={{
              background: '#e8f7f1',
              color: '#2fa77a',
              border: '2px solid #2fa77a',
              padding: '12px 24px',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: 'pointer',
            }}
          >
            Reset
          </button>
        </div>

        <p style={{ color: '#898ba0', fontSize: '14px', marginBottom: 0 }}>
          Full dashboard coming next...
        </p>
      </div>
    </div>
  );
}

export default App;
