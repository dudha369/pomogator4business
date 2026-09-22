from tortoise import fields
from tortoise.models import Model


class TttGame(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()
    board = fields.CharField(max_length=16, default=".........")
    turn = fields.CharField(max_length=1, default="X")
    player_x_id = fields.BigIntField(null=True)
    player_x_name = fields.CharField(max_length=255, null=True)
    player_o_id = fields.BigIntField(null=True)
    player_o_name = fields.CharField(max_length=255, null=True)
    status = fields.CharField(max_length=16, default="active")
    message_id = fields.BigIntField(null=True)

    class Meta:
        table = "ttt_games"
        unique_together = (("connection_id", "chat_id"),)


class WordleGame(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()
    secret = fields.CharField(max_length=32, default="")
    guesses = fields.TextField(default="[]")
    status = fields.CharField(max_length=16, default="active")
    message_id = fields.BigIntField(null=True)
    starter_id = fields.BigIntField(null=True)

    class Meta:
        table = "wordle_games"
        unique_together = (("connection_id", "chat_id"),)


class ChkGame(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()
    board = fields.TextField(default="")
    turn = fields.CharField(max_length=1, default="w")
    player_w_id = fields.BigIntField(null=True)
    player_w_name = fields.CharField(max_length=255, null=True)
    player_b_id = fields.BigIntField(null=True)
    player_b_name = fields.CharField(max_length=255, null=True)
    selected = fields.IntField(null=True)
    status = fields.CharField(max_length=16, default="active")
    message_id = fields.BigIntField(null=True)

    class Meta:
        table = "chk_games"
        unique_together = (("connection_id", "chat_id"),)


class MsGame(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()
    size = fields.IntField(default=6)
    bomb_mode = fields.CharField(max_length=16, default="auto")
    coop = fields.BooleanField(default=False)
    mines = fields.TextField(default="[]")
    revealed = fields.TextField(default="")
    starter_id = fields.BigIntField(null=True)
    starter_name = fields.CharField(max_length=255, null=True)
    phase = fields.CharField(max_length=16, default="settings")
    message_id = fields.BigIntField(null=True)

    class Meta:
        table = "ms_games"
        unique_together = (("connection_id", "chat_id"),)


class GuessGame(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()
    secret = fields.IntField(default=1)
    max_value = fields.IntField(default=100)
    attempts = fields.IntField(default=0)
    status = fields.CharField(max_length=16, default="active")

    class Meta:
        table = "guess_games"
        unique_together = (("connection_id", "chat_id"),)


class CityGame(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()
    used_words = fields.TextField(default="[]")
    next_letter = fields.CharField(max_length=4, null=True)
    status = fields.CharField(max_length=16, default="active")

    class Meta:
        table = "city_games"
        unique_together = (("connection_id", "chat_id"),)


class HangmanGame(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()
    secret = fields.CharField(max_length=64, default="")
    guessed_letters = fields.TextField(default="[]")
    mistakes = fields.IntField(default=0)
    status = fields.CharField(max_length=16, default="active")
    message_id = fields.BigIntField(null=True)

    class Meta:
        table = "hangman_games"
        unique_together = (("connection_id", "chat_id"),)


class G2048Game(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()
    board = fields.TextField(default="")
    score = fields.IntField(default=0)
    status = fields.CharField(max_length=16, default="active")
    player_id = fields.BigIntField(null=True)
    message_id = fields.BigIntField(null=True)

    class Meta:
        table = "g2048_games"
        unique_together = (("connection_id", "chat_id"),)
