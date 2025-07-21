import shutil
import discord

class ConfirmDeleteView(discord.ui.View):
    def __init__(self, target_dir, user_id):
        super().__init__(timeout=60)
        self.target_dir = target_dir
        self.user_id = user_id
        self.result = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("あなたはこの操作をできません。", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="削除する", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            shutil.rmtree(self.target_dir)
            await interaction.response.edit_message(content=f"ディレクトリ `{self.target_dir}` を削除しました。", view=None)
        except Exception as e:
            await interaction.response.edit_message(content=f"削除に失敗しました: {e}", view=None)
        self.result = True
        self.stop()

    @discord.ui.button(label="キャンセル", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="削除をキャンセルしました。", view=None)
        self.result = False
        self.stop()