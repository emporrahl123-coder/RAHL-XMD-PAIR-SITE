"""
Discord bot integration for RAHL XMD pairing system.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List, Dict, Any
import asyncio
import json
from datetime import datetime
import io

from ..core.pairing_system import PairingSystem, CodeTheme, PairingStatus
from ..core.qr_generator import QRGenerator
from ..core.animation_engine import AnimationEngine
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class RAHLDiscordBot(commands.Bot):
    """Discord bot for RAHL XMD pairing system."""
    
    def __init__(self, 
                 command_prefix: str = "!",
                 intents: Optional[discord.Intents] = None,
                 data_dir: str = "discord_data"):
        """
        Initialize Discord bot.
        
        Args:
            command_prefix: Bot command prefix
            intents: Discord intents
            data_dir: Data directory for Discord-specific data
        """
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.members = True
        
        super().__init__(command_prefix=command_prefix, intents=intents)
        
        # Initialize pairing system
        self.pairing_system = PairingSystem(data_dir=data_dir)
        self.qr_generator = QRGenerator()
        self.animation_engine = AnimationEngine(qr_generator=self.qr_generator)
        
        # User mapping (Discord ID -> RAHL XMD user ID)
        self.user_mapping: Dict[int, str] = {}
        
        # Load user mapping
        self._load_user_mapping()
    
    def _load_user_mapping(self) -> None:
        """Load Discord user mapping from file."""
        try:
            mapping_file = self.pairing_system.data_dir / "discord_users.json"
            if mapping_file.exists():
                with open(mapping_file, 'r') as f:
                    self.user_mapping = json.load(f)
                    # Convert keys back to integers
                    self.user_mapping = {int(k): v for k, v in self.user_mapping.items()}
                logger.info(f"Loaded {len(self.user_mapping)} user mappings")
        except Exception as e:
            logger.error(f"Failed to load user mapping: {e}")
    
    def _save_user_mapping(self) -> None:
        """Save Discord user mapping to file."""
        try:
            mapping_file = self.pairing_system.data_dir / "discord_users.json"
            with open(mapping_file, 'w') as f:
                json.dump(self.user_mapping, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save user mapping: {e}")
    
    def _get_or_create_user_id(self, discord_user: discord.User) -> str:
        """
        Get or create RAHL XMD user ID for Discord user.
        
        Args:
            discord_user: Discord user object
        
        Returns:
            RAHL XMD user ID
        """
        discord_id = discord_user.id
        
        if discord_id in self.user_mapping:
            return self.user_mapping[discord_id]
        
        # Create new user
        user_id = f"discord_{discord_id}"
        username = f"{discord_user.name}#{discord_user.discriminator}"
        
        try:
            user = self.pairing_system.register_user(
                user_id=user_id,
                username=username,
                preferences={
                    "discord_id": str(discord_id),
                    "avatar_url": str(discord_user.avatar.url) if discord_user.avatar else None
                }
            )
            
            self.user_mapping[discord_id] = user_id
            self._save_user_mapping()
            
            logger.info(f"Created new user for Discord user {username}")
            return user_id
        
        except ValueError as e:
            # User might already exist
            if "already exists" in str(e):
                self.user_mapping[discord_id] = user_id
                self._save_user_mapping()
                return user_id
            raise
    
    async def setup_hook(self) -> None:
        """Setup bot commands."""
        # Sync application commands
        await self.tree.sync()
        logger.info("Bot commands synced")
    
    async def on_ready(self) -> None:
        """Called when bot is ready."""
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for pairing codes 👁️"
            )
        )
    
    async def on_message(self, message: discord.Message) -> None:
        """Handle incoming messages."""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Process commands
        await self.process_commands(message)
    
    @commands.command(name="pair")
    async def pair_command(self, ctx: commands.Context, theme: str = "default"):
        """
        Generate a pairing code.
        
        Usage: !pair [theme]
        Themes: default, neon, cyberpunk, matrix, aurora, hologram
        """
        try:
            # Get or create user
            user_id = self._get_or_create_user_id(ctx.author)
            
            # Validate theme
            try:
                code_theme = CodeTheme(theme.lower())
            except ValueError:
                await ctx.send(f"❌ Invalid theme. Available themes: {', '.join(t.value for t in CodeTheme)}")
                return
            
            # Generate pairing code
            pairing_code = self.pairing_system.generate_pairing_code(
                owner_id=user_id,
                theme=code_theme,
                expires_hours=24,
                max_uses=3
            )
            
            # Generate QR code
            qr_img = self.qr_generator.generate_qr_code(pairing_code)
            
            # Convert to bytes for Discord
            with io.BytesIO() as image_binary:
                qr_img.save(image_binary, 'PNG')
                image_binary.seek(0)
                
                # Create embed
                embed = discord.Embed(
                    title="🔗 RAHL XMD Pairing Code",
                    description=f"Share this code with others to connect!",
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                
                embed.add_field(
                    name="📋 Code",
                    value=f"```{pairing_code.code}```",
                    inline=False
                )
                
                embed.add_field(
                    name="🎨 Theme",
                    value=pairing_code.theme.value.title(),
                    inline=True
                )
                
                embed.add_field(
                    name="⏰ Expires",
                    value=f"<t:{int(pairing_code.expires_at.timestamp())}:R>",
                    inline=True
                )
                
                embed.add_field(
                    name="📊 Uses",
                    value=f"{pairing_code.uses_count}/{pairing_code.max_uses}",
                    inline=True
                )
                
                embed.set_footer(text="RAHL XMD Pairing System")
                embed.set_image(url="attachment://qrcode.png")
                
                # Send message
                await ctx.send(
                    embed=embed,
                    file=discord.File(image_binary, filename="qrcode.png")
                )
                
                logger.info(f"Generated pairing code {pairing_code.code} for {ctx.author}")
        
        except Exception as e:
            logger.error(f"Error in pair command: {e}")
            await ctx.send(f"❌ An error occurred: {str(e)}")
    
    @commands.command(name="scan")
    async def scan_command(self, ctx: commands.Context, code: str):
        """
        Scan/use a pairing code.
        
        Usage: !scan <code>
        """
        try:
            # Get or create user
            user_id = self._get_or_create_user_id(ctx.author)
            
            # Use pairing code
            success, message = self.pairing_system.use_pairing_code(code.upper(), user_id)
            
            if success:
                pairing_id = message
                pairing = self.pairing_system.get_pairing(pairing_id)
                
                if pairing:
                    # Create success embed
                    embed = discord.Embed(
                        title="✅ Pairing Successful!",
                        description=f"You are now paired with another user!",
                        color=discord.Color.green(),
                        timestamp=datetime.now()
                    )
                    
                    embed.add_field(
                        name="🔗 Pairing ID",
                        value=f"`{pairing_id[:12]}...`",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="💝 Compatibility",
                        value=f"{pairing.compatibility_score:.0%}",
                        inline=True
                    )
                    
                    if pairing.shared_interests:
                        embed.add_field(
                            name="🎯 Shared Interests",
                            value=", ".join(pairing.shared_interests[:3]),
                            inline=True
                        )
                    
                    embed.set_footer(text="RAHL XMD Pairing System")
                    
                    await ctx.send(embed=embed)
                    
                    # Try to notify the other user
                    other_user_id = pairing.user2_id if pairing.user1_id == user_id else pairing.user1_id
                    
                    # Find Discord user
                    discord_id = None
                    for disc_id, rahl_id in self.user_mapping.items():
                        if rahl_id == other_user_id:
                            discord_id = disc_id
                            break
                    
                    if discord_id:
                        try:
                            other_user = await self.fetch_user(discord_id)
                            if other_user:
                                # Send DM
                                dm_embed = discord.Embed(
                                    title="🔔 New Pairing!",
                                    description=f"**{ctx.author.name}** used your pairing code!",
                                    color=discord.Color.blue(),
                                    timestamp=datetime.now()
                                )
                                
                                dm_embed.add_field(
                                    name="👤 User",
                                    value=ctx.author.mention,
                                    inline=True
                                )
                                
                                dm_embed.add_field(
                                    name="💝 Compatibility",
                                    value=f"{pairing.compatibility_score:.0%}",
                                    inline=True
                                )
                                
                                await other_user.send(embed=dm_embed)
                        except:
                            pass  # Couldn't send DM
                
                logger.info(f"User {ctx.author} used code {code}")
            
            else:
                await ctx.send(f"❌ {message}")
        
        except Exception as e:
            logger.error(f"Error in scan command: {e}")
            await ctx.send(f"❌ An error occurred: {str(e)}")
    
    @commands.command(name="mypairs")
    async def mypairs_command(self, ctx: commands.Context):
        """
        Show your active pairings.
        
        Usage: !mypairs
        """
        try:
            # Get or create user
            user_id = self._get_or_create_user_id(ctx.author)
            
            # Get pairings
            pairings = self.pairing_system.get_user_pairings(
                user_id, 
                status=PairingStatus.ACTIVE
            )
            
            if not pairings:
                embed = discord.Embed(
                    title="🤷 No Active Pairings",
                    description="You haven't paired with anyone yet!",
                    color=discord.Color.orange(),
                    timestamp=datetime.now()
                )
                
                embed.add_field(
                    name="💡 Tip",
                    value="Use `!pair` to generate a pairing code, or `!scan <code>` to use someone else's code!",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                return
            
            # Create embed
            embed = discord.Embed(
                title=f"🔗 Your Active Pairings ({len(pairings)})",
                description="Here are your current connections:",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            for i, pairing in enumerate(pairings[:5], 1):
                # Get other user's info
                other_user_id = pairing.user2_id if pairing.user1_id == user_id else pairing.user1_id
                
                # Try to find Discord user
                discord_user = None
                for disc_id, rahl_id in self.user_mapping.items():
                    if rahl_id == other_user_id:
                        try:
                            discord_user = await self.fetch_user(disc_id)
                        except:
                            pass
                        break
                
                user_display = discord_user.mention if discord_user else f"`{other_user_id[:8]}...`"
                
                embed.add_field(
                    name=f"#{i} - {pairing.pairing_id[:8]}...",
                    value=f"👤 {user_display}\n"
                          f"💝 {pairing.compatibility_score:.0%} compatibility\n"
                          f"📅 <t:{int(pairing.created_at.timestamp())}:R>",
                    inline=False
                )
            
            if len(pairings) > 5:
                embed.set_footer(text=f"... and {len(pairings) - 5} more pairings")
            
            await ctx.send(embed=embed)
        
        except Exception as e:
            logger.error(f"Error in mypairs command: {e}")
            await ctx.send(f"❌ An error occurred: {str(e)}")
    
    @commands.command(name="pairstats")
    async def pairstats_command(self, ctx: commands.Context):
        """
        Show your pairing statistics.
        
        Usage: !pairstats
        """
        try:
            # Get or create user
            user_id = self._get_or_create_user_id(ctx.author)
            
            # Get stats
            stats = self.pairing_system.get_user_stats(user_id)
            
            # Create embed
            embed = discord.Embed(
                title="📊 Your Pairing Statistics",
                color=discord.Color.purple(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="🔗 Total Pairings",
                value=str(stats.get("total_pairings", 0)),
                inline=True
            )
            
            embed.add_field(
                name="✅ Active Pairings",
                value=str(stats.get("active_pairings", 0)),
                inline=True
            )
            
            embed.add_field(
                name="🎯 Avg Compatibility",
                value=f"{stats.get('compatibility_avg', 0):.0%}",
                inline=True
            )
            
            embed.add_field(
                name="📋 Codes Generated",
                value=str(stats.get("codes_generated", 0)),
                inline=True
            )
            
            embed.add_field(
                name="🔄 Active Codes",
                value=str(stats.get("active_codes", 0)),
                inline=True
            )
            
            most_common = stats.get("most_common_interest")
            if most_common:
                embed.add_field(
                    name="🏆 Top Interest",
                    value=most_common,
                    inline=True
                )
            
            embed.set_footer(text="RAHL XMD Pairing System")
            
            await ctx.send(embed=embed)
        
        except Exception as e:
            logger.error(f"Error in pairstats command: {e}")
            await ctx.send(f"❌ An error occurred: {str(e)}")
    
    @commands.command(name="animatedqr")
    async def animatedqr_command(self, ctx: commands.Context, code: str):
        """
        Generate animated QR code for a pairing code.
        
        Usage: !animatedqr <code>
        """
        try:
            # Get pairing code
            pairing_code = self.pairing_system.get_pairing_code(code.upper())
            
            if not pairing_code:
                await ctx.send(f"❌ Pairing code not found")
                return
            
            # Check if user owns the code
            user_id = self._get_or_create_user_id(ctx.author)
            if pairing_code.owner_id != user_id:
                await ctx.send(f"❌ You don't own this pairing code")
                return
            
            # Generate animated frames
            frames = self.animation_engine.create_theme_animation(
                pairing_code,
                pairing_code.theme
            )
            
            if len(frames) > 1:
                # Save as GIF
                with io.BytesIO() as gif_binary:
                    # Save first frame
                    frames[0].save(
                        gif_binary,
                        format='GIF',
                        save_all=True,
                        append_images=frames[1:],
                        duration=100,
                        loop=0,
                        optimize=True
                    )
                    gif_binary.seek(0)
                    
                    # Send GIF
                    file = discord.File(gif_binary, filename="animated_qr.gif")
                    
                    embed = discord.Embed(
                        title="🌀 Animated QR Code",
                        description=f"Here's your animated QR code for `{code}`",
                        color=discord.Color.blue(),
                        timestamp=datetime.now()
                    )
                    
                    embed.set_image(url="attachment://animated_qr.gif")
                    embed.set_footer(text="RAHL XMD Pairing System")
                    
                    await ctx.send(embed=embed, file=file)
            
            else:
                await ctx.send("❌ Could not generate animated QR code")
        
        except Exception as e:
            logger.error(f"Error in animatedqr command: {e}")
            await ctx.send(f"❌ An error occurred: {str(e)}")
    
    @commands.command(name="themes")
    async def themes_command(self, ctx: commands.Context):
        """
        Show available themes.
        
        Usage: !themes
        """
        embed = discord.Embed(
            title="🎨 Available Themes",
            description="Choose a theme for your pairing codes:",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        
        for theme in CodeTheme:
            embed.add_field(
                name=theme.value.title(),
                value=f"`!pair {theme.value}`",
                inline=True
            )
        
        embed.add_field(
            name="🌀 Animated QR",
            value="Use `!animatedqr <code>` after generating a code",
            inline=False
        )
        
        embed.set_footer(text="RAHL XMD Pairing System")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context):
        """
        Show help information.
        
        Usage: !help
        """
        embed = discord.Embed(
            title="🤖 RAHL XMD Pairing Bot Help",
            description="Here are all available commands:",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        commands_info = [
            ("!pair [theme]", "Generate a pairing code with optional theme"),
            ("!scan <code>", "Use someone's pairing code to connect"),
            ("!mypairs", "Show your active pairings"),
            ("!pairstats", "Show your pairing statistics"),
            ("!animatedqr <code>", "Generate animated QR code for your pairing code"),
            ("!themes", "Show available themes"),
            ("!help", "Show this help message"),
        ]
        
        for cmd, desc in commands_info:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        embed.add_field(
            name="💡 Quick Start",
            value="1. Use `!pair` to generate a code\n"
                  "2. Share the code with friends\n"
                  "3. They use `!scan <your-code>` to connect\n"
                  "4. Use `!mypairs` to see your connections",
            inline=False
        )
        
        embed.set_footer(text="RAHL XMD Pairing System")
        
        await ctx.send(embed=embed)
