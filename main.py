import os
import random
import streamlit as st
from datetime import datetime
from mermaid import Mermaid
from groq import Groq

# Initialize the Groq client using the API key
api_key = "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"
if not api_key:
    raise ValueError("API key is missing")
client = Groq(api_key=api_key)

# Function to interact with Groq API
def groq_response(prompt):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a project proposal assistant chatbot."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-8b-8192"  # Specify the model
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Function to render Mermaid diagrams using mermaid-py
def render_with_mermaid_py(diagram_code):
    try:
        diagram = Mermaid(diagram_code)
        diagram_html = diagram.script  # This will fetch the diagram HTML code
        st.markdown(f"<div>{diagram_html}</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error rendering Mermaid diagram: {str(e)}")

# Generate WBS and Estimation with dynamic complexity adjustment
def generate_wbs_and_estimation(project_name, modules, tech_stack, complexity, overlap, roadmap_basis):
    prompt = f"""
    Project Proposal - {project_name}
    - Features: {modules}
    - Tech Stack: {tech_stack}
    - Complexity: {complexity}
    - Overlap: {overlap}
    - Roadmap Basis: {roadmap_basis}
    Based on this, provide a detailed Work Breakdown Structure (WBS) including estimations for:
    - UI/UX Design
    - Frontend Development
    - Backend Development
    - Machine Learning (if applicable)
    - API Integration
    - QA and Testing
    - Deployment
    """
    return groq_response(prompt)

# Generate diagrams dynamically
def generate_diagrams(user_roles):
    dfd_prompt = f"Generate a data flow diagram (DFD) in Mermaid.js for a system with these user roles: {user_roles}."
    erd_prompt = f"Generate an entity relationship diagram (ERD) in Mermaid.js for a system with these user roles: {user_roles}."
    
    user_flow = groq_response(f"Generate a user flow in Mermaid.js for the following roles: {user_roles}")
    dfd = groq_response(dfd_prompt)
    erd = groq_response(erd_prompt)
    
    return user_flow, dfd, erd

# Display the full project proposal
def display_project_proposal(project_name, project_overview, modules, tech_stack, user_roles, wbs, user_flow, dfd, erd):
    st.markdown(f"### Title: {project_name}")
    st.markdown(f"### Date: {datetime.now().strftime('%Y-%m-%d')}")
    st.markdown("### Reviewer: Mr. Aqib")

    st.markdown("### Project Overview")
    st.write(project_overview)

    st.markdown("### Modules / Features")
    st.write(modules)

    st.markdown("### Tech Stacks")
    st.write(tech_stack)

    st.markdown("### User Roles")
    st.write(user_roles)

    st.markdown("### User Flow Diagram")
    render_with_mermaid_py(user_flow)

    st.markdown("### Data Flow Diagram (DFD)")
    render_with_mermaid_py(dfd)

    st.markdown("### Entity Relationship Diagram (ERD)")
    render_with_mermaid_py(erd)

    st.markdown("### Work Breakdown Structure (WBS)")
    st.write(wbs)

# Streamlit app
def main():
    st.title("Project Proposal Chatbot")

    with st.form(key="project_form"):
        project_name = st.text_input("Enter the project title", value="My Project")
        project_overview = st.text_area("Provide the overall project idea")
        modules = st.text_area("List the main modules or features of the application")
        tech_stack = st.text_input("Do you have a preferred tech stack? (Leave blank for suggestions)")
        user_roles = st.text_input("Define the user roles (e.g., Admin, User)")

        design = st.radio("Do you have the design?", ("Yes", "No"))
        overlap = None
        if design == "Yes":
            overlap = st.radio("Do you want FE/BE overlap?", ("Yes", "No"))

        roadmap = st.radio("Do you need the Roadmap?", ("Yes", "No"))
        roadmap_basis = None
        if roadmap == "Yes":
            roadmap_basis = st.radio("Specify the roadmap basis", ("Week-based", "Month-based"))
        else:
            roadmap_basis = "No roadmap"

        complexity = st.selectbox("Select project complexity", ["Low", "Medium", "High"])

        # Submit Button
        submitted = st.form_submit_button("Generate Proposal")

        if submitted:
            st.info("Generating proposal... This may take a moment.")

            # Generate WBS and diagrams
            wbs = generate_wbs_and_estimation(
                project_name,
                modules,
                tech_stack or "Tech stack not specified; recommend.",
                complexity,
                overlap if overlap else "No FE/BE overlap",
                roadmap_basis
            )
            user_flow, dfd, erd = generate_diagrams(user_roles)

            # Display the project proposal
            display_project_proposal(
                project_name,
                project_overview,
                modules,
                tech_stack,
                user_roles,
                wbs,
                user_flow,
                dfd,
                erd
            )

if __name__ == "__main__":
    main()
