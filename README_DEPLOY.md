# APP_PALTAS_FLASK_PASOS_REALES_V5

Versión Flask con pasos visibles reales.

Verificación visual:
- Arriba aparece el indicador: Paso X de 4.
- Debajo aparece una barra con: 1. Pedido, 2. Entrega, 3. Contacto, 4. Confirmación.
- Abajo aparece: V5 · pasos reales.

## Probar localmente

```powershell
$env:GCP_SERVICE_ACCOUNT_JSON = Get-Content "C:\Users\arman\Downloads\inspired-cortex-493317-g1-6fff47b667cf.json" -Raw
cd "C:\Users\arman\Downloads\APP_PALTAS_FLASK_PASOS_REALES_V5\APP_PALTAS_FLASK_PASOS_REALES_V5"
python app.py
```

Abrir:

```text
http://127.0.0.1:5000
```
