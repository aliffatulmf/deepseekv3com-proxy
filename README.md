# DeepSeek Chat Proxy

A Flask-based API proxy that provides OpenAI-compatible interface for DeepSeek chat services with rate limiting, CORS support, and logging system.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/deepseek-chat-proxy.git
   cd deepseek-chat-proxy
   ```

2. Install dependencies:

   ```bash
   uv pip install .
   ```

## Usage

### Running the Server

Start the server using:

```bash
python deepseekv3.py
```

The server will run on `http://127.0.0.1:5000` by default.

### API Endpoints

#### Chat Completions

- **POST** `/v1/chat/completions`

  ```json
  {
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "model": "deepseek-chat",
    "stream": false
  }
  ```

#### Available Models

- **GET** `/v1/models`

  ```json
  {
    "object": "list",
    "data": [
      {
        "id": "deepseek-chat",
        "object": "model",
        "created": 1735693261,
        "owned_by": "deepseek"
      },
      {
        "id": "deepseek-coder",
        "object": "model",
        "created": 1735693262,
        "owned_by": "deepseek"
      }
    ]
  }
  ```

## Configuration

The server configuration is defined in `deepseekv3.py`:

```python
HOST = "127.0.0.1"
PORT = 5000
DEBUG = True
```

You can modify these values directly in the code or add environment variable support as needed.

## Dependencies

Main dependencies:

- Flask
- Flask-CORS
- httpx
- nodriver
- openai

## License

This project is MIT licensed. See the LICENSE file for details.
