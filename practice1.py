import gradio as gr
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader

# ----------- LLM Model -----------
llm = ChatOllama(model="phi")   # ya "llama3", "mistral" agar installed hai

# ----------- Prompt Template -----------
prompt = ChatPromptTemplate.from_template("""
You are an expert CV reviewer.

CV:
{cv}

Job Description:
{jd}

Please do the following:
1. Give a score (0-100) for how well the CV matches the Job Description.
2. List missing or weak skills.
3. Suggest improvements to make the CV stronger and more ATS friendly.
""")

chain = prompt | llm

# ----------- CV Review Function -----------
def review_cv(pdf_file, job_desc):
    try:
        # Load CV PDF
        loader = PyPDFLoader(pdf_file.name)
        cv_docs = loader.load()
        cv_text = " ".join([doc.page_content for doc in cv_docs])

        # Run chain
        result = chain.invoke({"cv": cv_text, "jd": job_desc})

        return result.content
    except Exception as e:
        return f" Error: {str(e)}"

# ----------- Gradio UI -----------
with gr.Blocks() as demo:
    gr.Markdown("# 📄 AI CV Reviewer (LangChain + Ollama)")
    gr.Markdown("Upload your CV and paste a job description to get an AI-powered review.")

    with gr.Row():
        pdf_input = gr.File(label="Upload your CV (PDF)", file_types=[".pdf"])
        job_input = gr.Textbox(label="Paste Job Description", lines=8, placeholder="Enter job description here...")

    output = gr.Textbox(label="CV Review Result", lines=15)

    review_btn = gr.Button("🚀 Review CV")
    review_btn.click(review_cv, inputs=[pdf_input, job_input], outputs=output)

# ----------- Launch App -----------
if __name__ == "__main__":
    demo.launch()