# SampleWebAppWithDatabase - Streamlit Cloud Deployment

## Cloud services used
- SaaS: Jupyter/Colab, GitHub
- PaaS-like: Streamlit Community Cloud
- DBaaS: Neon Postgres

## Deploy steps (students)
1. Create a GitHub repo and upload:
   - app.py
   - db.py
   - requirements.txt
   - .gitignore
   - README.md
2. Streamlit Community Cloud -> New app
   - select repo + branch
   - main file: app.py
3. Streamlit Cloud -> App Settings -> Secrets:
   NEON_DATABASE_URL="postgresql://... ?sslmode=require"
4. Test: submit form -> record appears in table.

## Local run (optional)
pip install -r requirements.txt
export NEON_DATABASE_URL="postgresql://... ?sslmode=require"
streamlit run app.py
