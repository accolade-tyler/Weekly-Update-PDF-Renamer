import streamlit as st
import os
import re
import tempfile
import zipfile
import io

# -----------------------------------
# CLIENT LIST
# -----------------------------------
CLIENT_LIST = [
    "1st Mississippi FCU", "Abbey CU", "Achieve CU", "Advantage CU", "Ashland CU",
    "Bayer Heritage FCU", "Best Reward FCU", "Buckeye State CU", "Christian Family CU",
    "Cincinnati Ohio Police FCU", "Coastline FCU", "DESCO FCU", "Education CU",
    "Emerald CU", "Expree CU", "Firefighters & Company FCU", "Gulf Coast Community FCU",
    "LCE FCU", "Medina County FCU", "Members Exchange FCU", "MyUSA CU", "Navigator FCU",
    "NuVista FCU", "Ohio Valley Community FCU", "Pathways Financial CU",
    "Perfect Circle CU", "PSE CU", "Quest FCU", "Sharefax CU", "Singing River FCU",
    "Sno Falls CU", "Sunbelt FCU", "Telhio CU", "The Ohio Education CU", "Towpath CU",
    "Triangle FCU", "UNO FCU", "Wayne County Community FCU", "Yolo FCU"
]

# -----------------------------------
# RENAME LOGIC
# -----------------------------------
def rename_uploaded_files(uploaded_files, date_tag=""):
    results = []
    temp_dir = tempfile.mkdtemp()  # Temporary folder to save uploaded files

    # Save uploaded files to temp_dir
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    # Rename files based on CLIENT_LIST
    for file_name in sorted(os.listdir(temp_dir)):
        file_path = os.path.join(temp_dir, file_name)

        match = re.search(r'(\d+)', file_name)
        if not match:
            results.append(f"⚠️ No number found in: {file_name}")
            continue

        file_number = int(match.group(1))
        if not (1 <= file_number <= len(CLIENT_LIST)):
            results.append(f"⚠️ Number {file_number} out of range: {file_name}")
            continue

        client_name = CLIENT_LIST[file_number - 1]
        ext = os.path.splitext(file_name)[1]
        new_name = f"{client_name}{date_tag}{ext}"
        new_path = os.path.join(temp_dir, new_name)

        os.rename(file_path, new_path)
        results.append(f"✅ {file_name} → {new_name}")

    # Create a ZIP of renamed files for download
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for f in os.listdir(temp_dir):
            zipf.write(os.path.join(temp_dir, f), arcname=f)
    zip_buffer.seek(0)

    return results, zip_buffer


# -----------------------------------
# STREAMLIT UI
# -----------------------------------
st.title("Weekly Update PDF Namer")

st.write("""
### How to Use
1. Select all PDFs to upload  
2. Optional: Enter a tag to append to each filename  
3. Click "Rename and Download" and scroll to the bottom
""")

uploaded_files = st.file_uploader(
    "Upload PDFs (multiple allowed)",
    type=["pdf"],
    accept_multiple_files=True
)

date_tag = st.text_input("Optional Tag (e.g., _2025_11_21)", value="")

if uploaded_files:
    if st.button("🔄 Rename Files"):
        try:
            results, zip_buffer = rename_uploaded_files(uploaded_files, date_tag)

            st.write("### Renaming Results")
            for r in results:
                st.write(r)

            st.download_button(
                label="⬇️ Download Renamed PDFs",
                data=zip_buffer,
                file_name="renamed_pdfs.zip",
                mime="application/zip"
            )

            st.success("All files renamed and ready to download!")

        except Exception as e:
            st.error(f"Error: {e}")

