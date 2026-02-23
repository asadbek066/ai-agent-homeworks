# Support Ticket Classifier

Auto-sorts customer support tickets using AI and routes them to the right team. Runs locally on your machine with Ollama.

## What It Does

- Reads tickets and figures out what they're about
- Routes them to the right support queue automatically
- Flags unclear ones for manual review
- Logs everything so you can see what happened
- Change categories and rules in a config file (no retraining)
- Can process hundreds of tickets at once

# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start the API
uvicorn app.main:app --reload --port 8000
```

## Test It

- **Dashboard**: http://localhost:8000/ (see all classifications)
- **Test form**: http://localhost:8000/test (try it yourself)

Or with PowerShell:
```powershell
$body = @{
  subject = 'Payment failed'
  description = 'Card declined'
  source_channel = 'email'
  customer_type = 'paid'
  language = 'en'
} | ConvertTo-Json
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/classify' -Method Post -ContentType 'application/json' -Body $body
```
