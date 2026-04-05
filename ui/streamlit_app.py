import streamlit as st
import requests
import pandas as pd
import os

# Backend FastAPI URL
# http://localhost:8000
# On Streamlit Cloud, set API_URL in the app's environment
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("Agentic Search")

query = st.text_input("Topic query") #, "AI startups in healthcare")

if st.button("Search") and query:
    try:
        resp = requests.get(
            f"{API_URL}/search",
            params={"q": query},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        st.error(f"Backend error: {exc}")
    else:
        rows = []
        for item in data.get("results", []):
            provenance = item.get("provenance", [])
            first_prov = provenance[0] if provenance else {}
            rows.append({
                "Entity": item.get("entity_name", ""),
                "Type": item.get("entity_type", ""),
                "Attributes": item.get("attributes", {}),
                "Source URL": first_prov.get("source_url", ""),
                "Evidence": first_prov.get("evidence_text", ""),
                "Confidence": first_prov.get("confidence", None),
            })

        st.subheader("Results table")
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)
        else:
            st.write("No entities extracted.")

        st.subheader("Raw JSON response")
        st.json(data)
else:
    st.info("Enter a query and click Search to run the pipeline.")