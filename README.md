# AI Infra Provisioning Guard

## Project Vision
The **AI Infra Provisioning Guard** is an enterprise-grade triage engine designed specifically for the Almaty SME market. By acting as a "Strict Security Admin," the application intercepts infrastructure provisioning requests, analyzes them through a robust Pydantic-powered AI logic stream, and strictly enforces the Principle of Least Privilege. It transforms potentially ambiguous and dangerous natural-language resource requests into secure, syntactically correct Cisco IOS and PostgreSQL parameters, defending your enterprise from both user error and internal AI hallucination.

## IT4IT Mapping

This project maps directly to the IT4IT lifecycle architecture:

* **Strategy to Portfolio (S2P):** We addressed a specific market gap—SMEs scaling their digital infrastructure but lacking dedicated cloud security architects—by strategically leveraging Gemini 1.5 Flash as an automated cloud gatekeeper.
* **Requirement to Deploy (R2D):** Driven by an Agentic CI/CD approach, the Product Architect (You) provided clear systemic directives, allowing me (the AI) to rapidly modularize a comprehensive, robust file structure. We deployed the core business logic (`schemas.py`, `llm_client.py`) in hours rather than weeks.
* **Request to Fulfill (R2F):** The clean Streamlit UI manages fulfillment requests. Instead of generic textual advice, it outputs deterministic code (Cisco IOS `access-list`, PostgreSQL `GRANT` rules). An admin can review the "Risk Dashboard," observe the explicit fallback logic, and instantly copy the syntax-perfect snippet to production.
* **Detect to Correct (D2C):** We integrated vital enterprise monitors natively into the pipeline. A real-time FinOps module extracts exact API token data calculating exact USD transaction costs. The reactive Hallucination Guard parses the AI's `confidence_score` (`< 85%`), and a deterministic `HybridValidator` acts as a hard breakpoint against catastrophic inputs (e.g., `0.0.0.0/0`), automatically appending every transaction into a comprehensive local `audit_log.csv`.

## Setup Instructions

**Prerequisites:**
- Python 3.9+
- A Google Gemini API Key

**Installation Steps:**
1. **Navigate** to the dedicated application directory:
   ```bash
   cd ./ai-infra-guard
   ```
2. **Install Dependencies** via `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Setup**:
   - For an immediate start, you can input your API key directly on the Streamlit Sidebar UI.
   - For constant sessions, use the generated `.env` file and set your key:
     ```env
     GEMINI_API_KEY="your_actual_key_here"
     ```
4. **Boot the Application**:
   ```bash
   streamlit run app.py
   ```
5. **Observability Tracking**:
   The `audit_log.csv` will automatically generate in the root project directory the moment the first user submits a request. Watch your S2P and FinOps metrics grow organically on subsequent usages.
