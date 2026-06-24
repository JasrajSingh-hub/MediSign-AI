import os
from PIL import Image, ImageDraw, ImageFont

def create_prescription():
    # Create a white canvas (800x1000)
    img = Image.new("RGB", (800, 1000), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Try to load standard windows system fonts, fallback if not found
    try:
        font = ImageFont.truetype("arial.ttf", 22)
        title_font = ImageFont.truetype("arial.ttf", 32)
        bold_font = ImageFont.truetype("arial.ttf", 26)
    except IOError:
        font = ImageFont.load_default()
        title_font = font
        bold_font = font

    # Define standard lines of text with coordinates to simulate a printed prescription
    lines = [
        ("City General Hospital", title_font, 40),
        ("Dr. Rajesh Kumar, MD", bold_font, 90),
        ("Reg No: 12345", font, 130),
        ("-" * 60, font, 170),
        ("Patient Name: Amit Sharma", bold_font, 210),
        ("Age: 35 Yrs    Gender: Male", font, 250),
        ("Date: 24/06/2026", font, 290),
        ("-" * 60, font, 330),
        ("Rx:", bold_font, 380),
        ("1. Paracetamol 500mg TDS for 5 days (after food)", font, 430),
        ("2. Amoxicillin 250 mg twice daily for 7 days", font, 480),
        ("3. Ibuprofen 400mg when required", font, 530),
        ("-" * 60, font, 600),
        ("Please follow instructions carefully.", font, 650),
    ]
    
    for text, f, y in lines:
        draw.text((60, y), text, fill=(0, 0, 0), font=f)
        
    output_path = "sample_prescription.png"
    img.save(output_path)
    print(f"Created {output_path} successfully in workspace root.")

if __name__ == "__main__":
    create_prescription()
