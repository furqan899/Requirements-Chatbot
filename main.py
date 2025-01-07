import os
import random
import streamlit as st
from datetime import datetime, timedelta
from docx import Document
from PyPDF2 import PdfReader
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI API
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key is missing. Set OPENAI_API_KEY environment variable.")
openai.api_key = api_key

def openai_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a project proposal assistant chatbot specialized in creating detailed technical documentation and Mermaid.js diagrams."},
                {"role": "user", "content": prompt}
            ]
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {str(e)}"

def generate_time_estimation_table(wbs, complexity):
    phases = {
        'UI/UX': {'Low': 2, 'Medium': 3, 'High': 4},
        'Frontend': {'Low': 4, 'Medium': 6, 'High': 8},
        'Backend': {'Low': 4, 'Medium': 6, 'High': 8},
        'API Integration': {'Low': 2, 'Medium': 3, 'High': 4},
        'Testing': {'Low': 2, 'Medium': 3, 'High': 4},
        'Deployment': {'Low': 1, 'Medium': 2, 'High': 3}
    }
    estimates = {phase: timing[complexity] for phase, timing in phases.items()}
    total_weeks = sum(estimates.values())
    estimates['Total'] = total_weeks
    return estimates

def generate_detailed_cost_breakdown(wbs, complexity):
    base_rates = {
        'UI/UX': 80,
        'Frontend': 100,
        'Backend': 120,
        'API Integration': 90,
        'Testing': 70,
        'Deployment': 85
    }
    
    multipliers = {'Low': 1, 'Medium': 1.25, 'High': 1.5}
    time_estimates = generate_time_estimation_table(wbs, complexity)
    
    breakdown = {}
    for phase in base_rates:
        if phase != 'Total':
            weeks = time_estimates[phase]
            rate = base_rates[phase] * multipliers[complexity]
            breakdown[phase] = {
                'Weeks': weeks,
                'Rate/Hour': rate,
                'Total Cost': weeks * 40 * rate  # 40 hours per week
            }
    
    return breakdown

def generate_wbs_and_estimation(project_name, modules, tech_stack, complexity, overlap, roadmap_basis):
    prompt = f"""
    Project Proposal - {project_name}
    - Features: {modules}
    - Tech Stack: {tech_stack}
    - Complexity: {complexity}
    - Overlap: {overlap}
    - Roadmap Basis: {roadmap_basis}
    Create a detailed Work Breakdown Structure (WBS) including phases and tasks for:
    - UI/UX Design
    - Frontend Development
    - Backend Development
    - API Integration
    - QA and Testing
    - Deployment
    Format as a structured list with main phases and sub-tasks.
    """
    return openai_response(prompt)

def generate_diagrams(user_roles, role_actions, role_data_flows, role_entities):
    # Dynamically generate user flow based on user roles and actions
    user_flow = "flowchart TD\n"
    for role, actions in role_actions.items():
        user_flow += f"  {role} -->|{', '.join(actions)}| {role}Actions[Actions of {role}]\n"

    # Dynamically generate data flow diagram (DFD) based on role data flows
    dfd = "flowchart TD\n"
    for role, flows in role_data_flows.items():
        for flow in flows:
            dfd += f"  {role} -->|{flow['action']}| {flow['process']}\n"
            dfd += f"  {flow['process']} -->|{flow['data']}| {flow['data_store']}\n"

    # Dynamically generate entity relationship diagram (ERD) based on role entities
    erd = "erDiagram\n"
    for entity, relationships in role_entities.items():
        erd += f"  {entity} {{\n"
        for attribute in relationships['attributes']:
            erd += f"    {attribute}\n"
        erd += "  }\n"
        for relation in relationships['relations']:
            erd += f"  {entity} ||--o{{ {relation['related_entity']} }} : {relation['relation_type']}\n"

    return user_flow, dfd, erd

# Example of dynamic input
user_roles = ['Admin', 'User', 'Manager']
role_actions = {
    'Admin': ['Create User', 'Edit User', 'Delete User'],
    'User': ['View Profile', 'Update Profile'],
    'Manager': ['Approve Requests', 'View Reports']
}

role_data_flows = {
    'Admin': [
        {'action': 'Manage Users', 'process': 'User Management', 'data': 'User Info', 'data_store': 'User DB'},
        {'action': 'Edit Settings', 'process': 'Settings Process', 'data': 'Settings Data', 'data_store': 'Settings DB'}
    ],
    'User': [
        {'action': 'Edit Profile', 'process': 'Profile Edit', 'data': 'Profile Data', 'data_store': 'Profile DB'}
    ]
}

role_entities = {
    'USER': {
        'attributes': ['string id', 'string name', 'string email'],
        'relations': [
            {'related_entity': 'ORDER', 'relation_type': 'places'}
        ]
    },
    'ORDER': {
        'attributes': ['string orderId', 'string orderDate'],
        'relations': [
            {'related_entity': 'ORDER_ITEMS', 'relation_type': 'contains'}
        ]
    }
}

# Generate dynamic diagrams
user_flow, dfd, erd = generate_diagrams(user_roles, role_actions, role_data_flows, role_entities)
print("User Flow:", user_flow)
print("DFD:", dfd)
print("ERD:", erd)


def generate_role_flow_table(user_roles):
    prompt = f"""Create a detailed table mapping for these user roles: {user_roles}.
    Include:
    1. Role name
    2. Primary responsibilities
    3. Key user stories
    4. Use cases
    5. Access levels
    Format as a markdown table with clear headers and detailed entries."""
    return openai_response(prompt)

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return "\n".join(page.extract_text() for page in PdfReader(uploaded_file).pages)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        return "\n".join(para.text for para in doc.paragraphs)
    return None

def save_to_word(project_name, project_overview, modules, tech_stack, user_roles, wbs, user_flow, dfd, erd, cost_breakdown, role_flow, time_estimates):
    doc = Document()
    doc.add_heading(f'Project Proposal: {project_name}', 0)
    
    sections = {
        'Project Overview': project_overview,
        'Modules / Features': modules,
        'Tech Stacks': tech_stack,
        'User Roles': user_roles,
        'Role-Based Flow Table': role_flow,
        'User Flow Diagram': user_flow,
        'Data Flow Diagram': dfd,
        'Entity Relationship Diagram': erd,
        'Work Breakdown Structure': wbs
    }
    
    for title, content in sections.items():
        doc.add_heading(title, level=1)
        doc.add_paragraph(content)

    # Add Time Estimates Table
    doc.add_heading('Time Estimates', level=1)
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Table Grid'
    table.rows[0].cells[0].text = 'Phase'
    table.rows[0].cells[1].text = 'Weeks'
    
    for phase, weeks in time_estimates.items():
        row = table.add_row()
        row.cells[0].text = phase
        row.cells[1].text = str(weeks)

    # Add Cost Breakdown
    doc.add_heading('Cost Breakdown', level=1)
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    headers = ['Phase', 'Weeks', 'Rate/Hour', 'Total Cost']
    for i, header in enumerate(headers):
        table.rows[0].cells[i].text = header
    
    for phase, details in cost_breakdown.items():
        row = table.add_row()
        row.cells[0].text = phase
        row.cells[1].text = str(details['Weeks'])
        row.cells[2].text = f"${details['Rate/Hour']}"
        row.cells[3].text = f"${details['Total Cost']:,.2f}"

    # Add Validity Disclaimer
    validity_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    doc.add_paragraph(f"\nThis proposal is valid until {validity_date}")
    
    file_path = f"{project_name}_Proposal_{datetime.now().strftime('%Y%m%d%H%M%S')}.docx"
    doc.save(file_path)
    return file_path

def display_project_proposal(project_name, project_overview, modules, tech_stack, user_roles, wbs, user_flow, dfd, erd, cost_breakdown, role_flow, time_estimates):
    st.markdown(f"### {project_name} - Project Proposal")
    st.markdown(f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
    
    sections = {
        'Project Overview': project_overview,
        'Modules / Features': modules,
        'Tech Stacks': tech_stack,
        'User Roles': user_roles,
        'Role-Based Flow Table': role_flow
    }
    
    for title, content in sections.items():
        st.markdown(f"### {title}")
        st.write(content)

    st.markdown("### User Flow")
    st.code(user_flow, language="mermaid")
    
    st.markdown("### Data Flow Diagram")
    st.code(dfd, language="mermaid")
    
    st.markdown("### Entity Relationship Diagram")
    st.code(erd, language="mermaid")
    
    st.markdown("### Work Breakdown Structure")
    st.write(wbs)
    
    st.markdown("### Time Estimates")
    st.table(time_estimates)
    
    st.markdown("### Cost Breakdown")
    st.table(cost_breakdown)
    
    word_file_path = save_to_word(project_name, project_overview, modules, tech_stack, user_roles, wbs, user_flow, dfd, erd, cost_breakdown, role_flow, time_estimates)
    
    with open(word_file_path, "rb") as f:
        st.download_button(
            label="Download Full Proposal",
            data=f,
            file_name=word_file_path,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

def main():
    st.title("Project Proposal Generator")
    
    with st.form("project_form"):
        project_name = st.text_input("Project Title", "My Project")
        project_overview = st.text_area("Project Overview")
        modules = st.text_area("Main Modules/Features")
        tech_stack = st.text_input("Preferred Tech Stack (optional)")
        user_roles = st.text_input("User Roles (comma-separated)")
        
        col1, col2 = st.columns(2)
        with col1:
            design = st.radio("Have Design?", ("Yes", "No"))
            overlap = st.radio("FE/BE Overlap?", ("Yes", "No")) if design == "Yes" else "No"
        
        with col2:
            roadmap = st.radio("Need Roadmap?", ("Yes", "No"))
            roadmap_basis = st.radio("Roadmap Basis", ("Week-based", "Month-based")) if roadmap == "Yes" else "No roadmap"
        
        complexity = st.selectbox("Project Complexity", ["Low", "Medium", "High"])
        uploaded_file = st.file_uploader("Upload Requirements (PDF/DOC)", type=["pdf", "docx"])
        
        if uploaded_file:
            extracted_text = extract_text_from_file(uploaded_file)
            if extracted_text:
                st.text_area("Extracted Content", extracted_text, height=200)
        
        submitted = st.form_submit_button("Generate Proposal")
        
        if submitted:
            if not all([project_name, project_overview, modules, user_roles]):
                st.error("Please fill in all required fields!")
                return
            
            with st.spinner("Generating proposal..."):
                wbs = generate_wbs_and_estimation(project_name, modules, tech_stack, complexity, overlap, roadmap_basis)
                user_flow, dfd, erd = generate_diagrams(user_roles, role_actions, role_data_flows, role_entities)
                role_flow = generate_role_flow_table(user_roles)
                time_estimates = generate_time_estimation_table(wbs, complexity)
                cost_breakdown = generate_detailed_cost_breakdown(wbs, complexity)
                
                display_project_proposal(
                    project_name, project_overview, modules, tech_stack,
                    user_roles, wbs, user_flow, dfd, erd,
                    cost_breakdown, role_flow, time_estimates
                )

if __name__ == "__main__":
    main()