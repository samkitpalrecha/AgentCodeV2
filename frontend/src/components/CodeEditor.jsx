// CodeEditor.jsx
import React from 'react';
import Editor from '@monaco-editor/react';

export default function CodeEditor({ code, onChange }) {
  return (
    <div style={{ height: '100%' }}>
      <Editor
        height="100%"
        language="python"
        value={code}
        onChange={(value) => onChange(value || '')}
        options={{
          automaticLayout: true,
          minimap: { enabled: false },
        }}
      />
    </div>
  );
}
