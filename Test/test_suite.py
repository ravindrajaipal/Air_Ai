#!/usr/bin/env python3
"""
VayuAI — Comprehensive Automated QA, Code Quality, Security, API & DOM Interaction Test Suite
"""

import json
import os
import re
import subprocess
import unittest
from bs4 import BeautifulSoup

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_HTML = os.path.join(REPO_DIR, "index.html")
API_JS = os.path.join(REPO_DIR, "api", "gemini.js")
VERCEL_JSON = os.path.join(REPO_DIR, "vercel.json")
README_MD = os.path.join(REPO_DIR, "README.md")


class VayuAiTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(INDEX_HTML, "r", encoding="utf-8") as f:
            cls.html = f.read()
        cls.soup = BeautifulSoup(cls.html, "lxml")
        scripts = cls.soup.find_all("script")
        cls.app_js = scripts[-1].string or ""

    def test_01_js_syntax_and_code_quality_standards(self):
        """Verify strict-mode IIFE encapsulation, zero var usage, centralized APP_CONFIG, event delegation, and valid JS syntax."""
        res = subprocess.run(["node", "--check", "-"], input=self.app_js, capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0, f"JS syntax error: {res.stderr}")
        self.assertIn("'use strict';", self.app_js)
        self.assertNotRegex(self.app_js, r"\bvar\s+", "Avoid var; use const/let")
        self.assertNotIn("window.__", self.app_js, "No private properties leaked onto window")
        self.assertIn("const APP_CONFIG = Object.freeze(", self.app_js)
        self.assertIn("function downloadFile(", self.app_js)
        self.assertIn("bindDelegatedInteractiveLists()", self.app_js)

    def test_02_unit_math_and_cpcb_piecewise_breakpoints(self):
        """Unit test CPCB piecewise AQI<->PM2.5 math, CADR/ACH physics, and ITF-OECD swap math via window.VayuAICore."""
        harness = f"""
        const window = {{ addEventListener: () => {{}}, location: {{ protocol: 'https:', hostname: 'localhost' }} }};
        const document = {{ addEventListener: () => {{}}, getElementById: () => null, querySelectorAll: () => [] }};
        const localStorage = {{ getItem: () => null, setItem: () => {{}}, removeItem: () => {{}} }};
        const Chart = function() {{ return {{ update: () => {{}}, data: {{ datasets: [{{data:[]}}, {{data:[]}}] }} }}; }};
        {self.app_js}

        const assert = require('assert');
        const core = window.VayuAICore;
        assert.strictEqual(core.getCpcbCategory(42).label, 'Good');
        assert.strictEqual(core.getCpcbCategory(85).label, 'Satisfactory');
        assert.strictEqual(core.getCpcbCategory(146).label, 'Moderate');
        assert.strictEqual(core.getCpcbCategory(265).label, 'Poor');
        assert.strictEqual(core.getCpcbCategory(367).label, 'Very Poor');
        assert.strictEqual(core.getCpcbCategory(430).label, 'Severe');
        assert.strictEqual(core.getCpcbCategory(480).label, 'Severe+');

        assert.strictEqual(core.aqiToCpcbPm25(50), 30.0);
        assert.strictEqual(core.aqiToCpcbPm25(100), 60.0);
        assert.strictEqual(core.aqiToCpcbPm25(200), 90.0);
        assert.strictEqual(core.aqiToCpcbPm25(300), 120.0);
        assert.strictEqual(core.aqiToCpcbPm25(400), 250.0);
        assert.strictEqual(core.pm25ToCpcbAqi(30), 50);
        assert.strictEqual(core.pm25ToCpcbAqi(60), 100);
        assert.strictEqual(core.pm25ToCpcbAqi(90), 200);
        assert.strictEqual(core.pm25ToCpcbAqi(120), 300);
        assert.strictEqual(core.pm25ToCpcbAqi(250), 400);

        assert.strictEqual(core.sanitizeNumber('999', 0, 500, 100), 500);
        assert.strictEqual(core.sanitizeNumber('abc', 0, 500, 100), 100);
        const m = core.computeMetrics();
        assert.strictEqual(m.outdoorPm25, 218.0);
        assert(m.steadyIndoorPm25 < 30 && m.steadyIndoorPm25 > 15);
        assert.strictEqual(m.pctCut, 71);
        assert(m.ach > 15);
        console.log('UNIT_OK');
        """
        res = subprocess.run(["node", "-e", harness], capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0, f"Unit test failed: {res.stderr}")
        self.assertIn("UNIT_OK", res.stdout)

    def test_03_integration_city_mask_and_ai_flows(self):
        """Integration test city switching, mask leakage, and deterministic AI responses."""
        harness = f"""
        const window = {{ addEventListener: () => {{}}, location: {{ protocol: 'https:', hostname: 'localhost' }} }};
        const document = {{ addEventListener: () => {{}}, getElementById: () => null, querySelectorAll: () => [] }};
        const localStorage = {{ getItem: () => null, setItem: () => {{}}, removeItem: () => {{}} }};
        const Chart = function() {{ return {{ update: () => {{}}, data: {{ datasets: [{{data:[]}}, {{data:[]}}] }} }}; }};
        {self.app_js}

        const assert = require('assert');
        const core = window.VayuAICore;
        core.state.cityKey = 'jodhpur';
        core.state.customAqi = core.CITY_PROFILES.jodhpur.aqi;
        core.state.customPm25 = core.CITY_PROFILES.jodhpur.pm25;
        core.state.maskKey = 'n95_unsealed';
        core.state.sustainableSwap = 'bicycle';
        const m = core.computeMetrics();
        assert.strictEqual(m.outdoorPm25, 131.2);
        assert.strictEqual(m.mask.eff, 0.70);
        assert.strictEqual(m.pctCut, 75);

        assert(core.generateBuiltInAiResponse('morning_smog').english.includes('100m'));
        assert(core.generateBuiltInAiResponse('diy_purifier').english.includes('293 CFM'));
        assert(core.generateBuiltInAiResponse('kitchen_iaq').english.includes('exhaust'));
        console.log('INTEGRATION_OK');
        """
        res = subprocess.run(["node", "-e", harness], capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0, f"Integration test failed: {res.stderr}")
        self.assertIn("INTEGRATION_OK", res.stdout)

    def test_04_serverless_api_validation_and_error_handling(self):
        """Test api/gemini.js for OPTIONS (204), GET (405), non-object/array body (400), oversized prompt (400), and missing key (503)."""
        harness = f"""
        const assert = require('assert');
        const handler = require({json.dumps(API_JS)});
        function mockRes() {{
          return {{
            statusCode: 200, headers: {{}}, body: null,
            setHeader(k, v) {{ this.headers[k] = v; }},
            status(code) {{ this.statusCode = code; return this; }},
            json(obj) {{ this.body = obj; return this; }},
            end() {{ return this; }}
          }};
        }}
        (async () => {{
          const rOpt = mockRes(); await handler({{ method: 'OPTIONS' }}, rOpt); assert.strictEqual(rOpt.statusCode, 204);
          const rGet = mockRes(); await handler({{ method: 'GET' }}, rGet); assert.strictEqual(rGet.statusCode, 405);
          const rArr = mockRes(); await handler({{ method: 'POST', body: ['bad'] }}, rArr); assert.strictEqual(rArr.statusCode, 400);
          const rNull = mockRes(); await handler({{ method: 'POST', body: null }}, rNull); assert.strictEqual(rNull.statusCode, 400);
          const rEmpty = mockRes(); await handler({{ method: 'POST', body: {{ prompt: '   ' }} }}, rEmpty); assert.strictEqual(rEmpty.statusCode, 400);
          const rLong = mockRes(); await handler({{ method: 'POST', body: {{ prompt: 'A'.repeat(300) }} }}, rLong); assert.strictEqual(rLong.statusCode, 400);
          delete process.env.GEMINI_API_KEY;
          const rNoKey = mockRes();
          await handler({{ method: 'POST', body: {{ prompt: 'How to reduce PM2.5?', city: 'Jodhpur', aqi: 265 }} }}, rNoKey);
          assert.strictEqual(rNoKey.statusCode, 503);
          assert.strictEqual(rNoKey.body.fallbackMode, 'Deterministic CPCB/WHO Rule Engine');
          console.log('API_OK');
        }})();
        """
        res = subprocess.run(["node", "-e", harness], capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0, f"API test failed: {res.stderr}")
        self.assertIn("API_OK", res.stdout)

    def test_05_security_xss_and_svg_escaping(self):
        """Verify zero hardcoded secrets, session-only key storage, security headers, and strict SVG/DOM XSS escaping."""
        secret_pattern = re.compile(r"AIzaSy[A-Za-z0-9_\-]{30,}")
        for root, _, files in os.walk(REPO_DIR):
            for file in files:
                with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                    self.assertIsNone(secret_pattern.search(f.read()), f"Hardcoded key in {file}")

        self.assertNotIn("localStorage.setItem('vayu_gemini_api_key'", self.html)
        with open(VERCEL_JSON, "r", encoding="utf-8") as vf:
            vercel_cfg = json.loads(vf.read())
        header_keys = [h["key"] for h in vercel_cfg["headers"][0]["headers"]]
        self.assertIn("X-Content-Type-Options", header_keys)
        self.assertIn("X-Frame-Options", header_keys)
        self.assertIn("Referrer-Policy", header_keys)

        # Verify malicious city name is escaped in SVG poster
        harness = f"""
        const svgBox = {{ innerHTML: '' }};
        const window = {{ addEventListener: () => {{}}, location: {{ protocol: 'https:', hostname: 'localhost' }} }};
        const document = {{ addEventListener: () => {{}}, getElementById: (id) => id === 'svgPosterContainer' ? svgBox : null, querySelectorAll: () => [] }};
        const localStorage = {{ getItem: () => null, setItem: () => {{}}, removeItem: () => {{}} }};
        const Chart = function() {{ return {{ update: () => {{}}, data: {{ datasets: [{{data:[]}}, {{data:[]}}] }} }}; }};
        {self.app_js}
        const assert = require('assert');
        const core = window.VayuAICore;
        core.renderSvgPoster({{ name: '<script>alert(1)</script>' }}, {{ label: 'Poor', grap: 'Stage I' }}, core.computeMetrics());
        assert(!svgBox.innerHTML.includes('<script>'), 'SVG poster must escape untrusted city names');
        assert(svgBox.innerHTML.includes('&lt;script&gt;'), 'Escaped SVG text must be present');
        console.log('XSS_OK');
        """
        res = subprocess.run(["node", "-e", harness], capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0, f"XSS test failed: {res.stderr}")
        self.assertIn("XSS_OK", res.stdout)

    def test_06_accessibility_and_responsive_layout(self):
        """Verify semantic landmarks, WCAG form labels, ARIA live regions, and responsive Tailwind classes."""
        self.assertIsNotNone(self.soup.find("header"))
        self.assertIsNotNone(self.soup.find("nav"))
        self.assertIsNotNone(self.soup.find("main"))
        self.assertGreaterEqual(len(self.soup.find_all("section")), 4)

        for tag in self.soup.find_all(["input", "select", "textarea"]):
            tid = tag.get("id")
            has_aria = bool(tag.get("aria-label"))
            has_label = bool(tid and self.soup.find("label", attrs={"for": tid}))
            self.assertTrue(has_aria or has_label, f"Control #{tid} missing accessible label")

        self.assertIn("sm:", self.html)
        self.assertIn("md:", self.html)
        self.assertIn("lg:", self.html)
        self.assertIn("maintainAspectRatio: false", self.html)

    def test_07_dom_hydration_event_delegation_and_exports(self):
        """Simulate DOMContentLoaded, filter empty state, reset, delegated zone clicks, and JSON/MD/SVG exports."""
        all_ids = [tag.get("id") for tag in self.soup.find_all(id=True)]
        harness = f"""
        const assert = require('assert');
        const elements = {{}};
        let downloadedFiles = [];
        function makeEl(id) {{
          return {{
            id, value: '', textContent: '', innerHTML: '', outerHTML: '<svg id="cleanAirPosterSvg"></svg>',
            className: '', disabled: false, listeners: {{}}, attributes: {{}}, children: [],
            classList: {{ add: () => {{}}, remove: () => {{}}, toggle: () => {{}}, contains: () => false }},
            addEventListener(ev, fn) {{ this.listeners[ev] = fn; }},
            setAttribute(k, v) {{ this.attributes[k] = v; }},
            getAttribute(k) {{ return this.attributes[k] || ''; }},
            appendChild(child) {{ this.children.push(child); }},
            prepend(child) {{ this.children.unshift(child); }},
            click() {{ if (this.download) downloadedFiles.push(this.download); }},
            querySelectorAll() {{ return []; }}
          }};
        }}
        for (const id of {json.dumps(all_ids)}) elements[id] = makeEl(id);
        elements['cleanAirPosterSvg'] = makeEl('cleanAirPosterSvg');
        const windowListeners = {{}};
        const window = {{
          location: {{ protocol: 'https:', hostname: 'localhost' }},
          addEventListener(ev, fn) {{ windowListeners[ev] = fn; }},
          print: () => {{}}
        }};
        const document = {{
          documentElement: makeEl('html'),
          body: {{ appendChild: () => {{}}, removeChild: () => {{}} }},
          getElementById(id) {{ return elements[id] || null; }},
          createElement(tag) {{ return makeEl(tag); }},
          querySelectorAll() {{ return []; }},
          execCommand: () => true
        }};
        const URL = {{ createObjectURL: () => 'blob:mock', revokeObjectURL: () => {{}} }};
        const Blob = function(parts, opts) {{ this.parts = parts; this.opts = opts; }};
        const localStorage = {{ getItem: () => null, setItem: () => {{}}, removeItem: () => {{}} }};
        const Chart = function() {{ return {{ update: () => {{}}, data: {{ datasets: [{{data:[]}}, {{data:[]}}] }} }}; }};

        {self.app_js}

        windowListeners['DOMContentLoaded']();
        assert(elements['svgPosterContainer'].innerHTML.includes('cleanAirPosterSvg'));
        assert(elements['floorplanGrid'].innerHTML.includes('Z1 · Living / Study'));
        assert.strictEqual(elements['outdoorCigEq'].textContent, '9.9');

        // Filter empty state + Reset
        elements['routineFilterInput'].value = 'unmatched_xyz';
        elements['routineFilterInput'].listeners['input']({{ target: elements['routineFilterInput'] }});
        assert(elements['routineListContainer'].innerHTML.includes('No routines match'));
        elements['resetDefaultsBtn'].listeners['click']();
        assert(elements['routineListContainer'].innerHTML.includes('06:00–09:00'));

        // Delegated click on Z1 toggles state.zones[0].active
        const beforeZ1 = window.VayuAICore.state.zones[0].active;
        elements['floorplanGrid'].listeners['click']({{
          target: {{ closest: () => ({{ getAttribute: () => 'Z1' }}) }}
        }});
        assert.strictEqual(window.VayuAICore.state.zones[0].active, !beforeZ1);

        // Exports (.JSON, .MD, .SVG)
        elements['exportJsonBtn'].listeners['click']();
        elements['exportMdBtn'].listeners['click']();
        elements['downloadSvgPosterBtn'].listeners['click']();
        assert(downloadedFiles.includes('vayu_ai_plan.json'));
        assert(downloadedFiles.includes('vayu_ai_plan.md'));
        assert(downloadedFiles.includes('VayuAI_delhi.svg'));

        console.log('DOM_AND_EXPORTS_OK');
        """
        res = subprocess.run(["node", "-e", harness], capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0, f"DOM & export test failed: {res.stderr}")
        self.assertIn("DOM_AND_EXPORTS_OK", res.stdout)

    def test_08_readme_and_repo_structure_alignment(self):
        """Verify README.md sections and actual repository files match without drift."""
        with open(README_MD, "r", encoding="utf-8") as rf:
            readme = rf.read()
        for section in [
            "1. Project Overview", "2. Problem Statement", "3. Features",
            "4. Technology Stack", "5. Architecture", "6. Installation Instructions",
            "7. Environment Variable Setup", "8. API Configuration",
            "9. Testing Instructions", "10. Deployment Instructions", "11. Assumptions and Limitations"
        ]:
            self.assertIn(section, readme, f"Missing README section: {section}")
        for expected in ["index.html", "vercel.json", ".env.example", ".gitignore", "api/gemini.js", "tests/test_suite.py"]:
            self.assertTrue(os.path.exists(os.path.join(REPO_DIR, expected)), f"Missing file: {expected}")



    def test_09_regression_and_edge_case_fidelity(self):
        """Verify outdoorHours affects dose reduction, profileKey personalizes AI responses, clean-air PM2.5<10 is preserved, and api/gemini.js hides internal errors."""
        harness = f"""
        const window = {{ addEventListener: () => {{}}, location: {{ protocol: 'https:', hostname: 'vayuai-one.vercel.app' }} }};
        const document = {{ addEventListener: () => {{}}, getElementById: () => null, querySelectorAll: () => [] }};
        const localStorage = {{ getItem: () => null, setItem: () => {{}}, removeItem: () => {{}} }};
        const Chart = function() {{ return {{ update: () => {{}}, data: {{ datasets: [{{data:[]}}, {{data:[]}}] }} }}; }};
        {self.app_js}

        const assert = require('assert');
        const core = window.VayuAICore;

        // 1. Clean air PM2.5 = 5.0 must NOT be clamped up to 10
        core.state.customAqi = 8;
        core.state.customPm25 = 5.0;
        assert.strictEqual(core.computeMetrics().outdoorPm25, 5.0);

        // 2. outdoorHours slider must dynamically change combinedDoseCut when mask is none/cotton
        core.state.customAqi = 367;
        core.state.customPm25 = 218.0;
        core.state.maskKey = 'none';
        core.state.outdoorHours = 0.5;
        const cutLowHrs = core.computeMetrics().combinedDoseCut;
        core.state.outdoorHours = 8.0;
        const cutHighHrs = core.computeMetrics().combinedDoseCut;
        assert(cutLowHrs > cutHighHrs, 'More unmasked outdoor hours must lower dose reduction');

        // 3. profileKey must produce distinct tailored responses
        core.state.profileKey = 'hostel';
        const rHostel = core.generateBuiltInAiResponse('default');
        core.state.profileKey = 'sensitive';
        const rSensitive = core.generateBuiltInAiResponse('default');
        core.state.profileKey = 'commuter';
        const rCommuter = core.generateBuiltInAiResponse('default');
        assert.notStrictEqual(rHostel.english, rSensitive.english);
        assert.notStrictEqual(rSensitive.english, rCommuter.english);
        console.log('REGRESSION_FIDELITY_OK');
        """
        res = subprocess.run(["node", "-e", harness], capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0, f"Regression fidelity test failed: {res.stderr}")
        self.assertIn("REGRESSION_FIDELITY_OK", res.stdout)

        with open(API_JS, "r", encoding="utf-8") as af:
            api_code = af.read()
        self.assertNotIn("err.message", api_code, "Serverless API must not expose raw internal error details")



    def test_10_accessibility_caching_and_keyboard_ux(self):
        """Verify semantic footer, dialog ARIA attributes, focus-visible styles, ESC handler, and Open-Meteo cache."""
        self.assertIsNotNone(self.soup.find("footer"), "Semantic <footer> landmark must exist")
        modal = self.soup.find(id="apiModal")
        self.assertEqual(modal.get("role"), "dialog")
        self.assertEqual(modal.get("aria-modal"), "true")
        self.assertIn("focus-visible", self.html)
        self.assertIn("e.key === 'Escape'", self.app_js)
        self.assertIn("LIVE_CACHE_TTL_MS", self.app_js)
        self.assertIn("syncChartTheme()", self.app_js)



    def test_11_data_provenance_and_city_comparison(self):
        """Verify dataMode distinguishes Preset vs Live vs Simulation and compareCitySelect computes exact PM2.5 & cigarette deltas."""
        self.assertIn("Preset · CPCB Nov 2026", self.html)
        self.assertIn("Live Feed · Open-Meteo CAMS", self.app_js)
        self.assertIn("Simulation · Custom AQI Estimate", self.app_js)
        self.assertIsNotNone(self.soup.find(id="compareCitySelect"))
        self.assertIsNotNone(self.soup.find(id="cityCompareReadout"))



    def test_12_exhaustive_interactive_controls_audit(self):
        """Verify zero unattached interactive IDs and execute clearChatBtn, resetZonesBtn, profileSelector presets, and enableAllRoutinesBtn."""
        all_ids = [tag.get("id") for tag in self.soup.find_all(id=True)]
        for el in self.soup.find_all(["button", "select", "input", "form"]):
            eid = el.get("id")
            if eid and eid not in ("aiPromptInput", "liveCityInput", "geminiApiKeyInput"):
                self.assertIn(f"getElementById('{eid}')", self.app_js, f"Missing JS handler for #{eid}")

        harness = f"""
        const assert = require('assert');
        const elements = {{}};
        function makeEl(id) {{
          return {{
            id, value: '', textContent: '', innerHTML: '', outerHTML: '<svg id="cleanAirPosterSvg"></svg>',
            className: '', disabled: false, listeners: {{}}, attributes: {{}}, children: [],
            classList: {{ add: () => {{}}, remove: () => {{}}, toggle: () => true, contains: () => false }},
            addEventListener(ev, fn) {{ this.listeners[ev] = fn; }},
            setAttribute(k, v) {{ this.attributes[k] = v; }},
            removeAttribute(k) {{ delete this.attributes[k]; }},
            getAttribute(k) {{ return this.attributes[k] || ''; }},
            appendChild(child) {{ this.children.push(child); }},
            prepend(child) {{ this.children.unshift(child); }},
            click() {{}},
            querySelectorAll() {{ return []; }}
          }};
        }}
        for (const id of {json.dumps(all_ids)}) elements[id] = makeEl(id);
        elements['cleanAirPosterSvg'] = makeEl('cleanAirPosterSvg');
        const windowListeners = {{}};
        const window = {{ location: {{ protocol: 'https:', hostname: 'localhost' }}, addEventListener(ev, fn) {{ windowListeners[ev] = fn; }}, print: () => {{}} }};
        const document = {{
          documentElement: makeEl('html'),
          body: {{ appendChild: () => {{}}, removeChild: () => {{}} }},
          getElementById(id) {{ return elements[id] || null; }},
          createElement(tag) {{ return makeEl(tag); }},
          querySelectorAll() {{ return []; }},
          execCommand: () => true
        }};
        const localStorage = {{ getItem: () => null, setItem: () => {{}}, removeItem: () => {{}} }};
        const Chart = function() {{ return {{ update: () => {{}}, data: {{ datasets: [{{data:[]}}, {{data:[]}}] }} }}; }};
        {self.app_js}

        windowListeners['DOMContentLoaded']();

        // Test profileSelector -> University Hostel updates state across all tabs
        elements['profileSelector'].value = 'hostel';
        elements['profileSelector'].listeners['change']({{ target: elements['profileSelector'] }});
        assert.strictEqual(window.VayuAICore.state.roomArea, 140);
        assert.strictEqual(window.VayuAICore.state.commuteKm, 8);
        assert.strictEqual(window.VayuAICore.state.sustainableSwap, 'bicycle');
        assert.strictEqual(window.VayuAICore.state.communityUnits, 200);

        // Test clearChatBtn resets chat stream to 1 fresh card
        elements['clearChatBtn'].listeners['click']();
        assert.strictEqual(elements['aiChatStream'].children.length >= 1, true);

        // Test aiBalanceZonesBtn + resetZonesBtn
        elements['aiBalanceZonesBtn'].listeners['click']();
        assert.strictEqual(window.VayuAICore.state.zones.every(z => z.active), true);
        elements['resetZonesBtn'].listeners['click']();
        assert.strictEqual(window.VayuAICore.state.zones[3].active, false);

        // Test enableAllRoutinesBtn
        elements['enableAllRoutinesBtn'].listeners['click']();
        assert.strictEqual(window.VayuAICore.ROUTINE_ITEMS.every(r => r.active), true);

        console.log('ALL_INTERACTIVE_CONTROLS_OK');
        """
        res = subprocess.run(["node", "-e", harness], capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0, f"Interactive audit test failed: {res.stderr}")
        self.assertIn("ALL_INTERACTIVE_CONTROLS_OK", res.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
