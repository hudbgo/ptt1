# Pentest AI Assist (Desktop)

Aplicación de escritorio de **pentesting asistido por IA** con memoria persistente y flujo de aprobación humana para cualquier acción propuesta.

> ⚠️ Uso ético obligatorio: solo para activos autorizados. Esta demo **no ejecuta explotación automática**.

## Stack
- Backend: FastAPI + SQLAlchemy + SQLite
- IA: red neuronal simple con PyTorch para priorización de riesgo
- Frontend Desktop: React + Vite + Electron
- Persistencia: `SQLite` local (`pentest_ai.db`)

## Estructura

- `backend/app/main.py`: API principal
- `backend/app/ai_engine.py`: modelo neuronal y lógica de priorización
- `backend/app/scanner.py`: escaneo ligero de puertos comunes
- `desktop/src/App.jsx`: dashboard UI
- `desktop/electron/main.js`: shell de escritorio

## Requisitos
- Python 3.11+
- Node.js 20+
- npm

## Arranque rápido

1. Instala dependencias backend:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```
2. Instala dependencias frontend:
   ```bash
   cd desktop
   npm install
   cd ..
   npm install
   ```
3. Ejecuta todo con un comando:
   ```bash
   npm run run-all
   ```

Esto inicia:
- API en `http://127.0.0.1:8000`
- App desktop Electron con dashboard React

## Flujo funcional
1. Introduce IP o dominio autorizado.
2. La IA realiza escaneo básico + fingerprinting.
3. La red neuronal prioriza riesgo y genera propuestas.
4. El usuario aprueba/rechaza propuestas.
5. Las decisiones quedan persistidas en SQLite.

## Build de instalador Windows (.exe)

Desde la raíz del proyecto:
```bash
npm run build-installer
```

Se generará el instalador NSIS en:
- `desktop/release/`

## Endpoints API principales
- `POST /analyses`: crea análisis nuevo
- `GET /analyses`: historial de análisis
- `PATCH /proposals/{id}`: guardar aprobación/rechazo

## Notas de seguridad
- No hay ejecución automática de exploits.
- Todas las propuestas requieren decisión humana explícita.
- Recomendado añadir autenticación y sandboxing antes de uso productivo.
