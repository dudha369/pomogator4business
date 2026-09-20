from aiogram import Router

from mirror.spam import router as spam_router

router = Router(name="mirror_root")
router.include_router(spam_router)
