import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import re

# Set page config
st.set_page_config(page_title="Marathi Word Chain Visualizer", layout="wide")

st.title("📖 Marathi Word Chain Visualizer")

# Ensure pytesseract knows where Tesseract is installed (optional if OCR is used later)
# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# Validate image directory
def validate_images_path(path):
    if not os.path.exists(path):
        st.error(f"The directory '{C:\Users\acer\OneDrive\Desktop\MINIPROJ\miniproj-20250323T045140Z-001.zip' does not exist.")
        return None
    if not any(os.scandir(path)):
        st.error(f"The directory '{C:\Users\acer\OneDrive\Desktop\MINIPROJ\miniproj-20250323T045140Z-001.zip}' is empty.")
        return None
    return path

# Find and process word chains
def find_word_chains(input_text, images_path):
    matched_results = []
    processed_indices = set()
    words = re.split(r'\s+', input_text.strip())
    total_words = len(words)

    for start in range(total_words):
        for end in range(total_words, start, -1):
            phrase = ' '.join(words[start:end]).strip()

            if any(i in processed_indices for i in range(start, end)):
                continue

            matched = False
            for root, dirs, files in os.walk(images_path):
                for file in files:
                    if phrase == os.path.splitext(file)[0]:
                        img_path = os.path.join(root, file)
                        matched_results.append((Image.open(img_path), phrase))
                        processed_indices.update(range(start, end))
                        matched = True
                        break
                if matched:
                    break

            if matched:
                break

    for i, word in enumerate(words):
        if i not in processed_indices:
            matched_results.append((None, word))
    return matched_results

# Display images with Marathi titles
def display_images_with_marathi(images, titles, font_path):
    if not os.path.exists(font_path):
        st.error(f"Font file not found at {font_path}. Please upload a valid .ttf font.")
        return

    try:
        font = ImageFont.truetype(font_path, size=20)
    except Exception as e:
        st.error(f"Failed to load font: {e}")
        return

    cols = st.columns(len(images))
    for col, img, title in zip(cols, images, titles):
        if img:
            draw = ImageDraw.Draw(img)
            text_bbox = draw.textbbox((0, 0), title, font=font)
            text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
            text_position = ((img.width - text_width) // 2, img.height - text_height - 10)
            draw.text(text_position, title, fill="black", font=font, stroke_width=1, stroke_fill="black")
            col.image(img.resize((300, 300)), caption=title)
        else:
            col.markdown(f"**{title}**")
            col.write("❌ Image not found")

# Upload section
st.sidebar.header("Upload Resources")
images_dir = st.sidebar.text_input("Enter image directory path:")
font_file = st.sidebar.file_uploader("Upload Marathi-compatible .ttf font", type=["ttf"])

# User input
user_input = st.text_input("Enter text (single word, phrase, or sentence):")

# Process when everything is ready
if st.button("Process"):
    if not images_dir or not font_file or not user_input:
        st.warning("Please provide all inputs (image path, font file, and text).")
    else:
        valid_path = validate_images_path(images_dir)
        if valid_path:
            # Save uploaded font temporarily
            temp_font_path = os.path.join("temp_font.ttf")
            with open(temp_font_path, "wb") as f:
                f.write(font_file.read())

            matches = find_word_chains(user_input, valid_path)
            if matches:
                images, titles = zip(*matches)
                pil_images = [img.resize((300, 300)) if img else None for img in images]
                display_images_with_marathi(pil_images, titles, temp_font_path)
            else:
                st.info("No matches found for the given input.")
