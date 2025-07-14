# JGxAAI Terminal

A terminal-style chat interface for Ollama models with hacker aesthetics.

## Framework & Technology

Built with **PySide6** (Qt for Python) providing:
- Native desktop integration across Linux, Windows, and macOS
- Hardware-accelerated rendering and smooth animations
- Professional UI components with extensive customization
- Efficient threading for non-blocking streaming responses

## Python Advantages

- **Rapid Development**: Fast prototyping and iteration cycles
- **Rich Ecosystem**: Extensive libraries for AI/ML integration
- **Cross-Platform**: Single codebase runs everywhere
- **Memory Management**: Automatic garbage collection
- **Readable Code**: Clean syntax for maintainable applications

## Requirements

- Python 3.6+
- Ollama running on localhost:11434

## Installation

```bash
git clone git@github.com:sirjoaogoncalves/JGxAAI.git 
cd JGxAAI
./install.sh
```

## Usage

```bash
./run.sh
```

## Features

- Terminal-style green-on-black interface
- Model selection from installed Ollama models
- Collapsible reasoning display for model thinking
- New chat functionality
- Supports both `<thinking>` and `<think>` tags
- Message bubbles sized to content

## Controls

- **[NEW CHAT]**: Clear conversation history
- **[SHOW REASONING]**: Toggle model reasoning display
- **Enter**: Send message
- **Model dropdown**: Select different Ollama models

## Future Development

**Go Rewrite Planned**: Next version will be implemented in Go for:
- **Performance**: Native compilation and faster execution
- **Memory Efficiency**: Lower resource usage and smaller binaries  
- **Static Binaries**: Single-file deployment without runtime dependencies
- **Concurrency**: Superior goroutine-based streaming and parallel processing
- **Distribution**: Simplified packaging and installation

## Troubleshooting

- Ensure Ollama is running: `ollama serve`
- Check Ollama models: `ollama list`
- Python virtual environment issues: Delete `venv` folder and re-run `./install.sh`
