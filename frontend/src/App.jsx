import React, { useState } from 'react';
import CodeEditor from './components/CodeEditor';
import Toolbar from './components/Toolbar';
import AgentPanel from './components/AgentPanel';
import OutputPane from './components/OutputPane';
import { runPython } from './utils/pyodideRunner';
import { callAgent } from './utils/agentClient';  // Import your existing client

export default function App() {
  const [code, setCode] = useState('# Write Python here');
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRun = async () => {
    setLoading(true);
    setOutput('Running…');
    try {
      // Use local execution first
      const result = await runPython(code);
      setOutput(result);
    } catch (err) {
      setOutput(err.toString());
    } finally {
      setLoading(false);
    }
  };

  const handleExplain = async () => {
    setLoading(true);
    setOutput('Generating explanation...');
    try {
      const { result, plan } = await callAgent(code, 'Explain and improve this code');
      setCode(result);
      setOutput(plan?.join('\n') || 'Explanation generated');
    } catch (err) {
      setOutput(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="app-container"
      style={{
        display: 'flex',
        height: '100vh',
        overflow: 'hidden',
        fontFamily: 'Segoe UI, Roboto, monospace'
      }}
    >
      {/* Left side: Toolbar + AgentPanel + Editor */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Toolbar onRun={handleRun} loading={loading} />
        
        {/* AgentPanel with loading state */}
        <div style={{ 
          height: '200px', 
          borderBottom: '1px solid #eee',
          padding: '0.5rem'
        }}>
          <AgentPanel 
            code={code} 
            setCode={setCode}  // Add this missing prop
            onExplain={handleExplain} 
            loading={loading} 
          />
        </div>
        
        {/* Code Editor */}
        <div style={{ 
          flex: 1, 
          backgroundColor: '#f8f8f8', 
          padding: '1rem',
          overflow: 'hidden'
        }}>
          <CodeEditor code={code} onChange={setCode} />
        </div>
      </div>

      {/* Right side: Output pane */}
      <div
        style={{
          width: '40%',
          minWidth: '300px',
          borderLeft: '1px solid #ccc',
          backgroundColor: '#1e1e1e',
          color: '#0f0',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <h3 style={{ 
          margin: '1rem', 
          color: '#fff',
          padding: '0.5rem',
          borderBottom: '1px solid #444'
        }}>
          Output
        </h3>
        <div
          style={{
            padding: '1rem',
            flex: 1,
            overflowY: 'auto',
            backgroundColor: '#000',
            fontFamily: 'monospace',
            fontSize: '0.95rem'
          }}
        >
          <OutputPane output={output} />
        </div>
      </div>
    </div>
  );
}