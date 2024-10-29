from flask import Flask, request, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

app = Flask(__name__)
CORS(app)

# Function for cropping the avatar image to a circle
def crop_to_circle(input_image, diameter=320):
    # Open the input image and convert it to RGBA
    img = Image.open(input_image).convert("RGBA")
    
    # Create a new image with transparent background for the circle
    circle_image = Image.new("RGBA", (diameter, diameter), (255, 255, 255, 0))
    
    # Create a mask for the circular area
    mask = Image.new("L", (diameter, diameter), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((5, 5, diameter-5, diameter-5), fill=255)  # Slight padding for a smoother edge

    # Apply a Gaussian blur for smoother edges
    mask = mask.filter(ImageFilter.GaussianBlur(2))

    # Resize the original image with high-quality resampling
    img = img.resize((diameter, diameter), Image.LANCZOS)
    
    # Paste the resized image onto the circular image using the mask
    circle_image.paste(img, (0, 0), mask)
    
    return circle_image
@app.route('/api/endpoint', methods=['POST'])
def process_image():
    if 'avatar' not in request.files or not all(key in request.form for key in ['ten', 'xungHo', 'chucVu', 'longText']):
        return "Missing data", 400
    
    # Retrieve the form data
    avatar = request.files['avatar']
    ten = request.form['ten']
    xungHo = request.form['xungHo']
    chucVu = request.form['chucVu']
    longText = request.form['longText']

    # Paths for images
    input_image_path = "./imgs/card.png"
    output_image_path = "./imgs/output.png"
    avatar_cropped_path = "./imgs/avatar_cropped.png"

    # Crop avatar
    cropped_avatar = crop_to_circle(avatar)
    cropped_avatar.save(avatar_cropped_path)

    # Open and modify the card image
    with Image.open(input_image_path) as img:
        draw = ImageDraw.Draw(img)

        position = (560, 235)            
        font_size =  32               
        text_color = (19, 97, 180)
        font = ImageFont.truetype("./fonts/cocofy.ttf", font_size)

        indent_len = 20
        max_x = 700  # Maximum width of the text area
        lines = [line for line in longText.split('\r\n') if line.strip()]  # Split text into lines based on newlines
        
        for line in lines:
            words = line.split(' ')  # Split each line into words
            current_line = []
            word_ident = True
            
            for word in words:
                # Add word to current line
                current_line.append(word)
                # Join current line into a single string
                line_text = ' '.join(current_line)
                # Measure the bounding box of the current line
                line_bbox = draw.textbbox((0, 0), line_text, font=font)
                line_x = line_bbox[2]
                
                # If the line is too wide, finalize the previous line and start a new one
                if line_x + 60 > max_x:
                    # Remove the last word from the current line
                    current_line.pop()
                    # Draw the previous line justified
                    if current_line:
                        total_width = draw.textbbox((0, 0), ' '.join(current_line), font=font)[2]
                        spaces_needed = len(current_line) - 1
                        if spaces_needed > 0:
                            total_space = max_x - total_width
                            x = position[0]
                            if word_ident:
                                x += indent_len
                                word_ident = False
                                total_space -= indent_len

                            space_between_words = total_space / spaces_needed
                            for i, word2 in enumerate(current_line):
                                draw.text((x, position[1]), word2, font=font, fill=text_color)
                                x += draw.textbbox((0, 0), word2, font=font)[2]
                                if i < spaces_needed:  # Avoid adding space after the last word
                                    x += space_between_words

                    # Move to the next line
                    position = (position[0], position[1] + 40)  # Adjust vertical position for the next line
                    current_line = [word]  # Start new line with the last word

            # Draw the last line left-aligned if there are words remaining
            if current_line:
                if (word_ident == True): draw.text((position[0] + indent_len, position[1]), ' '.join(current_line), font=font, fill=text_color)
                else: draw.text(position, ' '.join(current_line), font=font, fill=text_color)
                position = (position[0], position[1] + 40)  # Move to the next line after drawing the last line

        #################################################################################################################
        align_right = 1190 
        font_size1 = 17.26 
        font_size2 = 22.19             
        font1 = ImageFont.truetype("./fonts/altergothic.ttf", font_size1)
        font2 = ImageFont.truetype("./fonts/futureextra.ttf", font_size2)
        x = align_right - (draw.textbbox((0, 0), xungHo, font=font1)[2] + 10 + draw.textbbox((0, 0), ten, font=font2)[2])
        y = 565

        position = (x, y + 6)                      
        text_color = (233, 77, 25)
        draw.text(position,xungHo,font=font1, fill=text_color)

        position = (x + 30, y)                    
        text_color = (233, 77, 25)
        draw.text(position,ten,font=font2, fill=text_color)





        font_size = 17.26
        font = ImageFont.truetype("./fonts/altergothic.ttf", font_size)
        x = align_right - draw.textbbox((0, 0), chucVu, font=font)[2]
        position = (x, y + 28)                              
        text_color = (233, 77, 25)
        draw.text(position,chucVu,font=font, fill=text_color)
        #################################################################################################################
        avatarImg = Image.open(avatar_cropped_path)
        img.paste(avatarImg, (142, 256), avatarImg)
        #test.save("./imgs/dpi.png", dpi=(300, 300))
        img.save(output_image_path)
        #print(f"Image saved as {output_path}")

    # Return the generated image to the frontend
    return send_file(output_image_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(port=3000)
