import React, { useState } from 'react';
import { callAgent } from '../utils/agentClient';

export default function AgentPanel({ code, onExplain, loading: parentLoading }) {
  const [plan, setPlan] = useState([]);
  const [localLoading, setLocalLoading] = useState(false);
  
  // Use parent loading state if provided, otherwise use local loading
  const isLoading = parentLoading !== undefined ? parentLoading : localLoading;

  const handleExplain = async () => {
    // If parent handles loading, use the parent's onExplain
    if (onExplain) {
      onExplain();
      return;
    }
    
    // Otherwise handle it locally
    setLocalLoading(true);
    setPlan([]);
    
    try {
      const response = await callAgent(
        code, 
        'Explain this Python code and suggest improvements'
      );
      
      if (!response || !response.result) {
        throw new Error("Agent returned empty response");
      }
      
      // Note: We can't update code here without setCode prop
      console.log("Generated code:", response.result);
      
      if (response.plan && response.plan.length > 0) {
        setPlan(response.plan);
      } else {
        setPlan(["Agent completed successfully but didn't provide a plan"]);
      }
      
    } catch (error) {
      console.error("AI Assist failed:", error);
      setPlan([`Error: ${error.message}`]);
    } finally {
      setLocalLoading(false);
    }
  };

  return (
    <div className="agent-panel" style={{ 
      padding: '1rem',
      borderBottom: '1px solid #333',
      backgroundColor: '#1a1a1a',
      borderRadius: '8px',
      marginBottom: '1rem',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)'
    }}>
      <button 
        onClick={handleExplain} 
        disabled={isLoading}
        style={{
          padding: '0.75rem 1.5rem',
          background: isLoading ? '#555' : '#007acc',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: isLoading ? 'wait' : 'pointer',
          fontSize: '0.95rem',
          fontWeight: '500',
          transition: 'all 0.2s ease',
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
          ':hover': {
            background: isLoading ? '#555' : '#006bb3',
            transform: isLoading ? 'none' : 'translateY(-1px)'
          }
        }}
      >
        {isLoading ? (
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="spinner"></span>
            Processing...
          </span>
        ) : (
          'AI Explain & Improve'
        )}
      </button>
      
      <div style={{ 
        maxHeight: '200px', 
        overflowY: 'auto', 
        marginTop: '1rem',
        backgroundColor: '#252525',
        borderRadius: '6px',
        padding: '1rem',
        border: '1px solid #333'
      }}>
        {plan.length > 0 ? (
          <ul style={{ 
            listStyleType: 'none', 
            paddingLeft: '0',
            margin: 0,
            color: '#e0e0e0'
          }}>
            {plan.map((s, i) => (
              <li key={i} style={{ 
                padding: '0.75rem 0',
                fontSize: '0.9rem',
                borderBottom: i < plan.length - 1 ? '1px solid #383838' : 'none',
                display: 'flex',
                gap: '0.5rem'
              }}>
                <span style={{
                  color: '#007acc',
                  fontWeight: 'bold',
                  minWidth: '1.5rem'
                }}>{i + 1}.</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p style={{ 
            color: '#aaa', 
            fontStyle: 'italic',
            margin: 0,
            textAlign: 'center',
            padding: '0.5rem'
          }}>
            {isLoading ? 'Generating explanation...' : 'No steps generated yet'}
          </p>
        )}
      </div>

      {/* Add some CSS for the spinner */}
      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        .spinner {
          display: inline-block;
          width: 1rem;
          height: 1rem;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-radius: 50%;
          border-top-color: white;
          animation: spin 1s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}