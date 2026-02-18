#!/usr/bin/env python3
"""Test script for Reportes endpoints - runs against local backend on port 8080."""
import requests
import sys

BASE = "http://localhost:8080"

def main():
    # 1. Login as admin
    r = requests.post(f"{BASE}/api/auth/login", data={"username": "david", "password": "Admin123!"})
    assert r.status_code == 200, f"Login failed: {r.text}"
    token = r.json()["access_token"]
    H = {"Authorization": f"Bearer {token}"}
    print(f"1. LOGIN OK - Token: {token[:20]}...")

    # Login as user juan.perez
    r2 = requests.post(f"{BASE}/api/auth/login", data={"username": "juan.perez", "password": "Temp123!"})
    token_user = r2.json()["access_token"]
    HU = {"Authorization": f"Bearer {token_user}"}

    # Login as user pedro.martinez
    r3 = requests.post(f"{BASE}/api/auth/login", data={"username": "pedro.martinez", "password": "Temp123!"})
    token_pedro = r3.json()["access_token"]
    HP = {"Authorization": f"Bearer {token_pedro}"}

    # === Create test data ===
    print("\n=== CREANDO DATOS DE PRUEBA ===")

    justificantes = [
        (HU, {"empleado_id": 1, "tipo": "Dia Economico", "fecha_inicio": "2026-02-10", "fecha_fin": "2026-02-10", "dias_solicitados": 1, "motivo": "Asunto personal"}),
        (HU, {"empleado_id": 1, "tipo": "Permiso por Horas", "fecha_inicio": "2026-02-12", "fecha_fin": "2026-02-12", "hora_inicio": "10:00", "hora_fin": "12:00", "motivo": "Cita medica"}),
        (HU, {"empleado_id": 1, "tipo": "ISSTEP", "fecha_inicio": "2026-02-05", "fecha_fin": "2026-02-07", "dias_solicitados": 3, "motivo": "Consulta medica"}),
        (HP, {"empleado_id": 3, "tipo": "Comision Todo el Dia", "fecha_inicio": "2026-02-14", "fecha_fin": "2026-02-14", "dias_solicitados": 1, "motivo": "Reunion SEP", "lugar": "Puebla"}),
    ]
    for headers, data in justificantes:
        r = requests.post(f"{BASE}/api/justificantes", json=data, headers=headers)
        status = "OK" if r.status_code in (200, 201) else f"FAIL({r.status_code})"
        print(f"  {status} Justificante: {data['tipo']}")
        if r.status_code not in (200, 201):
            print(f"       -> {r.text[:120]}")

    # Prestacion
    r = requests.post(f"{BASE}/api/prestaciones", json={
        "tipo": "Licencia Medica", "fecha_inicio": "2026-03-01", "fecha_fin": "2026-03-05", "motivo": "Cirugia programada"
    }, headers=HU)
    print(f"  {'OK' if r.status_code == 200 else 'FAIL(' + str(r.status_code) + ')'} Prestacion: Licencia Medica")
    if r.status_code != 200:
        print(f"       -> {r.text[:120]}")

    # Adeudos
    adeudos = [
        {"empleado_id": 1, "tipo": "Material", "descripcion": "Libro de texto no devuelto", "monto": 350.00},
        {"empleado_id": 3, "tipo": "Equipo", "descripcion": "Laptop con dano", "monto": 5000.00},
    ]
    for data in adeudos:
        r = requests.post(f"{BASE}/api/adeudos", json=data, headers=H)
        status = "OK" if r.status_code in (200, 201) else f"FAIL({r.status_code})"
        print(f"  {status} Adeudo: {data['tipo']} - ${data['monto']}")
        if r.status_code not in (200, 201):
            print(f"       -> {r.text[:120]}")

    # === TEST REPORTES ===
    print("\n" + "=" * 50)
    print("PRUEBAS DE REPORTES")
    print("=" * 50)

    params_periodo = {"fecha_inicio": "2026-01-01", "fecha_fin": "2026-12-31"}
    tests = [
        ("ausentismo", params_periodo),
        ("dias-economicos", {"anio": 2026}),
        ("permisos-horas", {"anio": 2026}),
        ("prestaciones", params_periodo),
        ("justificantes", params_periodo),
        ("adeudos", {}),
        ("extemporaneos", params_periodo),
        ("estadisticas-justificantes", params_periodo),
    ]

    results = []
    for endpoint, params in tests:
        r = requests.get(f"{BASE}/api/reportes/{endpoint}", params=params, headers=H)
        status = "OK" if r.status_code == 200 else f"FAIL({r.status_code})"
        data = r.json() if r.status_code == 200 else {}
        n = len(data.get("datos", []))

        extra = ""
        if "monto_total_pendiente" in data:
            extra = f" | Monto pendiente: ${data['monto_total_pendiente']:,.2f}"
        if "por_tipo" in data and data["por_tipo"]:
            extra = f" | Por tipo: {data['por_tipo']}"
        if "total_justificantes" in data:
            extra = f" | Total justificantes: {data['total_justificantes']}"
        if "total_empleados" in data:
            extra = f" | Empleados: {data['total_empleados']}"

        results.append((endpoint, status, n))
        print(f"  {status} {endpoint}: {n} registros{extra}")

    # === EXPORT EXCEL ===
    print("\n--- Export Excel ---")
    exports_ok = 0
    export_tests = [
        ("ausentismo", params_periodo),
        ("dias-economicos", {"anio": 2026}),
        ("adeudos", {}),
        ("justificantes", params_periodo),
    ]
    for rep, extra_params in export_tests:
        params = {"reporte": rep}
        params.update(extra_params)
        r = requests.get(f"{BASE}/api/reportes/export", params=params, headers=H)
        ct = r.headers.get("content-type", "")
        ok = "spreadsheet" in ct and r.status_code == 200
        if ok:
            exports_ok += 1
        print(f"  {'OK' if ok else 'FAIL'} {rep}.xlsx - {len(r.content)} bytes")

    # === AUTH TEST ===
    print("\n--- Auth (sin token debe dar 401) ---")
    r = requests.get(f"{BASE}/api/reportes/ausentismo", params=params_periodo)
    auth_ok = r.status_code == 401
    print(f"  {'OK' if auth_ok else 'FAIL'} Sin auth: HTTP {r.status_code}")

    # === RESUMEN ===
    print("\n" + "=" * 50)
    endpoints_ok = sum(1 for _, s, _ in results if s == "OK")
    total_tests = len(results) + len(export_tests) + 1  # endpoints + exports + auth
    passed = endpoints_ok + exports_ok + (1 if auth_ok else 0)
    print(f"RESULTADO: {passed}/{total_tests} pruebas pasaron")
    if passed == total_tests:
        print("TODOS LOS TESTS PASARON")
    else:
        print("ALGUNOS TESTS FALLARON")
    print("=" * 50)

    return 0 if passed == total_tests else 1

if __name__ == "__main__":
    sys.exit(main())
