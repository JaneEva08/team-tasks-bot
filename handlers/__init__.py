from aiogram import Router

from handlers import start, tasks

router = Router()
router.include_router(start.router)
router.include_router(tasks.router)
