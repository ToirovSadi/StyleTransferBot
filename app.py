import os
import telebot

import io
from model import style_transfer

bot = telebot.TeleBot("6320906497:AAEAMUP83C0KV3w6qyhI7k93vi4vl_CbdIA")
CONTENT_FILE = "examples/content_image.png"
STYLE_FILE = "examples/style_image.png"
GEN_FILE = "examples/gen_image.png"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Hey, there!')
    

@bot.message_handler(commands=['transfer_style'])
def transfer_style(message):
    bot.send_message(message.chat.id, "Please send me content image")
    bot.register_next_step_handler(message, get_content_image)


def get_content_image(message):
    photo = message.photo[-1]
    # Download the images
    file1 = bot.download_file(bot.get_file(photo.file_id).file_path)
    
    print("saving content_image")
    with open(CONTENT_FILE, "wb") as f:
        f.write(file1)
    
    bot.send_message(message.chat.id, "Please send me style image")
    bot.register_next_step_handler(message, get_style_image)


def get_style_image(message):
    photo = message.photo[-1]
    # Download the images
    file1 = bot.download_file(bot.get_file(photo.file_id).file_path)
    
    print("saving style_image")
    with open(STYLE_FILE, "wb") as f:
        f.write(file1)
    
    bot.send_message(message.chat.id, "Please wait for the generated image")
    print("Start generating Image")
    # Process the images using your deep learning model
    output_image, params = process_images(CONTENT_FILE, STYLE_FILE)
    message = bot.send_photo(message.chat.id, photo=output_image)
    
    text = f"Elapsed time: {params['elapsed_time']:.3f} sec\n" + \
            f"Image size: {params['image_size']}\n" + \
            f"Epochs: {params['completed_epochs']}/{params['epochs']}\n" + \
            f"Timeout: {params['timeout_sec']} sec\n" + \
            f"Content Weight: {params['content_weight']}\n" + \
            f"Style Weight: {params['style_weight']}\n" + \
            f"TV Weight: {params['tv_weight']}\n"
    bot.reply_to(message, text)


def process_images(img1, img2):
    gen_image, params = style_transfer(
        content_image_path=img1,
        style_image_path=img2,
        timeout_sec=60,
        logs=True,
        image_size=512,
        skip_steps=5,
        style_weight=2e2,
    )
    # Save the gen_image
    gen_image.save(GEN_FILE, format='PNG')
    
    img_stream = io.BytesIO()
    gen_image.save(img_stream, format='PNG')
    img_stream.seek(0)
    
    return img_stream, params

bot.infinity_polling()