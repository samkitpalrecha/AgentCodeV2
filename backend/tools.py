import os, re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from unidiff import PatchSet
from unidiff.errors import UnidiffParseError
import logging

logger = logging.getLogger(__name__)
load_dotenv()

# Initialize Gemini via LangChain integration
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # Use Gemini 2.5 model
    temperature=0.1,
    max_output_tokens=2048,
    convert_system_message_to_human=False  # Required for Gemini compatibility
)

def search_internal(query: str, code: str) -> str:
    """Search within current code using AST-aware patterns"""
    # Prioritize function/class definitions
    pattern_map = {
        r'def\s+\w+': 'Function definitions',
        r'class\s+\w+': 'Class definitions',
        r'\w+\s*=': 'Variable assignments',
        r'import\s+\w+': 'Import statements'
    }
    
    results = []
    for pattern, label in pattern_map.items():
        if re.search(pattern, code):
            results.append(f"{label} related to '{query}'")
    
    # Fallback to context lines
    if not results:
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if query.lower() in line.lower():
                context = '\n'.join(lines[max(0, i-2):min(len(lines), i+3)])
                results.append(f"Context around line {i+1}:\n{context}")
    
    return "\n\n".join(results) if results else "No relevant code found"

def search_external(query: str) -> str:
    """Search external docs (simplified)"""
    # Placeholder - integrate with real sources in production
    return f"External documentation regarding '{query}'"

def apply_diff(current_code: str, diff: str) -> str:
    """Apply unified diff to current code with improved error handling"""
    try:
        # Clean up the diff first
        diff_lines = diff.strip().split('\n')
        clean_diff = []
        
        for line in diff_lines:
            if line.startswith('---') or line.startswith('+++'):
                continue
            clean_diff.append(line)
        
        clean_diff_str = '\n'.join(clean_diff)
        
        # If it's a simple replacement, handle it directly
        if '@@ -' not in clean_diff_str:
            # This might be a direct code replacement
            return clean_diff_str
        
        # Try to parse as unified diff
        full_diff = f"--- original.py\n+++ modified.py\n{clean_diff_str}"
        logger.info(f"Applying diff: {full_diff}")
        
        patch = PatchSet.from_string(full_diff)
        if not patch or len(patch) == 0:
            raise ValueError("Empty diff")
            
        patched_file = patch[0]
        lines = current_code.split('\n')
        
        # Apply hunks in reverse order to avoid index issues
        for hunk in sorted(patched_file, key=lambda h: h.target_start, reverse=True):
            start = max(0, hunk.target_start - 1)  # Convert to 0-index and ensure non-negative
            
            # Collect additions and removals
            additions = []
            removals = []
            
            for line in hunk:
                if line.is_added:
                    additions.append(line.value.rstrip('\n'))
                elif line.is_removed:
                    removals.append(line.value.rstrip('\n'))
            
            # Apply removals first
            for removal in removals:
                for i in range(len(lines)):
                    if lines[i].strip() == removal.strip():
                        del lines[i]
                        break
            
            # Then apply additions at the calculated position
            if additions:
                for i, addition in enumerate(additions):
                    lines.insert(min(start + i, len(lines)), addition)
        
        result = '\n'.join(lines)
        logger.info(f"Diff applied successfully. Result length: {len(result)}")
        return result
    
    except Exception as e:
        logger.error(f"Diff application failed: {str(e)}")
        # Fallback: if diff application fails, try to extract and return the new code
        if '+' in diff:
            added_lines = [line[1:] for line in diff.split('\n') if line.startswith('+') and not line.startswith('+++')]
            if added_lines:
                return '\n'.join(added_lines)
        
        # Last resort: return the original code with a comment
        return current_code + f"\n# Error applying diff: {str(e)}"
        
def extract_diff(response: str) -> str:
    """Extract diff from LLM response using pattern matching"""
    patterns = [
        r"```diff\n(.*?)\n```",  # Standard diff block
        r"```\n(.*?)\n```",      # Generic code block
        r"--- original.py\n(.*?)(?=\n\n|\Z)",  # Raw diff start
        r"@@ -[\d,]+ \+[\d,]+ @@\n(.*?)(?=\n\n|\Z)"  # Unified diff hunk
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            extracted = match.group(1).strip()
            logger.info(f"Extracted diff using pattern: {extracted}")
            return extracted
    
    # If no patterns match but we see diff-like content, extract it
    if '@@' in response or ('+' in response and '-' in response):
        logger.info("Found diff-like content, returning cleaned response")
        return response.strip()
    
    # Fallback: Return the entire response if no pattern matches
    logger.warning("No diff pattern found, returning full response")
    return response