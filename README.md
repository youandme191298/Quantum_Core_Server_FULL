# Quantum Core Server FULL (Render + Replit)
This package is a ready-to-deploy Quantum Core Server with 40 layer modules.

## Quick deploy (Render)
1. Create a GitHub repo and push the contents of this folder.
2. On Render.com -> New Web Service -> Connect repo -> Deploy.
3. Render will run `pip install -r requirements.txt` then `python quantum_core_server_pro.py`.
4. Visit `/layer_values` and `/total_energy` to inspect.

## Quick run (Replit)
1. Create a new Replit, upload files, press Run. Ensure packages installed in package manager.

## Notes
- To override a layer's behavior, create `core/layer_XX.py` with a `run_layer()` function (XX is 01..40).
- Call `/admin/reload_core` to reload overrides at runtime.
- SocketIO endpoint broadcasts `quantum_sync` events for dashboards that connect.
