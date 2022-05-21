import asyncio

from wahu_backend.pixiv_image import PixivImageGetter


def test_image_get():
    async def main():
        global image
        getter = PixivImageGetter(timeout=5)
        image = await getter.get_image(
            '/c/540x540_70/img-master/img/2021/11/17/00/00/56/94181355_p0_master1200.jpg'
        )
        await getter.close_session()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    assert len(image) != 0
