export async function callAgent(code, instruction) {
  try {
    console.log("Sending to API:", { code, instruction }); // Debug log
    const res = await fetch('/api/agent', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ code, instruction })
    });
    
    if (!res.ok) {
      throw new Error(`API Error: ${res.status} ${res.statusText}`);
    }
    
    const data = await res.json();
    console.log("API Response:", data); // Debug log
    return data;
    
  } catch (error) {
    console.error("API Call Failed:", error);
    throw error;
  }
}