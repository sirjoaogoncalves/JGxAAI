import requests
import json

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_models(self):
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get('models', [])
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Ollama: {str(e)}")
    
    def chat_stream(self, model, messages):
        payload = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=True,
                timeout=30
            )
            response.raise_for_status()
            
            assistant_message = ""
            thinking_content = ""
            in_thinking = False
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'message' in data and 'content' in data['message']:
                            content = data['message']['content']
                            assistant_message += content
                            
                            # Parse thinking tags (both <thinking> and <think>)
                            remaining_content = content
                            while remaining_content:
                                thinking_start = None
                                thinking_end = None
                                thinking_tag = None
                                
                                # Check for both <thinking> and <think> tags
                                if not in_thinking:
                                    if '<thinking>' in remaining_content:
                                        thinking_start = remaining_content.find('<thinking>')
                                        thinking_tag = 'thinking'
                                    if '<think>' in remaining_content:
                                        think_start = remaining_content.find('<think>')
                                        if thinking_start is None or think_start < thinking_start:
                                            thinking_start = think_start
                                            thinking_tag = 'think'
                                
                                if in_thinking:
                                    if '</thinking>' in remaining_content:
                                        thinking_end = remaining_content.find('</thinking>')
                                        thinking_tag = 'thinking'
                                    if '</think>' in remaining_content:
                                        think_end = remaining_content.find('</think>')
                                        if thinking_end is None or think_end < thinking_end:
                                            thinking_end = think_end
                                            thinking_tag = 'think'
                                
                                if not in_thinking and thinking_start is not None:
                                    # Start of thinking section
                                    before_thinking = remaining_content[:thinking_start]
                                    if before_thinking:
                                        yield ('message', before_thinking)
                                    
                                    tag_length = len(f'<{thinking_tag}>')
                                    remaining_content = remaining_content[thinking_start + tag_length:]
                                    in_thinking = True
                                    
                                elif in_thinking and thinking_end is not None:
                                    # End of thinking section
                                    thinking_part = remaining_content[:thinking_end]
                                    thinking_content += thinking_part
                                    yield ('thinking', thinking_content)
                                    
                                    tag_length = len(f'</{thinking_tag}>')
                                    remaining_content = remaining_content[thinking_end + tag_length:]
                                    in_thinking = False
                                    thinking_content = ""
                                    
                                elif in_thinking:
                                    # Inside thinking section
                                    thinking_content += remaining_content
                                    remaining_content = ""
                                    
                                else:
                                    # Regular message content
                                    yield ('message', remaining_content)
                                    remaining_content = ""
                        
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
            
            if assistant_message:
                # Clean the message of thinking tags before storing
                clean_message = assistant_message
                import re
                clean_message = re.sub(r'<thinking>.*?</thinking>', '', clean_message, flags=re.DOTALL)
                clean_message = re.sub(r'<think>.*?</think>', '', clean_message, flags=re.DOTALL)
                messages.append({"role": "assistant", "content": clean_message})
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Chat request failed: {str(e)}")