# 🚀 Sprint 1: The "Steel Thread" Execution
**Project:** Linker BI  
**Goal:** Establish the end-to-end flow from database introspection to the first validated SQL execution.

---

### **LNK-1.1: Extended LinkerState Implementation**
**Description:** Expand the base state to include custom fields required for the BI orchestration and inter-agent communication.
**Technical Tasks:**
* Add plan (List of strings) to track the execution strategy.
* Add metadata (Dictionary) for database schema results.
* Add semantic_layer (Optional string) for the generated YAML content.
* Add errors (List of strings) to capture feedback for the Critic loop.
**Acceptance Criteria:**
* State updates correctly across LangGraph nodes.
* Data is persisted between transitions in the graph.

---

### **LNK-1.2: Discovery Agent (SQLAlchemy Introspector)**
**Description:** Develop the "eyes" of the system—an agent capable of reading and mapping any database schema.
**Technical Tasks:**
* Implement DiscoveryAgent by inheriting from LinkerBaseAgent.
* Use sqlalchemy.inspect to extract table names, column types, and PK/FK relationships.
* Format the output into a structured dictionary for the state metadata.
**Acceptance Criteria:**
* Agent produces a full schema map of the connected database.
* Successfully handles SQLite and PostgreSQL dialects.

---

### **LNK-1.3: PydanticAI Semantic Expert (YAML Mapping)**
**Description:** Create a specialized PydanticAI agent to build the semantic layer with strict validation logic.
**Technical Tasks:**
* Define the SemanticLayer Pydantic model including metrics, dimensions, and aliases.
* Use pydantic_ai.Agent to map raw DB metadata to the business-logic model.
* Implement self-correction logic to handle LLM validation errors automatically.
**Acceptance Criteria:**
* Output is a strictly validated YAML object.
* LLM hallucinations regarding data types are blocked by Pydantic validation.

---

### **LNK-1.4: Planner Agent Node**
**Description:** An agent that decomposes the user's Natural Language query into logical execution steps.
**Technical Tasks:**
* Implement PlannerAgent logic.
* Use the Semantic Layer context to identify relevant tables and metrics.
* Generate a sequence of tasks: SQL Generation, Extraction, and Validation.
**Acceptance Criteria:**
* The plan in the state is logical and specific to the user's question.

---

### **LNK-1.5: Text-to-SQL Execution Engine**
**Description:** The core engine that transforms the plan and semantic aliases into executable SQL code.
**Technical Tasks:**
* Create a prompt for SQL generation using YAML-defined business names.
* Execute queries within a Read-Only transaction.
* Map query results into a structured format like a DataFrame.
**Acceptance Criteria:**
* Generated SQL is syntactically correct for the target database.
* Results are captured in the state without interrupting the flow.

---

### **LNK-1.6: Critic Agent (Feedback Loop)**
**Description:** A quality control agent that reviews the generated SQL and data for errors or security risks.
**Technical Tasks:**
* Check SQL for security risks and forbidden keywords.
* Validate if the resulting data is consistent with the initial question.
* Trigger a conditional loop back to the Executor if errors are found.
**Acceptance Criteria:**
* Agent can successfully initiate a retry loop in LangGraph.

---

### **LNK-1.7: LangGraph Assembly & Orchestration**
**Description:** Connect all individual nodes into a functional, cyclic orchestration graph.
**Technical Tasks:**
* Assemble all nodes using the StateGraph(LinkerState).
* Define conditional edges from the Critic node back to the Executor.
* Compile the graph with a persistent memory checkpointer.
**Acceptance Criteria:**
* The graph visualization shows the correct cyclic flow.
* The system runs end-to-end for a sample query.

---

### **LNK-1.8: Execution Sandbox & Safety Guardrails**
**Description:** A security layer to prevent destructive actions and handle resource limits.
**Technical Tasks:**
* Implement a sandbox utility to enforce SELECT-only permissions.
* Apply execution timeouts for long-running queries.
* Log all database interactions for auditing.
**Acceptance Criteria:**
* Destructive commands like DROP or DELETE are blocked.
* Resource-intensive queries are terminated automatically.

---

### **LNK-1.9: Typer CLI for Local Testing**
**Description:** A command-line interface to interact with Linker BI during development and debugging.
**Technical Tasks:**
* Build the CLI using the Typer library.
* Implement rich logging to display agent progress and graph traces.
**Acceptance Criteria:**
* Users can run queries from the terminal and see the agent's thought process.