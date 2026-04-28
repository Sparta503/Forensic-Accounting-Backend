# Forensic Accounting Backend (Executable)

## Requirements

- Windows 64-bit
- A `.env` file in this same `dist` folder

Your `.env` must include at least:

```env
MONGO_URI=...
DB_NAME=...
JWT_SECRET=...
```

## Run

### Option 1 (recommended)

Open PowerShell in this folder and run:

```powershell
.\forensic_backend.exe
```

### Option 2 (from the project root)

If you are in the project root (the folder that contains `dist/`), run:

```powershell
.\dist\forensic_backend.exe
```

## API Docs

Once the server starts, open:

- http://127.0.0.1:8000/docs

## Stop

Press `CTRL + C` in the console window.
