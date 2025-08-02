# AgentCodeV1

AgentCodeV1 is a browser-based Python IDE built using React, Monaco Editor, and Pyodide. It allows users to write and run Python code directly in the browser without needing any server or backend.

## Features

- Monaco Editor with Python syntax highlighting
- Run button to execute Python code using Pyodide
- Output console to show printed output or errors
- Toolbar with Run, Debug, Test, and Explain buttons (placeholders)
- Split-screen layout: editor on the left, output on the right

## Folder Structure

```plaintext
AgentCodeV1/
├── public/
├── src/
│   ├── components/
│   │   ├── CodeEditor.jsx
│   │   ├── OutputPane.jsx
│   │   └── Toolbar.jsx
│   ├── utils/
│   │   └── pyodideRunner.js
│   ├── App.jsx
│   └── main.jsx
├── package.json
├── vite.config.js
└── README.md
```

## Getting Started

### Requirements

- Node.js installed
- Git installed

### Setup Instructions

1. Clone the repository:

git clone https://github.com/samkitpalrecha/AgentCodeV1.git
cd AgentCodeV1

2. Install dependencies:
npm install

3. Run the app:
npm run dev

4. Open the app in a browser at:
http://localhost:5173


## How It Works

The editor is implemented using Monaco Editor. When the "Run" button is clicked, the code is executed using Pyodide (a WebAssembly-based Python runtime), and the result is shown in the output pane. Output is captured using `setStdout` and `setStderr` hooks provided by Pyodide.

## Future Improvements

- Hook up Debug, Test, and Explain buttons with real logic
- Add keyboard shortcut to run code
- Optionally support saving and loading files
- Improve layout and theming
