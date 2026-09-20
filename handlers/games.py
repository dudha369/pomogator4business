from aiogram import Router

from modules.checkers import router as chk_router
from modules.g2048 import router as g2048_router
from modules.minesweeper import router as ms_router
from modules.quiz import router as quiz_router
from modules.rps import router as rps_router
from modules.ttt import router as ttt_router

router = Router(name="games")
router.include_router(ttt_router)
router.include_router(chk_router)
router.include_router(ms_router)
router.include_router(rps_router)
router.include_router(quiz_router)
router.include_router(g2048_router)
