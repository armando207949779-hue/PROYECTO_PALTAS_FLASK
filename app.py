# ============================================================
# 01_APP_SOLPED_PALTAS
# Solicitud Pedido Paltas
# Versión Flask Mobile Premium — Rediseño V7
# ============================================================

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import gspread
from flask import Flask, redirect, render_template_string, request, session, url_for
from google.oauth2.service_account import Credentials


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cambia-esta-clave-en-railway")


INDEX_TEMPLATE = r"""
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#2d1a0a">
  <title>Pedido de Paltas</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">

  <style>
    :root {
      --tierra:   #2d1a0a;
      --palta:    #3d5a1e;
      --palta-md: #4e7227;
      --palta-lt: #6b9c35;
      --crema:    #f5f0e8;
      --crema-md: #ece4d0;
      --crema-dk: #d9ccb0;
      --pulpa:    #c8b560;
      --pulpa-lt: #f0e8a0;
      --white:    #fffef8;
      --ink:      #1a1108;
      --muted:    #6b5f4a;
      --line:     #e0d8c4;

      --r-card:   20px;
      --r-btn:    14px;
      --r-input:  12px;
      --shadow-card: 0 2px 12px rgba(45,26,10,0.10), 0 1px 3px rgba(45,26,10,0.06);
      --shadow-btn:  0 4px 16px rgba(61,90,30,0.22);

      --ff-display: 'Syne', sans-serif;
      --ff-body:    'DM Sans', sans-serif;
    }

    *, *::before, *::after {
      box-sizing: border-box;
      -webkit-tap-highlight-color: transparent;
    }

    body {
      margin: 0;
      font-family: var(--ff-body);
      font-size: 15px;
      color: var(--ink);
      background-color: var(--crema);
      background-image:
        radial-gradient(ellipse 80% 40% at 50% -10%, rgba(107,156,53,0.18) 0%, transparent 70%),
        url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23a09060' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
      min-height: 100dvh;
    }

    button, input, select { font: inherit; }

    /* ── Layout ── */
    .shell {
      width: 100%;
      max-width: 520px;
      margin: 0 auto;
      padding: max(0px, env(safe-area-inset-top)) 16px calc(32px + env(safe-area-inset-bottom));
    }

    /* ── Header ── */
    .topbar {
      position: sticky;
      top: 0;
      z-index: 30;
      padding: 12px 0 8px;
      background: linear-gradient(to bottom, var(--crema) 70%, transparent);
    }

    .header-inner {
      display: flex;
      align-items: center;
      gap: 13px;
      padding: 12px 14px;
      background: var(--white);
      border: 1px solid var(--crema-dk);
      border-radius: var(--r-card);
      box-shadow: var(--shadow-card);
    }

    .logo-wrap {
      width: 52px;
      height: 52px;
      border-radius: 14px;
      background: linear-gradient(135deg, var(--crema-md), var(--pulpa-lt));
      border: 1px solid var(--crema-dk);
      display: grid;
      place-items: center;
      flex: 0 0 auto;
      overflow: hidden;
    }

    .logo-wrap img {
      width: 46px;
      height: 46px;
      object-fit: contain;
    }

    .header-text { flex: 1; min-width: 0; }

    .eyebrow {
      font-family: var(--ff-body);
      font-size: 10px;
      font-weight: 600;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--palta-md);
      margin-bottom: 1px;
    }

    .app-title {
      font-family: var(--ff-display);
      font-size: 18px;
      font-weight: 800;
      line-height: 1.1;
      color: var(--tierra);
      margin: 0;
      letter-spacing: -0.02em;
    }

    /* ── Progress ── */
    .progress-section {
      margin-top: 8px;
    }

    .progress-track {
      height: 4px;
      background: var(--crema-dk);
      border-radius: 999px;
      overflow: hidden;
      margin-bottom: 8px;
    }

    .progress-fill {
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--palta), var(--palta-lt));
      transition: width 0.4s cubic-bezier(.4,0,.2,1);
    }

    .stepper {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 5px;
    }

    .step-dot {
      display: flex;
      align-items: center;
      gap: 5px;
      font-size: 11px;
      font-weight: 600;
      color: var(--muted);
      padding: 5px 7px;
      border-radius: 8px;
      border: 1px solid transparent;
      white-space: nowrap;
      overflow: hidden;
    }

    .step-dot::before {
      content: '';
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--crema-dk);
      flex: 0 0 auto;
    }

    .step-dot.active {
      color: var(--tierra);
      background: var(--pulpa-lt);
      border-color: var(--pulpa);
      font-weight: 700;
    }

    .step-dot.active::before {
      background: var(--palta-md);
    }

    .step-dot.done {
      color: var(--palta);
    }

    .step-dot.done::before {
      background: var(--palta-lt);
    }

    /* ── Card principal ── */
    .card {
      margin-top: 12px;
      background: var(--white);
      border: 1px solid var(--line);
      border-radius: var(--r-card);
      padding: 22px 18px;
      box-shadow: var(--shadow-card);
    }

    /* ── Screen title ── */
    .screen-title {
      font-family: var(--ff-display);
      font-size: clamp(24px, 7vw, 32px);
      font-weight: 800;
      letter-spacing: -0.03em;
      line-height: 1.05;
      color: var(--tierra);
      margin: 0 0 6px;
    }

    .screen-sub {
      font-size: 13.5px;
      color: var(--muted);
      line-height: 1.4;
      margin: 0 0 20px;
    }

    /* ── Labels / inputs ── */
    .field-label {
      display: block;
      font-size: 12.5px;
      font-weight: 600;
      color: var(--tierra);
      letter-spacing: 0.02em;
      text-transform: uppercase;
      margin: 16px 0 6px;
    }

    input[type="text"],
    input[type="tel"],
    input[type="number"],
    select {
      width: 100%;
      min-height: 48px;
      border-radius: var(--r-input);
      border: 1.5px solid var(--crema-dk);
      background: var(--crema);
      color: var(--ink);
      padding: 11px 13px;
      outline: none;
      font-size: 15px;
      transition: border-color 0.15s, box-shadow 0.15s;
    }

    input:focus,
    select:focus {
      border-color: var(--palta-md);
      background: var(--white);
      box-shadow: 0 0 0 3px rgba(78,114,39,0.14);
    }

    /* ── Opciones radio ── */
    .radio-group {
      display: grid;
      gap: 8px;
      margin: 8px 0 4px;
    }

    .radio-grid-2 { grid-template-columns: 1fr 1fr; }

    .opt-card {
      position: relative;
      display: flex;
      align-items: center;
      gap: 10px;
      min-height: 52px;
      padding: 12px 13px;
      border: 1.5px solid var(--crema-dk);
      border-radius: var(--r-input);
      background: var(--crema);
      cursor: pointer;
      transition: border-color 0.15s, background 0.15s, box-shadow 0.15s;
    }

    .opt-card input[type="radio"] {
      position: absolute;
      opacity: 0;
      pointer-events: none;
      min-height: unset;
    }

    .opt-dot {
      width: 18px;
      height: 18px;
      border-radius: 50%;
      border: 2px solid var(--crema-dk);
      background: var(--white);
      display: grid;
      place-items: center;
      flex: 0 0 auto;
      transition: border-color 0.15s;
    }

    .opt-dot::after {
      content: '';
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: transparent;
      transition: background 0.15s;
    }

    .opt-card:has(input:checked) {
      border-color: var(--palta-md);
      background: var(--white);
      box-shadow: 0 0 0 3px rgba(78,114,39,0.10);
    }

    .opt-card:has(input:checked) .opt-dot {
      border-color: var(--palta-md);
    }

    .opt-card:has(input:checked) .opt-dot::after {
      background: var(--palta-md);
    }

    .opt-text { flex: 1; min-width: 0; }

    .opt-title {
      display: block;
      font-weight: 600;
      font-size: 14px;
      color: var(--ink);
      line-height: 1.2;
    }

    .opt-hint {
      display: block;
      font-size: 11.5px;
      color: var(--muted);
      margin-top: 1px;
      line-height: 1.3;
    }

    .price-badge {
      font-family: var(--ff-display);
      font-size: 15px;
      font-weight: 800;
      color: var(--palta);
      white-space: nowrap;
    }

    /* ── Total box ── */
    .total-box {
      margin: 20px 0 4px;
      padding: 18px 16px;
      background: var(--tierra);
      border-radius: var(--r-card);
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .total-icon {
      font-size: 28px;
      line-height: 1;
      flex: 0 0 auto;
    }

    .total-label-small {
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: rgba(255,255,255,0.55);
      margin-bottom: 2px;
    }

    .total-number {
      font-family: var(--ff-display);
      font-size: clamp(26px, 10vw, 38px);
      font-weight: 800;
      letter-spacing: -0.04em;
      color: var(--pulpa-lt);
      line-height: 1;
    }

    .total-sub {
      font-size: 11.5px;
      color: rgba(255,255,255,0.45);
      margin-top: 3px;
    }

    /* ── Infobox / summary ── */
    .infobox {
      background: var(--crema);
      border: 1px solid var(--line);
      border-radius: var(--r-input);
      padding: 13px 14px;
      margin: 12px 0;
      font-size: 13.5px;
      color: var(--muted);
      line-height: 1.4;
    }

    .sumbox {
      background: var(--crema);
      border: 1px solid var(--crema-dk);
      border-radius: var(--r-card);
      margin: 16px 0;
      overflow: hidden;
    }

    .sumbox-head {
      background: var(--tierra);
      color: rgba(255,255,255,0.85);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      padding: 8px 14px;
    }

    .sumrow {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 10px 14px;
      border-bottom: 1px solid var(--line);
      font-size: 13.5px;
    }

    .sumrow:last-child { border-bottom: 0; }

    .sum-key {
      color: var(--muted);
      font-weight: 500;
      flex: 0 0 auto;
    }

    .sum-val {
      color: var(--ink);
      font-weight: 600;
      text-align: right;
      word-break: break-word;
    }

    /* ── Botones ── */
    .btn-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-top: 20px;
    }

    .btn-row.single { grid-template-columns: 1fr; }

    .btn {
      width: 100%;
      min-height: 50px;
      border-radius: var(--r-btn);
      border: 1.5px solid var(--crema-dk);
      background: var(--crema);
      color: var(--tierra);
      font-family: var(--ff-body);
      font-weight: 600;
      font-size: 14.5px;
      cursor: pointer;
      text-decoration: none;
      display: grid;
      place-items: center;
      padding: 11px 16px;
      text-align: center;
      transition: background 0.12s, border-color 0.12s, transform 0.08s;
    }

    .btn:active { transform: scale(0.975); }

    .btn.primary {
      background: var(--palta);
      border-color: var(--palta);
      color: #fff;
      box-shadow: var(--shadow-btn);
      font-weight: 700;
    }

    .btn.primary:hover {
      background: var(--palta-md);
      border-color: var(--palta-md);
    }

    /* ── WhatsApp ── */
    .wa-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 9px;
      width: 100%;
      min-height: 52px;
      border-radius: var(--r-btn);
      background: #25d366;
      color: #fff !important;
      font-weight: 700;
      font-size: 15px;
      text-decoration: none !important;
      margin: 12px 0;
      box-shadow: 0 6px 20px rgba(37,211,102,0.28);
    }

    /* ── Alertas ── */
    .notice {
      border-radius: var(--r-input);
      padding: 11px 13px;
      margin: 10px 0;
      font-size: 13.5px;
      font-weight: 500;
      line-height: 1.4;
    }

    .notice.ok      { background: #e9f5e1; color: #2a5216; border: 1px solid #a8d580; }
    .notice.warn    { background: #fff3e0; color: #7a3d0a; border: 1px solid #f7c47a; }
    .notice.err     { background: #fdeaea; color: #8b1a1a; border: 1px solid #f3a8a8; }

    /* ── Checkbox ── */
    .check-row {
      display: flex;
      gap: 10px;
      align-items: flex-start;
      margin: 16px 0 4px;
      font-size: 13.5px;
      font-weight: 500;
      line-height: 1.35;
      color: var(--ink);
      padding: 12px 13px;
      border: 1.5px solid var(--crema-dk);
      border-radius: var(--r-input);
      background: var(--crema);
    }

    .check-row input[type="checkbox"] {
      width: 18px;
      height: 18px;
      min-height: unset;
      accent-color: var(--palta);
      margin-top: 1px;
      flex: 0 0 auto;
    }

    .hidden { display: none !important; }

    .footer {
      text-align: center;
      color: var(--crema-dk);
      font-size: 11px;
      margin-top: 20px;
      letter-spacing: 0.04em;
    }

    /* ── Responsive ── */
    @media (max-width: 400px) {
      .shell { padding-left: 11px; padding-right: 11px; }
      .card { padding: 18px 14px; }
      .btn-row { grid-template-columns: 1fr; }
      .radio-grid-2 { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
<div class="shell">

  <header class="topbar">
    <div class="header-inner">
      <div class="logo-wrap">
        <img src="{{ url_for('static', filename='LOGO-PALTA.png') }}" alt="Paltas" onerror="this.style.display='none'">
      </div>
      <div class="header-text">
        <div class="eyebrow">Pedido online</div>
        <h1 class="app-title">Paltas del campo</h1>
      </div>
    </div>

    {% set nombres = {1: "Pedido", 2: "Entrega", 3: "Contacto", 4: "Confirmación"} %}
    <div class="progress-section" style="margin-top:10px;">
      <div class="progress-track">
        <div class="progress-fill" style="width: {{ paso * 25 }}%;"></div>
      </div>
      <div class="stepper">
        {% for n in [1, 2, 3, 4] %}
          <div class="step-dot {% if n == paso %}active{% elif n < paso %}done{% endif %}">
            {{ nombres[n] }}
          </div>
        {% endfor %}
      </div>
    </div>
  </header>

  <div class="card">
    {% for error in errores %}
      <div class="notice err">{{ error }}</div>
    {% endfor %}

    {# ── RESULTADO ── #}
    {% if resultado %}
      {% if resultado.google_ok %}
        <div class="notice ok">✓ Pedido registrado y guardado.</div>
      {% else %}
        <div class="notice warn">
          Pedido guardado localmente. Google Sheets requiere revisión.<br>
          <small>{{ resultado.google_msg }}</small>
        </div>
      {% endif %}

      <div class="sumbox">
        <div class="sumbox-head">Registro</div>
        <div class="sumrow"><span class="sum-key">Folio</span><span class="sum-val">{{ resultado.folio }}</span></div>
        <div class="sumrow"><span class="sum-key">Total</span><span class="sum-val">{{ resultado.total }}</span></div>
      </div>

      <a class="wa-btn" href="{{ resultado.whatsapp_url }}" target="_blank">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.135.558 4.14 1.535 5.878L.057 23.882a.5.5 0 0 0 .614.612l6.088-1.455A11.934 11.934 0 0 0 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 21.818a9.818 9.818 0 0 1-5.002-1.37l-.358-.213-3.715.888.918-3.636-.233-.375A9.818 9.818 0 1 1 12 21.818z"/></svg>
        Enviar por WhatsApp
      </a>

      <form method="post" action="{{ url_for('nuevo') }}">
        <button class="btn primary" type="submit">Nuevo pedido</button>
      </form>

    {# ── PASO 1 ── #}
    {% elif paso == 1 %}
      <h2 class="screen-title">¿Qué paltas quieres?</h2>
      <p class="screen-sub">Elige el tipo y la cantidad. El total se actualiza solo.</p>

      <form method="post" action="{{ url_for('paso_1') }}">
        <span class="field-label">Variedad</span>
        <div class="radio-group radio-grid-2">
          {% for tipo, precio in precios.items() %}
            <label class="opt-card">
              <input type="radio" name="tipo_palta" value="{{ tipo }}" data-precio="{{ precio }}" {% if datos.tipo_palta == tipo %}checked{% endif %}>
              <span class="opt-dot"></span>
              <span class="opt-text">
                <span class="opt-title">{{ tipo }}</span>
                <span class="opt-hint">{{ formato_pesos(precio) }} / kg</span>
              </span>
            </label>
          {% endfor %}
        </div>

        <label class="field-label" for="kilos">Kilos</label>
        <input id="kilos" name="kilos" type="number" inputmode="decimal" min="1" step="0.5" value="{{ datos.kilos }}">

        <div class="total-box">
          <div class="total-icon">🥑</div>
          <div>
            <div class="total-label-small" id="precioKgLabel">{{ datos.tipo_palta }} · {{ formato_pesos(datos.precio_kg) }} / kg</div>
            <div class="total-number" id="totalVisual">{{ formato_pesos(datos.total_paltas) }}</div>
            <div class="total-sub">total por {{ datos.kilos }} kg</div>
          </div>
        </div>

        <div class="btn-row single">
          <button class="btn primary" type="submit">Continuar →</button>
        </div>
      </form>

    {# ── PASO 2 ── #}
    {% elif paso == 2 %}
      <h2 class="screen-title">¿Cómo lo recibés?</h2>
      <p class="screen-sub">Elige la modalidad de entrega.</p>

      <form method="post" action="{{ url_for('paso_2') }}">
        <div class="radio-group">
          {% for opcion in ["Retiro sin costo", "Despacho zona cercana", "Cotizar otra comuna o región"] %}
            <label class="opt-card">
              <input type="radio" name="modalidad_entrega" value="{{ opcion }}" {% if datos.modalidad_entrega == opcion %}checked{% endif %}>
              <span class="opt-dot"></span>
              <span class="opt-text">
                <span class="opt-title">{{ opcion }}</span>
                {% if opcion == "Retiro sin costo" %}
                  <span class="opt-hint">Sin costo — coordinas por WhatsApp</span>
                {% elif opcion == "Despacho zona cercana" %}
                  <span class="opt-hint">La Calera, Quillota, La Cruz, Hijuelas</span>
                {% else %}
                  <span class="opt-hint">Consultamos disponibilidad contigo</span>
                {% endif %}
              </span>
            </label>
          {% endfor %}
        </div>

        <div id="bloqueRetiro">
          <label class="field-label" for="comuna_retiro">Localidad de retiro</label>
          <select id="comuna_retiro" name="comuna_retiro">
            {% for c in localidades %}
              <option value="{{ c }}" {% if datos.comuna == c %}selected{% endif %}>{{ c }}</option>
            {% endfor %}
          </select>
          <div class="infobox">El punto exacto se confirma por WhatsApp al registrar el pedido.</div>
        </div>

        <div id="bloqueLocal" class="hidden">
          <label class="field-label" for="comuna_local">Comuna</label>
          <select id="comuna_local" name="comuna_local">
            {% for c in localidades %}
              <option value="{{ c }}" {% if datos.comuna == c %}selected{% endif %}>{{ c }}</option>
            {% endfor %}
          </select>
        </div>

        <div id="bloqueOtra" class="hidden">
          <label class="field-label" for="region">Región</label>
          <select id="region" name="region">
            {% for r in regiones_comunas.keys() %}
              <option value="{{ r }}" {% if datos.region == r %}selected{% endif %}>{{ r }}</option>
            {% endfor %}
          </select>
          <label class="field-label" for="comuna_otra">Comuna</label>
          <select id="comuna_otra" name="comuna_otra"></select>
        </div>

        <div id="bloqueDireccion" class="hidden">
          <div class="infobox">Ingresa la dirección para coordinar el despacho.</div>
          <label class="field-label" for="poblacion">Población / sector</label>
          <input id="poblacion" name="poblacion" value="{{ datos.poblacion }}" placeholder="Ej: Boco, Pocochay, Artificio">
          <label class="field-label" for="calle">Calle</label>
          <input id="calle" name="calle" value="{{ datos.calle }}" placeholder="Ej: Los Aromos">
          <label class="field-label" for="numero">Número</label>
          <input id="numero" name="numero" value="{{ datos.numero }}" placeholder="Ej: 123">
        </div>

        <div class="btn-row">
          <button class="btn" type="submit" formaction="{{ url_for('volver', paso=1) }}">← Volver</button>
          <button class="btn primary" type="submit">Continuar →</button>
        </div>
      </form>

    {# ── PASO 3 ── #}
    {% elif paso == 3 %}
      <h2 class="screen-title">Tus datos</h2>
      <p class="screen-sub">Para confirmar el pedido y coordinar la entrega.</p>

      <form method="post" action="{{ url_for('paso_3') }}">
        <label class="field-label" for="nombre">Nombre</label>
        <input id="nombre" name="nombre" value="{{ datos.nombre }}" placeholder="Tu nombre completo" autocomplete="name">

        <label class="field-label" for="whatsapp">WhatsApp</label>
        <input id="whatsapp" name="whatsapp" value="{{ datos.whatsapp }}" placeholder="+56 9 1234 5678" inputmode="tel" autocomplete="tel">

        <div class="sumbox" style="margin-top:20px;">
          <div class="sumbox-head">Resumen del pedido</div>
          <div class="sumrow"><span class="sum-key">Palta</span><span class="sum-val">{{ datos.kilos }} kg · {{ datos.tipo_palta }}</span></div>
          <div class="sumrow"><span class="sum-key">Total</span><span class="sum-val">{{ formato_pesos(datos.total_paltas) }}</span></div>
          <div class="sumrow"><span class="sum-key">Entrega</span><span class="sum-val">{{ datos.modalidad_entrega }}</span></div>
        </div>

        <div class="btn-row">
          <button class="btn" type="submit" formaction="{{ url_for('volver', paso=2) }}">← Volver</button>
          <button class="btn primary" type="submit">Ver resumen →</button>
        </div>
      </form>

    {# ── PASO 4 ── #}
    {% elif paso == 4 %}
      <h2 class="screen-title">Revisa y confirma</h2>
      <p class="screen-sub">Verifica que todo esté bien antes de registrar.</p>

      {% if datos.modalidad_entrega == "Retiro sin costo" %}
        {% set direccion = "Retiro en " ~ datos.comuna %}
      {% else %}
        {% set direccion = [datos.poblacion, datos.calle, datos.numero] | select | join(", ") %}
      {% endif %}

      <div class="total-box" style="margin-bottom:16px;">
        <div class="total-icon">🥑</div>
        <div>
          <div class="total-label-small">Total paltas</div>
          <div class="total-number">{{ formato_pesos(datos.total_paltas) }}</div>
          <div class="total-sub">{{ datos.kilos }} kg · {{ datos.tipo_palta }}</div>
        </div>
      </div>

      <div class="sumbox">
        <div class="sumbox-head">Pedido y entrega</div>
        <div class="sumrow"><span class="sum-key">Precio / kg</span><span class="sum-val">{{ formato_pesos(datos.precio_kg) }}</span></div>
        <div class="sumrow"><span class="sum-key">Entrega</span><span class="sum-val">{{ datos.modalidad_entrega }}</span></div>
        <div class="sumrow"><span class="sum-key">Comuna</span><span class="sum-val">{{ datos.comuna }}</span></div>
        <div class="sumrow"><span class="sum-key">Dirección</span><span class="sum-val">{{ direccion or "Por coordinar" }}</span></div>
        <div class="sumrow"><span class="sum-key">Nombre</span><span class="sum-val">{{ datos.nombre }}</span></div>
        <div class="sumrow"><span class="sum-key">WhatsApp</span><span class="sum-val">{{ datos.whatsapp }}</span></div>
      </div>

      <div class="sumbox">
        <div class="sumbox-head">Datos para transferencia</div>
        <div class="sumrow"><span class="sum-key">Titular</span><span class="sum-val">{{ titular }}</span></div>
        <div class="sumrow"><span class="sum-key">RUT</span><span class="sum-val">{{ rut }}</span></div>
        <div class="sumrow"><span class="sum-key">Banco</span><span class="sum-val">{{ banco }}</span></div>
        <div class="sumrow"><span class="sum-key">Cuenta</span><span class="sum-val">{{ tipo_cuenta }}</span></div>
        <div class="sumrow"><span class="sum-key">Monto</span><span class="sum-val">{{ formato_pesos(datos.total_paltas) }}</span></div>
      </div>

      <form method="post" action="{{ url_for('registrar') }}">
        <label class="check-row">
          <input type="checkbox" name="confirmar" value="si">
          <span>Confirmo que los datos son correctos.</span>
        </label>
        <div class="btn-row">
          <button class="btn" type="submit" formaction="{{ url_for('volver', paso=3) }}">← Volver</button>
          <button class="btn primary" type="submit">Registrar pedido</button>
        </div>
      </form>
    {% endif %}
  </div>

  <div class="footer">{{ app_version or "01_APP_SOLPED_PALTAS · V7" }}</div>
</div>

<script>
  const regionesComunas = {{ regiones_comunas | tojson }};

  const fmt = v => "$" + Math.round(Number(v || 0)).toLocaleString("es-CL");

  const kilosInput   = document.querySelector("#kilos");
  const totalNum     = document.querySelector("#totalVisual");
  const totalSub     = totalNum?.closest(".total-box")?.querySelector(".total-sub");
  const precioLabel  = document.querySelector("#precioKgLabel");
  const tipoRadios   = document.querySelectorAll("input[name='tipo_palta']");

  function actualizarTotal() {
    if (!kilosInput || !totalNum) return;
    const sel    = document.querySelector("input[name='tipo_palta']:checked");
    const tipo   = sel?.value || "Hass";
    const precio = Number(sel?.dataset.precio || 0);
    const kilos  = Number(kilosInput.value || 0);
    totalNum.textContent = fmt(precio * kilos);
    if (precioLabel) precioLabel.textContent = `${tipo} · ${fmt(precio)} / kg`;
    if (totalSub)    totalSub.textContent    = `total por ${kilos} kg`;
  }

  tipoRadios.forEach(r => r.addEventListener("change", actualizarTotal));
  kilosInput?.addEventListener("input", actualizarTotal);
  actualizarTotal();

  // Modalidad entrega
  const bloqueRetiro    = document.querySelector("#bloqueRetiro");
  const bloqueLocal     = document.querySelector("#bloqueLocal");
  const bloqueOtra      = document.querySelector("#bloqueOtra");
  const bloqueDireccion = document.querySelector("#bloqueDireccion");
  const regionSelect    = document.querySelector("#region");
  const comunaOtra      = document.querySelector("#comuna_otra");

  function modalidad() {
    return document.querySelector("input[name='modalidad_entrega']:checked")?.value || "Retiro sin costo";
  }

  function actualizarModalidad() {
    const m = modalidad();
    bloqueRetiro?.classList.toggle("hidden", m !== "Retiro sin costo");
    bloqueLocal?.classList.toggle("hidden",  m !== "Despacho zona cercana");
    bloqueOtra?.classList.toggle("hidden",   m !== "Cotizar otra comuna o región");
    bloqueDireccion?.classList.toggle("hidden", m === "Retiro sin costo");
  }

  function cargarComunas() {
    if (!regionSelect || !comunaOtra) return;
    const comunas = regionesComunas[regionSelect.value] || [];
    const actual  = "{{ datos.comuna }}";
    comunaOtra.innerHTML = "";
    comunas.forEach(c => {
      const o = document.createElement("option");
      o.value = o.textContent = c;
      if (c === actual) o.selected = true;
      comunaOtra.appendChild(o);
    });
  }

  document.querySelectorAll("input[name='modalidad_entrega']")
    .forEach(r => r.addEventListener("change", actualizarModalidad));
  regionSelect?.addEventListener("change", cargarComunas);

  cargarComunas();
  actualizarModalidad();
</script>
</body>
</html>
"""


# ============================================================
# CONFIGURACIÓN DEL NEGOCIO
# ============================================================

PRECIOS_PALTA = {
    "Hass": 2500,
    "Fuerte": 2500,
}

KILOS_MINIMOS = 1.0

TITULAR = "Enrique Armando Brun Urrutia"
RUT = "20.794.977-9"
BANCO = "Banco Estado"
TIPO_CUENTA = "Cuenta RUT"

WHATSAPP_NEGOCIO = "56963596523"

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1o1zvFzeOsGkDdLQbvEBvMyK6avLiMVMj04Ic0J2bzSw/edit?usp=sharing"
GOOGLE_SHEET_NAME = "Pedidos"

ARCHIVO_RESPALDO = Path("ordenes_paltas.csv")
LOCALIDADES_CERCANAS = ["La Calera", "Quillota", "La Cruz", "Hijuelas"]


REGIONES_COMUNAS = {
    "Arica y Parinacota": ["Arica", "Camarones", "General Lagos", "Putre"],
    "Tarapacá": ["Alto Hospicio", "Camiña", "Colchane", "Huara", "Iquique", "Pica", "Pozo Almonte"],
    "Antofagasta": ["Antofagasta", "Calama", "María Elena", "Mejillones", "Ollagüe", "San Pedro de Atacama", "Sierra Gorda", "Taltal", "Tocopilla"],
    "Atacama": ["Alto del Carmen", "Caldera", "Chañaral", "Copiapó", "Diego de Almagro", "Freirina", "Huasco", "Tierra Amarilla", "Vallenar"],
    "Coquimbo": ["Andacollo", "Canela", "Combarbalá", "Coquimbo", "Illapel", "La Higuera", "La Serena", "Los Vilos", "Monte Patria", "Ovalle", "Paihuano", "Punitaqui", "Río Hurtado", "Salamanca", "Vicuña"],
    "Valparaíso": ["Algarrobo", "Cabildo", "Calle Larga", "Cartagena", "Casablanca", "Catemu", "Concón", "El Quisco", "El Tabo", "Hijuelas", "Isla de Pascua", "Juan Fernández", "La Calera", "La Cruz", "La Ligua", "Limache", "Llaillay", "Los Andes", "Nogales", "Olmué", "Panquehue", "Papudo", "Petorca", "Puchuncaví", "Putaendo", "Quillota", "Quilpué", "Quintero", "Rinconada", "San Antonio", "San Esteban", "San Felipe", "Santa María", "Santo Domingo", "Valparaíso", "Villa Alemana", "Viña del Mar", "Zapallar"],
    "Metropolitana de Santiago": ["Alhué", "Buin", "Calera de Tango", "Cerrillos", "Cerro Navia", "Colina", "Conchalí", "Curacaví", "El Bosque", "El Monte", "Estación Central", "Huechuraba", "Independencia", "Isla de Maipo", "La Cisterna", "La Florida", "La Granja", "La Pintana", "La Reina", "Lampa", "Las Condes", "Lo Barnechea", "Lo Espejo", "Lo Prado", "Macul", "Maipú", "María Pinto", "Melipilla", "Ñuñoa", "Padre Hurtado", "Paine", "Pedro Aguirre Cerda", "Peñaflor", "Peñalolén", "Pirque", "Providencia", "Pudahuel", "Puente Alto", "Quilicura", "Quinta Normal", "Recoleta", "Renca", "San Bernardo", "San Joaquín", "San José de Maipo", "San Miguel", "San Pedro", "San Ramón", "Santiago", "Talagante", "Tiltil", "Vitacura"],
    "O'Higgins": ["Chépica", "Codegua", "Coinco", "Coltauco", "Doñihue", "Graneros", "La Estrella", "Las Cabras", "Litueche", "Lolol", "Machalí", "Malloa", "Marchihue", "Mostazal", "Nancagua", "Navidad", "Olivar", "Palmilla", "Paredones", "Peralillo", "Peumo", "Pichidegua", "Pichilemu", "Placilla", "Pumanque", "Quinta de Tilcoco", "Rancagua", "Rengo", "Requínoa", "San Fernando", "San Vicente", "Santa Cruz"],
    "Maule": ["Cauquenes", "Chanco", "Colbún", "Constitución", "Curepto", "Curicó", "Empedrado", "Hualañé", "Licantén", "Linares", "Longaví", "Maule", "Molina", "Parral", "Pelarco", "Pelluhue", "Pencahue", "Rauco", "Retiro", "Río Claro", "Romeral", "Sagrada Familia", "San Clemente", "San Javier", "San Rafael", "Talca", "Teno", "Vichuquén", "Villa Alegre", "Yerbas Buenas"],
    "Ñuble": ["Bulnes", "Chillán", "Chillán Viejo", "Cobquecura", "Coelemu", "Coihueco", "El Carmen", "Ninhue", "Ñiquén", "Pemuco", "Pinto", "Portezuelo", "Quillón", "Quirihue", "Ránquil", "San Carlos", "San Fabián", "San Ignacio", "San Nicolás", "Treguaco", "Yungay"],
    "Biobío": ["Alto Biobío", "Antuco", "Arauco", "Cabrero", "Cañete", "Chiguayante", "Concepción", "Contulmo", "Coronel", "Curanilahue", "Florida", "Hualpén", "Hualqui", "Laja", "Lebu", "Los Álamos", "Los Ángeles", "Lota", "Mulchén", "Nacimiento", "Negrete", "Penco", "Quilaco", "Quilleco", "San Pedro de la Paz", "San Rosendo", "Santa Bárbara", "Santa Juana", "Talcahuano", "Tirúa", "Tomé", "Tucapel", "Yumbel"],
    "La Araucanía": ["Angol", "Carahue", "Cholchol", "Collipulli", "Cunco", "Curacautín", "Curarrehue", "Ercilla", "Freire", "Galvarino", "Gorbea", "Lautaro", "Loncoche", "Lonquimay", "Los Sauces", "Lumaco", "Melipeuco", "Nueva Imperial", "Padre Las Casas", "Perquenco", "Pitrufquén", "Pucón", "Purén", "Renaico", "Saavedra", "Temuco", "Teodoro Schmidt", "Toltén", "Traiguén", "Victoria", "Vilcún", "Villarrica"],
    "Los Ríos": ["Corral", "Futrono", "La Unión", "Lago Ranco", "Lanco", "Los Lagos", "Máfil", "Mariquina", "Paillaco", "Panguipulli", "Río Bueno", "Valdivia"],
    "Los Lagos": ["Ancud", "Calbuco", "Castro", "Chaitén", "Chonchi", "Cochamó", "Curaco de Vélez", "Dalcahue", "Fresia", "Frutillar", "Futaleufú", "Hualaihué", "Llanquihue", "Los Muermos", "Maullín", "Osorno", "Palena", "Puerto Montt", "Puerto Octay", "Puerto Varas", "Puqueldón", "Purranque", "Puyehue", "Queilén", "Quellón", "Quemchi", "Quinchao", "Río Negro", "San Juan de la Costa", "San Pablo"],
    "Aysén": ["Aysén", "Chile Chico", "Cisnes", "Cochrane", "Coyhaique", "Guaitecas", "Lago Verde", "O'Higgins", "Río Ibáñez", "Tortel"],
    "Magallanes": ["Antártica", "Cabo de Hornos", "Laguna Blanca", "Natales", "Porvenir", "Primavera", "Punta Arenas", "Río Verde", "San Gregorio", "Timaukel", "Torres del Paine"],
}


# ============================================================
# UTILIDADES  (idénticas a V6)
# ============================================================

def formato_pesos(valor) -> str:
    try:
        numero = int(round(float(valor)))
    except Exception:
        numero = 0
    return "$" + f"{numero:,}".replace(",", ".")


def calcular_total(tipo_palta: str, kilos: float) -> int:
    return int(round(PRECIOS_PALTA[tipo_palta] * kilos))


def normalizar_whatsapp(numero: str) -> str:
    return "".join(c for c in numero if c.isdigit())


def columnas_internas() -> list[str]:
    return [
        "folio", "fecha_registro", "tipo_palta", "kilos", "precio_por_kg",
        "total_paltas", "modalidad_entrega", "region", "comuna", "poblacion",
        "calle", "numero", "nombre", "whatsapp", "estado",
    ]


def encabezados_google_sheets() -> list[str]:
    return [
        "Folio", "Fecha registro", "Tipo de palta", "Kilos", "Precio por kg",
        "Total paltas", "Modalidad de entrega", "Región", "Comuna",
        "Población / sector", "Calle", "Número", "Nombre cliente",
        "WhatsApp cliente", "Estado",
    ]


def obtener_service_account_info() -> dict:
    contenido = os.getenv("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not contenido:
        raise RuntimeError("Falta la variable de entorno GCP_SERVICE_ACCOUNT_JSON.")
    return json.loads(contenido)


def obtener_worksheet_google_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_info(obtener_service_account_info(), scopes=scopes)
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_url(GOOGLE_SHEET_URL)
    try:
        worksheet = spreadsheet.worksheet(GOOGLE_SHEET_NAME)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=GOOGLE_SHEET_NAME,
            rows=1000,
            cols=len(encabezados_google_sheets()),
        )
    return worksheet


def asegurar_encabezados_google_sheets(worksheet) -> None:
    encabezados = encabezados_google_sheets()
    valores = worksheet.get_all_values()
    if not valores:
        worksheet.append_row(encabezados, value_input_option="USER_ENTERED")
        return
    primera_fila = [str(v).strip() for v in valores[0]]
    if primera_fila[: len(encabezados)] != encabezados:
        worksheet.insert_row(encabezados, index=1, value_input_option="USER_ENTERED")


def guardar_respaldo_csv(datos: dict) -> None:
    existe = ARCHIVO_RESPALDO.exists()
    columnas = columnas_internas()
    with ARCHIVO_RESPALDO.open("a", newline="", encoding="utf-8") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=columnas)
        if not existe:
            writer.writeheader()
        writer.writerow(datos)


def guardar_google_sheets(datos: dict) -> tuple[bool, str]:
    try:
        worksheet = obtener_worksheet_google_sheets()
        asegurar_encabezados_google_sheets(worksheet)
        fila = [datos.get(clave, "") for clave in columnas_internas()]
        worksheet.append_row(fila, value_input_option="USER_ENTERED")
        return True, "Guardado en Google Sheets."
    except Exception as error:
        guardar_respaldo_csv(datos)
        return False, str(error)


def crear_cuerpo_solicitud(datos: dict) -> str:
    return f"""
Nueva solicitud de pedido de paltas.

FOLIO
{datos["folio"]}

PEDIDO
Tipo de palta: {datos["tipo_palta"]}
Kilos: {datos["kilos"]} kg
Precio por kg: {formato_pesos(datos["precio_por_kg"])}
Total paltas: {formato_pesos(datos["total_paltas"])}

ENTREGA
Modalidad: {datos["modalidad_entrega"]}
Región: {datos["region"] or "No aplica"}
Comuna: {datos["comuna"] or "No aplica"}
Población / sector: {datos["poblacion"] or "No informado"}
Calle: {datos["calle"] or "No informado"}
Número: {datos["numero"] or "No informado"}

CONTACTO
Nombre: {datos["nombre"]}
WhatsApp: {datos["whatsapp"]}

TRANSFERENCIA
Titular: {TITULAR}
RUT: {RUT}
Banco: {BANCO}
Tipo de cuenta: {TIPO_CUENTA}
Monto sugerido: {formato_pesos(datos["total_paltas"])}

Estado: {datos["estado"]}
Fecha registro: {datos["fecha_registro"]}
"""


def link_whatsapp(datos: dict) -> str:
    mensaje = f"""Nueva solicitud de pedido de paltas.

Pedido:
• Tipo: {datos["tipo_palta"]}
• Cantidad: {datos["kilos"]} kg
• Precio por kg: {formato_pesos(datos["precio_por_kg"])}
• Total paltas: {formato_pesos(datos["total_paltas"])}

Entrega:
• Modalidad: {datos["modalidad_entrega"]}
• Región: {datos["region"] or "No aplica"}
• Comuna: {datos["comuna"] or "No aplica"}
• Población / sector: {datos["poblacion"] or "No informado"}
• Calle: {datos["calle"] or "No informado"}
• Número: {datos["numero"] or "No informado"}

Contacto:
• Nombre: {datos["nombre"]}
• WhatsApp: {datos["whatsapp"]}

Folio: {datos["folio"]}

Quiero coordinar la entrega."""
    return f"https://wa.me/{WHATSAPP_NEGOCIO}?text={quote(mensaje)}"


def datos_actuales() -> dict:
    pedido = session.get("pedido", {})
    return {
        "tipo_palta":        pedido.get("tipo_palta", "Hass"),
        "kilos":             pedido.get("kilos", KILOS_MINIMOS),
        "precio_kg":         pedido.get("precio_kg", PRECIOS_PALTA["Hass"]),
        "total_paltas":      pedido.get("total_paltas", PRECIOS_PALTA["Hass"]),
        "modalidad_entrega": pedido.get("modalidad_entrega", "Retiro sin costo"),
        "region":            pedido.get("region", "Valparaíso"),
        "comuna":            pedido.get("comuna", "La Calera"),
        "poblacion":         pedido.get("poblacion", ""),
        "calle":             pedido.get("calle", ""),
        "numero":            pedido.get("numero", ""),
        "nombre":            pedido.get("nombre", ""),
        "whatsapp":          pedido.get("whatsapp", ""),
    }


def actualizar_pedido(**kwargs) -> None:
    pedido = session.get("pedido", {})
    pedido.update(kwargs)
    session["pedido"] = pedido


def validar_paso_2(modalidad: str, poblacion: str, calle: str, numero: str) -> list[str]:
    errores = []
    if modalidad != "Retiro sin costo":
        if not poblacion.strip(): errores.append("Población / sector")
        if not calle.strip():     errores.append("Calle")
        if not numero.strip():    errores.append("Número")
    return errores


def construir_datos_finales() -> dict:
    pedido = datos_actuales()
    folio  = "PALTA-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    return {
        "folio":             folio,
        "fecha_registro":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo_palta":        pedido["tipo_palta"],
        "kilos":             pedido["kilos"],
        "precio_por_kg":     int(pedido["precio_kg"]),
        "total_paltas":      int(pedido["total_paltas"]),
        "modalidad_entrega": pedido["modalidad_entrega"],
        "region":            pedido["region"],
        "comuna":            pedido["comuna"],
        "poblacion":         pedido["poblacion"],
        "calle":             pedido["calle"],
        "numero":            pedido["numero"],
        "nombre":            pedido["nombre"],
        "whatsapp":          normalizar_whatsapp(pedido["whatsapp"]),
        "estado":            "Solicitud recibida",
    }


# ============================================================
# RUTAS  (idénticas a V6)
# ============================================================

@app.route("/", methods=["GET"])
def index():
    paso = int(session.get("paso", 1))
    paso = max(1, min(4, paso))
    session["paso"] = paso
    return render_template_string(
        INDEX_TEMPLATE,
        paso=paso,
        datos=datos_actuales(),
        precios=PRECIOS_PALTA,
        localidades=LOCALIDADES_CERCANAS,
        regiones_comunas=REGIONES_COMUNAS,
        formato_pesos=formato_pesos,
        titular=TITULAR,
        rut=RUT,
        banco=BANCO,
        tipo_cuenta=TIPO_CUENTA,
        app_version="01_APP_SOLPED_PALTAS · V7",
        resultado=session.pop("resultado", None),
        errores=session.pop("errores", []),
    )


@app.route("/paso/1", methods=["POST"])
def paso_1():
    tipo_palta = request.form.get("tipo_palta", "Hass")
    kilos      = float(request.form.get("kilos", KILOS_MINIMOS))
    precio_kg  = PRECIOS_PALTA[tipo_palta]
    total      = calcular_total(tipo_palta, kilos)
    actualizar_pedido(tipo_palta=tipo_palta, kilos=kilos, precio_kg=precio_kg, total_paltas=total)
    session["paso"] = 2
    return redirect(url_for("index"))


@app.route("/paso/2", methods=["POST"])
def paso_2():
    modalidad = request.form.get("modalidad_entrega", "Retiro sin costo")
    region    = ""
    comuna    = ""
    poblacion = request.form.get("poblacion", "").strip()
    calle     = request.form.get("calle", "").strip()
    numero    = request.form.get("numero", "").strip()

    if modalidad == "Retiro sin costo":
        region = "Valparaíso"
        comuna = request.form.get("comuna_retiro", "La Calera")
        poblacion = calle = numero = ""
    elif modalidad == "Despacho zona cercana":
        region = "Valparaíso"
        comuna = request.form.get("comuna_local", "La Calera")
    else:
        region = request.form.get("region", "Valparaíso")
        comuna = request.form.get("comuna_otra", "La Calera")

    errores = validar_paso_2(modalidad, poblacion, calle, numero)
    if errores:
        session["errores"] = ["Falta completar: " + ", ".join(errores)]
        session["paso"]    = 2
        return redirect(url_for("index"))

    actualizar_pedido(
        modalidad_entrega=modalidad, region=region, comuna=comuna,
        poblacion=poblacion, calle=calle, numero=numero,
    )
    session["paso"] = 3
    return redirect(url_for("index"))


@app.route("/paso/3", methods=["POST"])
def paso_3():
    nombre   = request.form.get("nombre", "").strip()
    whatsapp = request.form.get("whatsapp", "").strip()
    errores  = []
    if not nombre:   errores.append("Nombre")
    if not whatsapp: errores.append("WhatsApp")
    if errores:
        session["errores"] = ["Falta completar: " + ", ".join(errores)]
        session["paso"]    = 3
        return redirect(url_for("index"))
    actualizar_pedido(nombre=nombre, whatsapp=whatsapp)
    session["paso"] = 4
    return redirect(url_for("index"))


@app.route("/registrar", methods=["POST"])
def registrar():
    if request.form.get("confirmar") != "si":
        session["errores"] = ["Confirma que los datos están correctos."]
        session["paso"]    = 4
        return redirect(url_for("index"))
    datos                 = construir_datos_finales()
    google_ok, google_msg = guardar_google_sheets(datos)
    session["resultado"]  = {
        "google_ok":   google_ok,
        "google_msg":  google_msg,
        "whatsapp_url": link_whatsapp(datos),
        "folio":       datos["folio"],
        "total":       formato_pesos(datos["total_paltas"]),
        "texto":       crear_cuerpo_solicitud(datos),
    }
    session["paso"] = 4
    return redirect(url_for("index"))


@app.route("/volver/<int:paso>", methods=["POST"])
def volver(paso: int):
    session["paso"] = max(1, min(4, paso))
    return redirect(url_for("index"))


@app.route("/nuevo", methods=["POST"])
def nuevo():
    session.clear()
    session["paso"] = 1
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
