import os
import streamlit as st
from datetime import datetime
from groq import Groq 
from io import BytesIO
from fpdf import FPDF 

# Initialize the Groq client using the API key from environment variables
api_key = "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"
client = Groq(api_key=api_key)

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
            model="llama3-8b-8192"  # Specify the model (replace with your desired model)
        )
        return chat_completion.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {str(e)}"

# Generate WBS and Estimation with dynamic complexity adjustment
def generate_wbs_and_estimation(project_name, modules, tech_stack, complexity):
    prompt = f"""
    Project Proposal - {project_name}
    - Features: {modules}
    - Tech Stack: {tech_stack}
    - Complexity: {complexity}
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

# Generate user flow and architecture in Mermaid.js
def generate_diagrams(user_roles):
    flow_prompt = f"Generate a user flow in Mermaid.js for the following roles: {user_roles}"
    dfd_prompt = f"Generate a data flow diagram (DFD) in Mermaid.js for a generic application backend."
    user_flow = groq_response(flow_prompt)
    dfd = groq_response(dfd_prompt)
    return user_flow, dfd

# Generate PDF
def generate_pdf(wbs, user_flow, dfd, save_path=None):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Project Proposal", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(200, 10, txt="Work Breakdown Structure (WBS):", ln=True)
    pdf.multi_cell(0, 10, wbs)
    pdf.ln(10)

    pdf.cell(200, 10, txt="User Flow (Mermaid.js):", ln=True)
    pdf.multi_cell(0, 10, user_flow)
    pdf.ln(10)

    pdf.cell(200, 10, txt="DFD / Backend Architecture (Mermaid.js):", ln=True)
    pdf.multi_cell(0, 10, dfd)

     # Save the PDF locally if save_path is provided
    if save_path:
        pdf.output(save_path)
        print(f"PDF saved to: {save_path}")
    # Create a BytesIO object
    output = BytesIO()
    
    # Write the PDF content to the BytesIO buffer
    pdf.output(dest="S").encode("latin1")  # Ensure proper encoding
    output.seek(0)  # Move the cursor to the beginning of the buffer

    return output.getvalue()  # Return the PDF data as bytes


# Display the full project proposal
def display_project_proposal(project_name, project_overview, modules, tech_stack, user_roles, wbs, user_flow, dfd):
    st.subheader(f"Project Proposal - {project_name}")

    st.markdown("### Project Overview")
    st.write(project_overview)

    st.markdown("### Modules / Features")
    st.write(modules)

    st.markdown("### Tech Stacks")
    st.write(tech_stack)

    st.markdown("### User Roles")
    st.write(user_roles)

    st.markdown("### User Flow (Mermaid.js)")
    st.code(user_flow, language="mermaid")

    st.markdown("### DFD / Backend Architecture (Mermaid.js)")
    st.code(dfd, language="mermaid")

    st.markdown("### Work Breakdown Structure (WBS)")
    st.write(wbs)

    st.markdown(f"**Disclaimer**: This project proposal is valid as of {datetime.now().strftime('%Y-%m-%d')}")

    # Generate the PDF content
    # Provide option to download the proposal as a PDF
    # pdf_data = generate_pdf(wbs, user_flow, dfd)
    # st.download_button("Download Proposal as PDF", pdf_data, "proposal.pdf", mime="application/pdf")


# Streamlit app
def main():
    st.title("Project Proposal Chatbot")

    # Variables to hold results
    proposal_ready = False
    pdf_data = None

    with st.form(key="project_form"):
        project_name = st.text_input("Enter the project title", value="My Project")
        project_overview = st.text_area("Provide the overall project idea")
        modules = st.text_area("List the main modules or features of the application")
        tech_stack = st.text_input("Do you have a preferred tech stack? (Leave blank for suggestions)")
        user_roles = st.text_input("Define the user roles (e.g., Admin, User)")

        complexity = st.selectbox("Select project complexity", ["Low", "Medium", "High"])

        # Ensure required fields are filled
        if not project_name or not modules:
            st.error("Project name and modules are required fields!")

        # Submit Button
        submitted = st.form_submit_button("Generate Proposal")

        if submitted:
            st.info("Generating proposal... This may take a moment.")
            # Generate WBS and diagrams
            wbs = generate_wbs_and_estimation(
                project_name,
                modules,
                tech_stack or "Tech stack not specified; recommend.",
                complexity
            )
            user_flow, dfd = generate_diagrams(user_roles)

            # Display the project proposal
            display_project_proposal(
                project_name,
                project_overview,
                modules,
                tech_stack,
                user_roles,
                wbs,
                user_flow,
                dfd
            )

            # Generate the PDF content
            pdf_data = generate_pdf(wbs, user_flow, dfd)

            # Save the PDF to disk
            with open("proposal.pdf", "wb") as f:
                f.write(pdf_data)

            st.success("PDF saved to disk as 'proposal.pdf'.")
            proposal_ready = True

        # Place the download button outside the form
        if proposal_ready and pdf_data:
            st.download_button(
                "Download Proposal as PDF",
                pdf_data,
                "proposal.pdf",
                mime="application/pdf"
            )


if __name__ == "__main__":
    main()
