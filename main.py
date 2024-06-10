import datetime
import io
import os
from typing import Annotated

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

# if __name__ == "__main__":
#     print(xmltobmp.generateImage('test_price_tag.xml').save('test1.bmp'))
