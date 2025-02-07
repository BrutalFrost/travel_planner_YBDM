import sys
from pathlib import Path

# import matplotlib.image as mpimg
# import matplotlib.pyplot as plt
# mport pandas as pd
import streamlit as st
from PIL import Image

sys.path.append(str(Path(__file__).parents[1]))


def layout():
    # inset start

    st.set_page_config(page_title="This is a Multipage WebApp")
    st.sidebar.success("WHat do you want to do")
    # inset stop
    st.markdown("# The magic travel agent")

    st.markdown("")

    img_path = Path(__file__).parents[0] / "Page1figure.jpeg"

    img = Image.open(img_path)
    st.image(img, caption="Traveling by YHDM")
    st.markdown("This is an example of the traveling agent ...")

    read_css()


def read_css():
    css_path = Path(__file__).parents[0] / "style.css"

    with open(css_path) as css:
        st.markdown(
            f"<style>{css.read()}</style>",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    layout()
