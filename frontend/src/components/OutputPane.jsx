// OutputPane.jsx
import React from 'react';

export default function OutputPane({ output }) {
  return (
    <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
      {output}
    </pre>
  );
}
