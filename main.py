import datetime
import io
import os
from typing import Annotated

from PIL import Image
from fastapi.openapi.models import Response
from starlette.responses import StreamingResponse

import xmltobmp
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse

app = FastAPI()


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()], specification: str, price_rub: str, price_kop: str, c_price1_rub: str,
                      c_price1_kop: str, country: str, id_: str, date_price: str, unit: str):
    f = open('temp.xml', 'wb')
    f.write(file)
    f.close()

    img = xmltobmp.generateImage('temp.xml', specification, price_rub, price_kop, c_price1_rub, c_price1_kop, country, id_, date_price, unit)
    img.save('temp.bmp')
    return FileResponse(path='temp.bmp', filename='test_temp.bmp', media_type='image/bmp')


@app.post("/twoTags/")
async def create_file(file_1: Annotated[bytes, File()], specification_1: str, price_rub_1: str, price_kop_1: str, c_price1_rub_1: str, c_price1_kop_1: str,
                      file_2: Annotated[bytes, File()], specification_2: str, price_rub_2: str, price_kop_2: str, c_price1_rub_2: str, c_price1_kop_2: str,
                      distance = 0):
    f = open('temp_1.xml', 'wb')
    f.write(file_1)
    f.close()

    f = open('temp_2.xml', 'wb')
    f.write(file_2)
    f.close()

    img_1 = xmltobmp.generateImage('temp_1.xml', specification_1, price_rub_1, price_kop_1, c_price1_rub_1, c_price1_kop_1)
    img_2 = xmltobmp.generateImage('temp_2.xml', specification_2, price_rub_2, price_kop_2, c_price1_rub_2, c_price1_kop_2)

    new_image = Image.new('RGB', (2 * img_1.size[0]+int(distance), img_1.size[1]), (250, 250, 250))
    new_image.paste(img_1, (0, 0))
    new_image.paste(img_2, (img_1.size[0]+int(distance), 0))
    new_image.save('temp.bmp')

    return FileResponse(path='temp.bmp', filename='test_temp.bmp', media_type='image/bmp')

# if __name__ == "__main__":
#     print(xmltobmp.generateImage('test_price_tag.xml').save('test1.bmp'))
