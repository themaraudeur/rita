import discord
from discord.ext import commands
import json
import os
import asyncio

# Classe de bot personnalisée pour charger la configuration et les cogs
class RitaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.dm_messages = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erreur: Impossible de charger le fichier config.json. {e}")
            exit()

    async def setup_hook(self):
        # Charge les cogs (extensions) du bot
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"✅ Cog chargé : {filename}")
                except Exception as e:
                    print(f"❌ Erreur lors du chargement du cog {filename}: {e}")
        
        # S'assure que les vues persistantes sont ré-enregistrées au démarrage
        from cogs.ticket_system import TicketCreationView, TicketCloseView
        self.add_view(TicketCreationView(self))
        self.add_view(TicketCloseView(self))


    async def on_ready(self):
        print(f"✅ {self.user} est prêt et connecté !")
        print(f"📌 Connecté à {len(self.guilds)} serveur(s).")


async def main():
    bot = RitaBot()
    bot.load_config()
    await bot.start(bot.config.get("bot_token"))

if __name__ == "__main__":
    asyncio.run(main())
