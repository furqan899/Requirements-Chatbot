from typing import Dict, List, Any
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import streamlit as st
from datetime import datetime
import os
import openai
from docx import Document
from docx.shared import Inches
import pdfplumber
from io import StringIO
from docx import Document as docxDocument

# Initialize LLM
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_text(messages):
    # Ensure messages are in the correct format for chat-based models
    response = openai.ChatCompletion.create(
        model="gpt-4",  # or "gpt-4" if you're using GPT-4
        messages=messages,
        max_tokens=1024,
        temperature=0.7,
    )
    
    # Return the generated text from the response
    return response['choices'][0]['message']['content']

# State definition
class ProjectState(BaseModel):
    project_info: Dict = Field(default_factory=dict)
    wbs: str = ""
    diagrams: Dict[str, str] = Field(default_factory=dict)
    estimates: Dict[str, Any] = Field(default_factory=dict)
    documents: Dict[str, str] = Field(default_factory=dict)
    user_roles: List[str] = []
    user_flows: Dict[str, List[str]] = Field(default_factory=dict)
    suggested_tech_stacks: List[str] = []

# Nodes for the graph
def collect_project_info(state):
    with st.expander("Project Details"):
        state.project_info["project_name"] = st.text_input("Project Title")
        state.project_info["overview"] = st.text_area("Project Overview")
        state.project_info["modules"] = st.text_area("Main Modules/Features")

        # Suggest tech stacks
        suggested_tech_stacks = suggest_tech_stacks(state.project_info["modules"])
        state.suggested_tech_stacks = suggested_tech_stacks

        # Allow user to select tech stacks
        state.project_info["tech_stack"] = st.multiselect("Tech Stack", 
                                                         suggested_tech_stacks, 
                                                         default=suggested_tech_stacks)

        # Optional: File upload
        uploaded_file = st.file_uploader("Upload Project Requirements (optional)")
        if uploaded_file is not None:
            # Process the uploaded file (e.g., extract text from doc/pdf)
            if uploaded_file.type == "application/pdf":
                # Extract text from PDF using pdfplumber
                text = extract_text_from_pdf(uploaded_file)
                st.text_area("Extracted Text", text)
                state.project_info["overview"] = text  # Example of adding the overview
            elif uploaded_file.type == "application/msword":
                # Extract text from Word document
                text = extract_text_from_docx(uploaded_file)
                st.text_area("Extracted Text", text)
                state.project_info["overview"] = text  # Example of adding the overview
        return {"project_info": state.project_info}

def extract_text_from_pdf(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(uploaded_file):
    doc = docxDocument.open(uploaded_file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def define_user_roles(state):
    with st.expander("User Roles"):
        state.user_roles = st.multiselect("User Roles", ["Admin", "User", "Guest", "Other"])
        for role in state.user_roles:
            user_stories = st.text_area(f"User Stories for {role}")
            state.user_flows[role] = user_stories.split("\n")
        return state

def generate_wbs(state):
    prompt = ChatPromptTemplate.from_template("""
    Create a detailed WBS for project:
    {project_details}
    Include time estimates and dependencies.
    Consider tech stacks: {tech_stacks}
    """)
    chain = prompt | generate_text | StrOutputParser()
    state.wbs = chain.invoke({
        "project_details": str(state.project_info),
        "tech_stacks": ", ".join(state.project_info["tech_stack"])
    })
    return state

def generate_diagrams(state):
    diagram_types = {
        "dfd": """Generate a Mermaid.js Data Flow Diagram for:
                 Roles: {roles}
                 Features: {features}""",
        "erd": """Generate a Mermaid.js Entity Relationship Diagram for:
                 Project: {project}
                 Features: {features}""",
        "user_flow": """Generate a Mermaid.js User Flow diagram for:
                        Roles: {roles}
                        Features: {features}""",
        "backend_arch": """Generate a Mermaid.js diagram for the backend architecture of this project:
                          Tech Stacks: {tech_stacks}
                          Modules: {modules}"""
    }

    for diagram_type, prompt_template in diagram_types.items():
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | generate_text | StrOutputParser()
        state.diagrams[diagram_type] = chain.invoke({
            "roles": ", ".join(state.user_roles),
            "features": state.project_info.get("modules", ""),
            "project": state.project_info.get("project_name", ""),
            "tech_stacks": ", ".join(state.project_info["tech_stack"])
        })
    return state

def calculate_estimates(state):
    prompt = ChatPromptTemplate.from_template("""
    Based on WBS:
    {wbs}
    Generate detailed time and cost estimates considering complexity: {complexity}
    """)
    chain = prompt | generate_text | StrOutputParser()
    estimates = chain.invoke({
        "wbs": state.wbs,
        "complexity": state.project_info.get("complexity", "Medium")
    })

    state.estimates = {
        "time": generate_time_table(estimates),
        "cost": generate_cost_breakdown(estimates)
    }
    return state

def generate_documents(state):
    document_types = {
        "proposal": """Create a comprehensive project proposal including:
                       {project_info}
                       WBS: {wbs}
                       Estimates: {estimates}""",
        "technical_spec": """Create technical specifications based on:
                             {project_info}
                             Diagrams: {diagrams}"""
    }

    for doc_type, prompt_template in document_types.items():
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | generate_text | StrOutputParser()
        state.documents[doc_type] = chain.invoke({
            "project_info": str(state.project_info),
            "wbs": state.wbs,
            "estimates": str(state.estimates),
            "diagrams": str(state.diagrams)
        })
    return state

# Helper functions
def generate_time_table(estimates_text: str) -> Dict:
    prompt = ChatPromptTemplate.from_template("""
    Convert this estimation text to a structured time table:
    {estimates}
    """)
    chain = prompt | generate_text | StrOutputParser()
    return eval(chain.invoke({"estimates": estimates_text}))

def generate_cost_breakdown(estimates_text: str) -> Dict:
    prompt = ChatPromptTemplate.from_template("""
    Convert this estimation text to a detailed cost breakdown:
    {estimates}
    """)
    chain = prompt | generate_text | StrOutputParser()
    return eval(chain.invoke({"estimates": estimates_text}))

def suggest_tech_stacks(modules):
    prompt = ChatPromptTemplate.from_template("""
    Suggest relevant tech stacks for a project with the following modules:
    {modules}
    """)
    chain = prompt | generate_text | StrOutputParser()
    suggested_stacks = chain.invoke({"modules": modules})
    return suggested_stacks.split(", ")

def generate_proposal_document(state):
    doc = Document()

    doc.add_heading('Project Proposal', 0)

    doc.add_heading('Project Title', level=1)
    doc.add_paragraph(state.project_info["project_name"])

    doc.add_heading('Project Overview', level=1)
    doc.add_paragraph(state.project_info["overview"])

    doc.add_heading('Modules/Features', level=1)
    doc.add_paragraph(state.project_info["modules"])

    doc.add_heading('Tech Stacks', level=1)
    for stack in state.project_info["tech_stack"]:
        doc.add_paragraph(f"- {stack}")

    doc.add_heading('User Roles and Flows', level=1)
    for role, flows in state.user_flows.items():
        doc.add_heading(f"{role}", level=2)
        for flow in flows:
            doc.add_paragraph(f"- {flow}")

    doc.add_heading('Diagrams', level=1)
    for diagram_type, diagram in state.diagrams.items():
        doc.add_heading(f"{diagram_type.upper()}", level=2)
        doc.add_paragraph(diagram)

    doc.add_heading('Work Breakdown Structure (WBS)', level=1)
    doc.add_paragraph(state.wbs)

    doc.add_heading('Time Estimates', level=1)
    for key, value in state.estimates["time"].items():
        doc.add_paragraph(f"{key}: {value}")

    doc.add_heading('Cost Estimates', level=1)
    for key, value in state.estimates["cost"].items():
        doc.add_paragraph(f"{key}: {value}")

    doc.add_heading('Disclaimer', level=1)
    doc.add_paragraph("This project proposal is subject to change based on further analysis and client feedback.")

    # Save the document
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
    doc_name = f"project_proposal_{current_datetime}.docx"
    doc.save(doc_name)

    return doc_name

# Graph definition
def create_graph() -> StateGraph:
    workflow = StateGraph(ProjectState)

    workflow.add_node("collect_info", collect_project_info)
    workflow.add_node("define_user_roles", define_user_roles)
    workflow.add_node("generate_wbs", generate_wbs)
    workflow.add_node("generate_diagrams", generate_diagrams)
    workflow.add_node("calculate_estimates", calculate_estimates)
    workflow.add_node("generate_documents", generate_documents)

    workflow.set_entry_point("collect_info")

    workflow.add_edge("collect_info", "define_user_roles")
    workflow.add_edge("define_user_roles", "generate_wbs")
    workflow.add_edge("generate_wbs", "generate_diagrams")
    workflow.add_edge("generate_diagrams", "calculate_estimates")
    workflow.add_edge("calculate_estimates", "generate_documents")
    workflow.add_edge("generate_documents", END)

    return workflow.compile()

# Streamlit interface
def main():
    st.title("Project Proposal Generator")

    graph = create_graph()
    state = ProjectState()
    final_state = graph.invoke(state)

    display_results(final_state)

def display_results(state: ProjectState):
    st.header("Generated Proposal")

    st.subheader("Work Breakdown Structure")
    st.text(state.wbs)

    st.subheader("Diagrams")
    for diagram_type, diagram in state.diagrams.items():
        st.markdown(f"### {diagram_type.upper()}")
        st.code(diagram, language="mermaid")

    st.subheader("Estimates")
    st.write("Time Estimates:", state.estimates["time"])
    st.write("Cost Breakdown:", state.estimates["cost"])

    st.subheader("Documents")
    doc_name = generate_proposal_document(state)
    st.success(f"Proposal document generated: {doc_name}")
    st.download_button("Download Proposal", doc_name, file_name=doc_name)

if __name__ == "__main__":
    main()
