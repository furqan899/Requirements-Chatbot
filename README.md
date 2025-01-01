---

# Project Proposal Chatbot

This project is a **Project Proposal Chatbot** that helps generate detailed project proposals. It allows users to input details about their projects and provides structured outputs, including Work Breakdown Structure (WBS), tech stack recommendations, user flows, and estimated costs. The application also supports file uploads (PDF and DOCX) to extract project details automatically and can generate a downloadable project proposal in DOCX format.

### Features

- **Project Overview**: Provides an overall description of the project.
- **Modules/Features**: Defines the main features or modules of the application.
- **Tech Stack**: Suggests a tech stack or allows users to specify their preferred stack.
- **User Roles**: Defines the user roles (e.g., Admin, User).
- **Roadmap**: Option to generate a roadmap based on user preferences (week-based or month-based).
- **Work Breakdown Structure (WBS)**: Generates a detailed WBS for the project.
- **Diagrams**: Generates user flow, data flow diagram (DFD), and entity relationship diagram (ERD) based on the provided user roles.
- **Cost Estimation**: Estimates project costs based on the WBS and complexity.
- **File Uploads**: Supports file uploads (PDF, DOCX) to extract project requirements and auto-fill project details.
- **DOCX Download**: Allows users to download the generated project proposal as a DOCX file.

### Technologies Used

- **Streamlit**: For building the interactive web application.
- **Groq**: For generating content using AI models.
- **Python-docx**: For creating and manipulating Word documents.
- **PyPDF2**: For extracting text from PDF files.

### Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/your-username/project-proposal-chatbot.git
   ```

2. Navigate to the project folder:

   ```bash
   cd project-proposal-chatbot
   ```

3. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:
   - **Windows**: 
     ```bash
     venv\Scripts\activate
     ```
   - **Mac/Linux**: 
     ```bash
     source venv/bin/activate
     ```

5. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Run the Streamlit app:

   ```bash
   streamlit run app.py
   ```

   This will open the application in your browser.

### How to Use

1. **Enter Project Details**:
   - Fill in the project title, description, modules/features, tech stack, user roles, and complexity.
   - Optionally upload a project requirement file (PDF or DOCX).
   
2. **Generate Proposal**:
   - Click the "Generate Proposal" button to generate the project proposal. The application will display the project overview, modules, tech stacks, user roles, user flows, backend architecture diagrams, WBS, and cost estimation.

3. **Download Proposal**:
   - After the proposal is generated, you will see a "Download Proposal as DOCX" button. Click it to download the generated proposal as a Word document.

### Files Supported for Upload

- **PDF**: Project requirement documents in PDF format.
- **DOCX**: Project requirement documents in DOCX format.

### Example Output

Once the proposal is generated, the output will include:
- Project Overview
- Modules/Features
- Tech Stacks
- User Roles
- User Flow Diagram (in Mermaid.js format)
- DFD (Data Flow Diagram)
- ERD (Entity Relationship Diagram)
- Work Breakdown Structure (WBS)
- Cost Estimation

### Future Enhancements

- Add more advanced cost estimation models.
- Integrate with external APIs to fetch tech stack recommendations.
- Add project timeline management tools.

### Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Make your changes and commit them (`git commit -am 'Add feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Create a new Pull Request.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
