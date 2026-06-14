import discord
from discord.ext import commands, tasks
from mcstatus import JavaServer, BedrockServer
import asyncio
import os

# ==================== CONFIG (Environment Variables) ====================
SERVER_ADDRESS = os.getenv('SERVER_ADDRESS', 'your.server.ip')  # Railway Variables එකෙන් ගන්න
CHANNEL_ID = int(os.getenv('CHANNEL_ID', '0'))                  # Channel ID
UPDATE_INTERVAL_MINUTES = int(os.getenv('UPDATE_INTERVAL', '5'))  # විනාඩි ගණන

# =====================================================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

status_message = None

@bot.event
async def on_ready():
    print(f'✅ Minecraft Auto Status Bot ඔන්ලයින් වුණා! {bot.user}')
    await bot.change_presence(activity=discord.Game(name="Minecraft | !mchelp"))
    
    if CHANNEL_ID != 0:
        auto_status_update.start()
    else:
        print("⚠️ CHANNEL_ID සකස් කර නැත. Auto update නොකරයි.")

# ==================== AUTO STATUS UPDATE ====================
@tasks.loop(minutes=UPDATE_INTERVAL_MINUTES)
async def auto_status_update():
    global status_message
    channel = bot.get_channel(CHANNEL_ID)
    
    if channel is None:
        print(f"❌ Channel ID {CHANNEL_ID} හමු නොවුණි.")
        return

    try:
        # Java Edition උත්සාහ
        server = JavaServer.lookup(SERVER_ADDRESS)
        status = server.status()

        embed = discord.Embed(
            title="✅ Minecraft Server ONLINE",
            description=f"**IP:** `{SERVER_ADDRESS}`",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="🟢 Players", value=f"{status.players.online}/{status.players.max}", inline=True)
        embed.add_field(name="📌 Version", value=status.version.name, inline=True)
        embed.add_field(name="🏷️ MOTD", value=status.motd.to_plain(), inline=False)
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/5969/5969052.png")

    except Exception:
        # Bedrock Edition උත්සාහ
        try:
            bedrock = BedrockServer.lookup(SERVER_ADDRESS)
            status = bedrock.status()

            embed = discord.Embed(
                title="✅ Minecraft Bedrock Server ONLINE",
                description=f"**IP:** `{SERVER_ADDRESS}`",
                color=0x00ff00,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="🟢 Players", value=f"{status.players.online}/{status.players.max}", inline=True)
            embed.add_field(name="📌 Version", value=f"{status.version.brand} {status.version.name}", inline=True)
        except:
            embed = discord.Embed(
                title="❌ Server OFFLINE",
                description=f"**{SERVER_ADDRESS}** සම්බන්ධ කරගත නොහැකි විය.",
                color=0xff0000,
                timestamp=discord.utils.utcnow()
            )

    # Message Edit හෝ නව Message යැවීම
    try:
        if status_message is None:
            status_message = await channel.send(embed=embed)
        else:
            await status_message.edit(embed=embed)
    except:
        try:
            status_message = await channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending status: {e}")

@auto_status_update.before_loop
async def before_auto_update():
    await bot.wait_until_ready()

# ==================== MANUAL COMMANDS ====================
@bot.command()
async def mcstatus(ctx, address: str = None):
    addr = address or SERVER_ADDRESS
    await ctx.send(f"🔍 `{addr}` සෙවමින්... කරුණාකර ටිකක් ඉන්න.")

    try:
        server = JavaServer.lookup(addr)
        status = server.status()
        embed = discord.Embed(title="✅ Server ONLINE", color=0x00ff00)
        embed.add_field(name="Players", value=f"{status.players.online}/{status.players.max}", inline=True)
        embed.add_field(name="Version", value=status.version.name, inline=True)
        embed.add_field(name="MOTD", value=status.motd.to_plain(), inline=False)
    except:
        try:
            bedrock = BedrockServer.lookup(addr)
            status = bedrock.status()
            embed = discord.Embed(title="✅ Bedrock Server ONLINE", color=0x00ff00)
            embed.add_field(name="Players", value=f"{status.players.online}/{status.players.max}", inline=True)
        except:
            embed = discord.Embed(title="❌ Server OFFLINE", color=0xff0000)
            embed.description = f"`{addr}` සම්බන්ධ කරගත නොහැකි විය."

    await ctx.send(embed=embed)

@bot.command()
async def mchelp(ctx):
    embed = discord.Embed(title="🎮 Minecraft Bot Help", color=0x00ffff)
    embed.add_field(name="!mcstatus", value="ඔබේ Server එකේ තත්ත්වය බලන්න", inline=False)
    embed.add_field(name="!mcstatus <ip>", value="වෙනත් Server එකක් බලන්න", inline=False)
    embed.add_field(name="Auto Update", value="කාලයකට වතාවක් තෝරාගත් Channel එකේ Update වෙනවා", inline=False)
    await ctx.send(embed=embed)

# ==================== RUN BOT ====================
bot.run(os.getenv('DISCORD_TOKEN'))
