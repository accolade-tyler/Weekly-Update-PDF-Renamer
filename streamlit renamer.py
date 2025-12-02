import streamlit as st
import zipfile
import tempfile
import os
import re
import io

# -----------------------------------
# CLIENT LIST
# -----------------------------------
CLIENT_LIST = [
    "1st Mississippi FCU", "Abbey CU", "Achieve CU", "Advantage CU", "Ashland CU",
    "Bayer Heritage FCU", "Best Reward CU", "Buckeye State CU", "Christian Family CU",
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
def rename_files(folder_path, date_tag=""):
    results = []
    files = sorted(os.listdir(folder_path))

    for file_name in files:
        file_path = os.path.join(folder_path, file_name)

        if not os.path.isfile(file_path):
            continue

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

        os.rename(file_path, os.path.join(folder_path, new_name))
        results.append(f"✅ {file_name} → {new_name}")

    return results

# -----------------------------------
# STREAMLIT UI
# -----------------------------------
st.title("📁 PDF Renamer — Upload ZIP ➜ Download Renamed ZIP")

st.write("""
### How to Use:
1. Zip the PDFs you want renamed  
2. Upload the ZIP file  
3. Click *Rename*  
4. Download the renamed PDFs as a new ZIP  
""")

zip_file = st.file_uploader("Upload ZIP containing only PDFs", type=["zip"])
date_tag = st.text_input("Optional Date Tag (ex: _2025_11_21)", value="")

if zip_file:
    # Create temp directory
    temp_dir = tempfile.mkdtemp()

    # Extract PDFs into temp folder
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    folder_path = temp_dir
    st.success("ZIP extracted successfully!")

    st.write("### Files Detected:")
    st.write(os.listdir(folder_path))

    if st.button("🔄 Rename PDFs"):
        try:
            results = rename_files(folder_path, date_tag)

            st.write("### Renaming Results")
            for r in results:
                st.write(r)

            st.success("Renaming complete! You can now download the converted folder.")

            # Create ZIP in memory
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_name in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file_name)
                    zipf.write(file_path, arcname=file_name)
            buffer.seek(0)

            # Provide download button
            st.download_button(
                label="⬇️ Download Renamed ZIP",
                data=buffer,
                file_name="renamed_pdfs.zip",
                mime="application/zip"
            )

        except Exception as e:
            st.error(f"Error: {e}")
