# Full Implementation Plan: AI Infra Provisioning Guard

This document serves as the complete, step-by-step roadmap that was executed to build the enterprise-grade AI Infra Provisioning Guard. It merges all phases of development—from initial concept to the final "Detect to Correct" (D2C) stream.

---

## Phase 1: Foundation & Architecture

**Goal:** Establish the core modular file structure and integrate the Gemini API with structured outputs (Pydantic).

**Implementation Steps:**
1. **Initialize Project Directory:** Create the `ai-infra-guard` root, along with `src/core` and `src/security` subdirectories.
2. **Define Dependencies (`requirements.txt`):** Ensure `streamlit`, `google-genai`, `pydantic`, and `python-dotenv` are installed.
3. **Draft the Data Schema (`src/core/schemas.py`):**
   - Create a Pydantic `ProvisioningResult` model to strictly define the structured JSON output.
   - Fields: `resource_type`, `requested_permissions`, `approved_permissions`, `risk_level`, `action_taken`, `reasoning`.
4. **Develop the System Prompt (`src/core/prompts.py`):**
   - Define the AI's persona as a "Strict Security Admin."
   - Explicitly instruct the AI to enforce the Principle of Least Privilege and downgrade excessive requests.
5. **Create the Client Integration (`src/core/llm_client.py`):**
   - Implement the connection to Gemini using the `google-genai` SDK.
   - Bind the system prompt and require the response to parse against the Pydantic schema using `response_schema`.
6. **Implement Deterministic Validation (`src/security/validator.py`):**
   - Build a `HybridValidator` containing a hard-coded blocklist (e.g., `0.0.0.0/0`, `ALL PRIVILEGES`).
   - If triggered, the validator overrides the AI's output, setting risk to maximum and blocking the action.

---

## Phase 2: Scenario Handling & B2B Fulfillment

**Goal:** Transform the general system into a highly precise fulfillment engine tailored for the Almaty SME market.

**Implementation Steps:**
1. **Extend the Schema (`src/core/schemas.py`):**
   - Add `suggested_config` to strictly output code snippets.
2. **Embed Few-Shot Prompt Targeting (`src/core/prompts.py`):**
   - Add exact examples instructing the model to generate PostgreSQL `GRANT` statements for database access.
   - Add exact examples instructing the model to generate Cisco IOS `access-list` configurations for network requests.
3. **Update the Validator (`src/security/validator.py`):**
   - Ensure the validator explicitly searches the generated `suggested_config` for destructive rules and forcibly replaces it with a `[SYSTEM OVERRIDE]` comment if blocked.
4. **Build the Initial UI (`app.py`):**
   - Implement the Streamlit frontend with a sidebar for dynamic API Key input.
   - Use `st.code()` to display the `suggested_config` so it can be instantly copied to the clipboard.

---

## Phase 3: The "Detect to Correct" (D2C) Enterprise Layer

**Goal:** Finalize the application with FinOps tracking, hallucination safeguards, and compliance observability.

**Implementation Steps:**
1. **Hallucination Guard (`src/core/schemas.py` & `src/core/prompts.py`):**
   - Introduce a `confidence_score` (1-100) to the schema.
   - Instruct the AI to self-assess its certainty. If the instruction is highly ambiguous, it must lower its score.
2. **FinOps Module Integration (`src/core/llm_client.py`):**
   - Update the client script to extract `prompt_token_count` and `candidates_token_count` from the `usage_metadata` payload.
   - Program the inference cost logic (e.g., Gemini Flash pricing: $0.35 per 1M input, $1.05 per 1M output).
3. **Observability Audit Trail (`app.py`):**
   - Write a `log_to_csv` function to catch every completed transaction.
   - Commit the Timestamp, Risk Level, Cost in USD, AI Confidence, and Raw Query into a local `audit_log.csv` file.
4. **Real-time Metrics Dashboard (`app.py`):**
   - Utilize Streamlit Session State (`st.session_state`) to hold historical data.
   - Implement empty placeholders (`st.empty()`) at the top of the interface and inject cumulative metrics ("Session Cost", "Total BLOCKED", "Total Analyzed") so the dashboard updates instantaneously after each prompt without a full page reload.
5. **JSON Report Export (`app.py`):**
   - Bind an `st.download_button` that packages the exact Pydantic output block and FinOps data into a downloadable JSON receipt.
