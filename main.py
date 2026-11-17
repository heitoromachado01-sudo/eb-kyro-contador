
import discord
from discord.ext import commands
import json
import os

TOKEN = os.getenv("BOT_TOKEN")
CANAL_PROVAS = int(os.getenv("PROVAS_CHANNEL_ID", "0"))
ARQUIVO = "provas.json"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

try:
    with open(ARQUIVO, "r") as f:
        provas = json.load(f)
except:
    provas = {}

def salvar():
    with open(ARQUIVO, "w") as f:
        json.dump(provas, f)

@bot.event
async def on_ready():
    print(f"BOT ONLINE: {bot.user}")

@bot.event
async def on_message(message):
    if not message.author.bot and message.channel.id == CANAL_PROVAS:
        imagens = [
            a for a in message.attachments
            if (a.content_type or "").startswith("image/")
            or a.filename.lower().endswith(
                (".png", ".jpg", ".jpeg", ".gif", ".webp")
            )
        ]

        if imagens:
            uid = str(message.author.id)
            provas[uid] = provas.get(uid, 0) + len(imagens)
            salvar()

    await bot.process_commands(message)

@bot.command(name="provas")
async def consultar(ctx, jogador: discord.User = None):
    if jogador is None:
        return await ctx.send("Use: !provas @jogador")

    total = provas.get(str(jogador.id), 0)

    await ctx.send(
        f"📋 **CONTAGEM DE PROVAS**\n"
        f"👤 Jogador: {jogador.mention}\n"
        f"📸 Prints: **{total}**"
    )

@bot.command(name="rank")
async def ranking(ctx):
    ordem = sorted(
        provas.items(),
        key=lambda item: item[1],
        reverse=True
    )

    if not ordem:
        return await ctx.send("Ainda não existem provas!")

    texto = "🏆 **RANKING DE PROVAS — EB DO KYRO**\n\n"

    for i, (uid, total) in enumerate(ordem[:10], 1):
        try:
            jogador = await bot.fetch_user(int(uid))
            nome = jogador.display_name
        except:
            nome = uid

        texto += f"**{i}.** {nome} — {total} prints\n"

    await ctx.send(texto)

if not TOKEN:
    raise ValueError("BOT_TOKEN não configurado!")

if not CANAL_PROVAS:
    raise ValueError("ID do canal não configurado!")

bot.run(TOKEN)
  
