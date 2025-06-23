import discord
from discord.ext import commands
from discord.ui import View, Select
import json

# Activation des intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.dm_messages = True

# Création du bot
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ID du serveur (À MODIFIER avec ton serveur)
GUILD_ID = 1308868908932927528

# Charger la configuration des commandes du serveur
def load_server_commands():
    try:
        with open("command_serveur.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}  # Retourne un JSON vide si le fichier n'existe pas

# Charger la configuration des commandes en MP
def load_dm_commands():
    try:
        with open("commands_dm.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}  # Retourne un JSON vide si le fichier n'existe pas

# Vérifier si un utilisateur a un rôle requis
def has_required_roles(user, roles_required):
    return any(role.name in roles_required for role in user.roles)

# Menu déroulant pour les catégories de tickets
class CategorySelect(Select):
    def __init__(self, author):
        self.author = author
        options = [
            discord.SelectOption(label="PPA", description="Ouvrir un ticket pour PPA"),
            discord.SelectOption(label="PSY", description="Ouvrir un ticket pour PSY"),
            discord.SelectOption(label="Kine", description="Ouvrir un ticket pour Kine"),
        ]
        super().__init__(placeholder="Choisissez une catégorie...", options=options, custom_id="category_select")

    async def callback(self, interaction: discord.Interaction):
        guild = bot.get_guild(GUILD_ID)

        if not guild:
            await interaction.response.send_message("❌ Erreur : Serveur introuvable. Vérifie que le bot est bien sur le serveur et que l'ID est correct.", ephemeral=True)
            return

        selected_category = self.values[0].lower()
        category = discord.utils.get(guild.categories, name=selected_category)

        if not category:
            await interaction.response.send_message(f"❌ La catégorie {selected_category} n'existe pas.", ephemeral=True)
            return

        # Vérifie si un ticket existe déjà pour cet utilisateur
        existing_ticket = next((c for c in category.text_channels if c.name == f"ticket-{self.author.name.lower()}"), None)

        if existing_ticket:
            await interaction.response.send_message(
                f"⚠️ Vous avez déjà un ticket ouvert : {existing_ticket.mention}", ephemeral=True
            )
            return

        # Crée un nouveau ticket
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{self.author.name.lower()}",
            category=category,
            topic=f"Ticket ouvert par {self.author} dans la catégorie {selected_category}",
        )

        # Définit les permissions
        await ticket_channel.set_permissions(self.author, read_messages=True, send_messages=True)
        await ticket_channel.set_permissions(guild.default_role, read_messages=False)

        await interaction.response.send_message(
            f"✅ Votre ticket a été créé dans la catégorie **{selected_category}** : {ticket_channel.mention}",
            ephemeral=True,
        )
        await ticket_channel.send(f"👋 Bonjour {self.author.mention}, merci d'avoir ouvert un ticket !")

# Vue contenant le menu déroulant
class CategorySelectView(View):
    def __init__(self, author):
        super().__init__(timeout=None)
        self.add_item(CategorySelect(author))

# Commande pour créer un ticket sécurisé en MP
@bot.command()
async def securiser(ctx):
    # Vérifier que la commande est utilisée en MP
    if isinstance(ctx.channel, discord.DMChannel):
        # Récupérer la configuration du serveur
        server_commands = load_server_commands()

        if "ticket_create_secure" in server_commands and server_commands["ticket_create_secure"]["enabled"]:
            # Vérifier si l'utilisateur a les rôles requis (optionnel)
            roles_required = server_commands["ticket_create_secure"].get("roles_required", [])

            if roles_required and not has_required_roles(ctx.author, roles_required):
                await ctx.author.send("❌ Vous n'avez pas les permissions nécessaires pour créer un ticket sécurisé.")
                return

            # Envoi du message privé avec le menu pour créer un ticket sécurisé
            view = CategorySelectView(ctx.author)
            await ctx.author.send("🎟️ Créez un ticket sécurisé en choisissant une catégorie ci-dessous :", view=view)
        else:
            await ctx.author.send("❌ La commande de ticket sécurisé n'est pas activée.")
    else:
        await ctx.send("❌ La commande `!securiser` doit être utilisée en message privé.")

# Gestion des tickets simples en MP
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if isinstance(message.channel, discord.DMChannel):  # Si c'est un MP
        guild = bot.get_guild(GUILD_ID)

        if guild is None:
            await message.channel.send("❌ Erreur : Serveur introuvable. Vérifie que le bot est bien sur le serveur.")
            return

        dm_commands = load_dm_commands()
        if "ticket_create_simple" in dm_commands and dm_commands["ticket_create_simple"]["enabled"]:
            view = CategorySelectView(message.author)
            await message.channel.send(dm_commands["ticket_create_simple"]["response_message"], view=view)
        else:
            await message.channel.send("Commande inconnue ou désactivée.")
    else:
        await bot.process_commands(message)  # Traitement des commandes normales

# Vérifier que le bot est bien connecté au serveur
@bot.event
async def on_ready():
    print(f"✅ {bot.user} est prêt et connecté !")

    # Affiche les serveurs où le bot est présent
    for guild in bot.guilds:
        print(f"📌 Serveur trouvé : {guild.name} (ID: {guild.id})")

    bot.add_view(CategorySelectView(bot.user))  # Enregistre la vue après un redémarrage

# Lancement du bot
bot.run("MTMwODg2Nzc3NTc2MjI2ODI4MA.GvostK.OSPPTHuSYWbwr5xgcjrebJLpsTWoZrCbBujnfs")
