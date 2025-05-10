# AI Integration for Language Conversations

This document explains how to configure and use different AI providers for the language conversation module (`language_ai`).

## Configuration

The `language_ai` module allows you to use multiple AI providers to generate responses in conversations. By default, the system uses a simulator that provides predefined responses, but you can configure different providers based on your needs.

### Free and Paid Options

We offer several AI integration options:

1. **Simulator (free)** - Default mode, provides predefined responses for development and testing.
2. **Hugging Face (free with limits)** - Uses Hugging Face's Inference API with open models.
3. **Ollama (free, local)** - Fully local solution using Ollama to run models on your machine.
4. **OpenAI (paid)** - Uses OpenAI's API with GPT-3.5-Turbo or GPT-03.

## Configuration in Environment Files

To configure the AI provider, add the following variables to your `.env` file:

```
# Choose provider: 'simulator', 'huggingface', 'ollama', or 'openai'
AI_PROVIDER=simulator

# For OpenAI
OPENAI_API_KEY=your_openai_api_key

# For Hugging Face
HUGGINGFACE_API_TOKEN=your_huggingface_token
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2  # Example model

# For Ollama
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=mistral  # Or another locally installed model
```

## Installing Dependencies

Depending on the provider you want to use, install the necessary dependencies:

```bash
# For OpenAI
pip install openai

# For Hugging Face (already included via requests)
# No additional dependency needed

# For Ollama
# No additional Python dependency needed, but you must install Ollama locally
# See https://ollama.ai/download for installation instructions
```

With Poetry:

```bash
# For OpenAI
poetry add openai
```

## Usage Guide for Free Options

### Option 1: Hugging Face (Free)

Hugging Face offers a free inference API that allows you to use generative AI models.

1. Create an account on [Hugging Face](https://huggingface.co/signup)
2. Get an API token in your account settings: [Settings > Access Tokens](https://huggingface.co/settings/tokens)
3. Configure your `.env` file with the following variables:
   ```
   AI_PROVIDER=huggingface
   HUGGINGFACE_API_TOKEN=your_token_here
   HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2
   ```

Limitations of the free version:
- Limited number of requests per day
- Longer response time than paid services
- Possible service denial if excessive use

### Option 2: Ollama (100% Free and Local)

Ollama allows you to run AI models locally on your computer.

1. Download and install [Ollama](https://ollama.ai/download) for your operating system
2. Launch Ollama and download a model:
   ```bash
   ollama pull mistral
   ```
3. Configure your `.env` file:
   ```
   AI_PROVIDER=ollama
   OLLAMA_API_URL=http://localhost:11434
   OLLAMA_MODEL=mistral
   ```

Advantages:
- Completely free and unlimited
- 100% local data (no information is sent to external servers)
- No usage costs

Disadvantages:
- Requires a computer with good performance (GPU recommended)
- Potentially lower quality than cutting-edge models like GPT-4

## Usage Guide for the Paid Option (OpenAI)

To use OpenAI:

1. Create an account on [OpenAI](https://platform.openai.com/)
2. Get an API key in your settings
3. Add credit to your account (OpenAI offers $5 free to start)
4. Configure your `.env` file:
   ```
   AI_PROVIDER=openai
   OPENAI_API_KEY=your_api_key
   ```

## Fallback and Backup System

The system is configured to always fallback to the simulator in case of problems with the chosen AI provider. This ensures that the application continues to work even if the API is unavailable or credits are depleted.

## Development and Testing

For development and testing, it is recommended to use the simulator which requires no external configuration:

```
AI_PROVIDER=simulator
```

## Multilingual Support

All AI providers are configured to support conversations in different languages. The system will send instructions to the model to respond in the target language of the conversation.

## Maintenance and Updates

AI models and APIs evolve regularly. It is recommended to periodically check for updates to the libraries and models used.

With Ollama, update your local models regularly:

```bash
ollama pull mistral:latest
```