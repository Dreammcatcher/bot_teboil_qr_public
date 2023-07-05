from io import BytesIO
from models.model import session, Teboil, UserId
import qrcode
from PIL import Image, ImageDraw, ImageFont


async def create_qr_after_update(nomer, balance):
    """
    :return объект собранной картинки карты лояльности
    """
    qrimg = qrcode.make(nomer)
    img = Image.open('images/com.teboil.azs_empty2.png')

    font = ImageFont.truetype("images/CriqueGroteskDisplay-BlackIt.ttf", 70)
    drawer = ImageDraw.Draw(img)

    drawer.text((690, 678), str(balance), font=font, fill='white', stroke_width=0)

    width, height = qrimg.size
    barcod = qrimg.crop((37, 37, width - 37, height - 37))

    qrimg = barcod.resize((655, 655))
    imag1 = img.copy()
    imag1.paste(qrimg, (211, 945))
    #imag1.save('ready.png', quality=100)
    image_kart_buffer = BytesIO()
    image_kart_buffer.name = 'ready.png'
    imag1.save(image_kart_buffer, 'png')
    image_kart_buffer.seek(0)
    return image_kart_buffer


def append_user_to_bd(user_id: any, user_name: str):
    data = UserId(user_id=int(user_id),
                  user_name=user_name)
    session.add(data)
    session.commit()
