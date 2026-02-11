# Pentest AI Assist (Desktop)

Aplicación de escritorio de **pentesting asistido por IA** con memoria persistente, aprobación humana obligatoria y ejecución controlada de acciones seguras.

> ⚠️ Uso ético obligatorio: solo para activos autorizados. Esta demo **no ejecuta explotación automática**.

## Principio de seguridad clave

- **IA (análisis)**: detecta, prioriza y propone.
- **Execution Engine (ejecución)**: módulo separado que solo ejecuta acciones permitidas y seguras.
- **Humano**: debe aprobar explícitamente antes de cualquier ejecución.

Esta separación evita que la IA invoque herramientas ofensivas directamente.

## Stack
- Backend: FastAPI + SQLAlchemy + SQLite
- IA: red neuronal simple con PyTorch para priorización de riesgo
- Motor de ejecución: `backend/app/execution_engine.py` (allowlist + validación + timeout + logs)
- Frontend Desktop: React + Vite + Electron
- Persistencia: `SQLite` local (`pentest_ai.db`)

## Estructura
- `backend/app/main.py`: API principal
- `backend/app/ai_engine.py`: modelo neuronal y lógica de priorización (solo propuesta)
- `backend/app/execution_engine.py`: ejecución controlada (sin IA)
- `backend/app/scanner.py`: escaneo ligero de puertos comunes
- `desktop/src/App.jsx`: dashboard UI
- `desktop/electron/main.js`: shell de escritorio

## Arranque rápido
1. Instala backend:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```
2. Instala frontend:
   ```bash
   cd desktop && npm install && cd .. && npm install
   ```
3. Ejecuta todo:
   ```bash
   npm run run-all
   ```

## Flujo de explotación controlada
1. El usuario analiza un objetivo.
2. La IA genera propuestas con `action_key` y parámetros.
3. El usuario aprueba/rechaza (se guarda `approved_by`).
4. Solo propuestas aprobadas muestran botón **Ejecutar**.
5. `POST /execute` valida aprobación + allowlist + parámetros y ejecuta.
6. Resultado y logs se guardan en DB + `execution_engine.log`.

## Acciones permitidas (allowlist)
- `dns_resolve`
- `tcp_connectivity_check`
- `http_head_check`

Para ampliar acciones seguras:
1. Añadir acción en `ALLOWED_ACTIONS`.
2. Implementar validación estricta en `validate_action`.
3. Implementar ejecución read-only y timeout.
4. Mantener trazabilidad (DB + log).

## Testing
```bash
pytest backend/tests -q
```
Incluye validación de:
- no ejecución sin aprobación
- ejecución con aprobación
- rechazo de parámetros inválidos
- creación de logs

## Build instalador Windows
```bash
npm run build-installer
```
Salida en `desktop/release/`.

## Notas de control de cambios
- Se prioriza la resolución de conflictos manteniendo el modelo de seguridad: IA propone, humano aprueba y el engine ejecuta solo acciones permitidas.

## Verificación de conflictos de merge
Antes de commitear, puedes validar que no quedaron marcadores `<<<<<<<`, `=======`, `>>>>>>>`:
```bash
npm run check-conflicts
```
