import io
import re
import textwrap
import urllib.request
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw, ImageOps
from pincer import command, Client, Descripted
from pincer.objects import Message, Embed, MessageContext


class Bot(Client):

    @Client.event
    async def on_ready(self):
        print(
            f"Started client on {self.bot}\n"
            "Registered commands: " + ", ".join(self.chat_commands)
        )

    @command(
        name='twitter',
        description='to create fake tweets',
        guild=690604075775164437
    )
    async def twitter(self, ctx: MessageContext, content: Descripted[str, '...']):
        await ctx.interaction.ack()

        message = content
        for text_match, user_id in re.findall(re.compile(r"(<@!(\d+)>)"), message):
            print(str(await self.get_user(user_id)))
            message = message.replace(text_match, '@' + str(await self.get_user(user_id)))

        if len(message) > 280:
            return 'A tweet can be at maximum 280 characters long'

        # wrap the message to be multi-line
        message = textwrap.wrap(message, 38)

        # download the profile picture and convert it into Image object
        request = urllib.request.Request(
            f"https://cdn.discordapp.com/avatars/{ctx.author.user.id}/{ctx.author.user.avatar}.webp?size=128",
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'}
        )
        avatar = urllib.request.urlopen(request).read()
        avatar = io.BytesIO(avatar)
        avatar = Image.open(avatar).convert("RGBA").resize((128, 128))

        # modify profile picture to be circular
        mask = Image.new('L', (128, 128), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + (128, 128), fill=255)
        avatar = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
        avatar.putalpha(mask)

        # create the tweet by pasting the profile picture into a white image
        tweet = trans_paste(
            avatar,

            # background
            Image.new('RGBA', (800, 250 + 50 * len(message)), (255, 255, 255)),

            box=(15, 15)
        )

        # add the fonts
        font = ImageFont.truetype('Segoe UI.ttf', 40)
        font_small = ImageFont.truetype('Segoe UI.ttf', 30)
        font_bold = ImageFont.truetype('Segoe UI Bold.ttf', 40)

        # write the name and username on the Image
        draw = ImageDraw.Draw(tweet)
        draw.text((180, 20), str(ctx.author.user), fill=(0, 0, 0),
                  font=font_bold)
        draw.text((180, 70), '@' + ctx.author.user.username, fill=(120, 120, 120),
                  font=font)

        # write the content of the tweet on the Image
        message = '\n'.join(message).split(' ')
        result = []

        # generate a dict to set were the text need to be in different color.
        # for example, if a word starts with '@' it will be write in blue.
        # example:
        #   [
        #       {'color': (0, 0, 0), 'text': 'hello world '},
        #       {'color': (0, 154, 234), 'text': '@drawbu'}
        #   ]
        for word in message:
            for i_o, o in enumerate(word.split('\n')):

                o += '\n' if i_o != len(word.split('\n')) - 1 else ' '

                if not result:
                    result.append({'color': (0, 0, 0), 'text': o})
                    continue

                if not o.startswith('@'):
                    if result[-1:][0]['color'] == (0, 0, 0):
                        result[-1:][0]['text'] += o
                        continue

                    result.append({'color': (0, 0, 0), 'text': o})
                    continue

                result.append({'color': (0, 154, 234), 'text': o})

        # write the text
        draw = ImageDraw.Draw(tweet)
        x = 30
        y = 170
        for o in result:
            y -= font.getsize(' ')[1]
            for l_index, line in enumerate(o['text'].split('\n')):
                if l_index != 0:
                    x = 30
                y += font.getsize(' ')[1]
                draw.text((x, y), line, fill=o['color'], font=font)
                x += font.getsize(line)[0]

        # write the footer
        draw.text(
            (30, tweet.size[1] - 60),
            datetime.now().strftime(
                '%I:%M %p · %d %b. %Y · Twitter for Discord'),
            fill=(120, 120, 120),
            font=font_small)

        return Message(
            embeds=[
                Embed(
                    title='Twitter for Discord',
                    description=''
                ).set_image(url="attachment://image0.png")
            ],
            attachments=[tweet]
        )


# https://stackoverflow.com/a/53663233/15485584
def trans_paste(fg_img, bg_img, alpha=1.0, box=(0, 0)):
    """
    paste an image into one another
    """
    fg_img_trans = Image.new("RGBA", fg_img.size)
    fg_img_trans = Image.blend(fg_img_trans, fg_img, alpha)
    bg_img.paste(fg_img_trans, box, fg_img_trans)
    return bg_img


if __name__ == "__main__":
    # Of course we have to run our client, you can replace the
    # XXXYOURBOTTOKENHEREXXX with your token, or dynamically get it
    # through a dotenv/env.
    Bot("XXXYOURBOTTOKENHEREXXX").run()
