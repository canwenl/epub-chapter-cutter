import streamlit as st
from pathlib import Path
import tempfile, shutil, zipfile
from ebooklib import epub, ITEM_DOCUMENT
from markdownify import markdownify as md


def export_chapters_to_dir(epub_bytes: bytes, out_dir: Path):
    """Convert an EPUB (in-memory bytes) to per‑chapter Markdown files."""
    # Write bytes to a temp file because EbookLib expects a path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".epub") as tmp:
        tmp.write(epub_bytes)
        tmp.flush()
        book = epub.read_epub(tmp.name)

    for idx, item in enumerate(book.get_items_of_type(ITEM_DOCUMENT), start=1):
        title = Path(item.get_name()).stem or f"chapter_{idx:03}"
        md_text = md(
            item.get_content().decode("utf-8"), heading_style="ATX"
        )
        (out_dir / f"{idx:02}_{title}.md").write_text(md_text, encoding="utf-8")


st.set_page_config(page_title="EPUB Chapter Cutter", page_icon="📖")

st.title("📖 EPUB Chapter Cutter")
st.write(
    "Upload an **EPUB** file and download all chapters as a **ZIP** of Markdown files.\n"
)

uploaded_file = st.file_uploader("Choose an EPUB file", type=["epub"])

if uploaded_file:
    if st.button("Convert"):
        with st.spinner("Processing chapters …"):
            with tempfile.TemporaryDirectory() as temp_dir:
                out_dir = Path(temp_dir) / "chapters"
                out_dir.mkdir()

                # 1️⃣ 章节拆分
                export_chapters_to_dir(uploaded_file.read(), out_dir)

                # 2️⃣ 打包 ZIP 以供下载
                zip_path = (
                    Path(temp_dir)
                    / f"{Path(uploaded_file.name).stem}_md.zip"
                )
                shutil.make_archive(zip_path.with_suffix("").as_posix(), "zip", out_dir)

                # 3️⃣ 输出下载按钮
                with open(zip_path, "rb") as f:
                    st.download_button(
                        label="⬇️  Download Markdown ZIP",
                        data=f,
                        file_name=zip_path.name,
                        mime="application/zip",
                    )
        st.success("Done! Click the button above to download.")

st.markdown("---")
st.caption("Built with Streamlit · EbookLib · markdownify")
