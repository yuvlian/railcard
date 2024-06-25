from img_utils import create_dark_block, create_light_block, create_relic_background, create_rounded_mask, img_from_url
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageChops
from mihomo import Character, Player, StarrailInfoParsed
from utils import comb_stats, combine_attr_fields, get_atk_boosts, get_config, search, sort_fields

config = get_config()

def create_card(data: StarrailInfoParsed, chara_index: int, img_url: str | None = None) -> Image.Image:
    ch = data.characters[chara_index]
    img = create_dark_block(1520, 1338)

    render_char_img(img, ch, img_url)
    render_eidolon(img, ch)
    render_trace(img, ch)
    render_path(img, ch)
    render_user(img, data.player)
    render_lc(img, ch)
    render_stats(img, ch)
    render_relics(img, ch)
    return img

def render_char_img(img: Image, ch: Character, img_url: str | None):
    print("Rendering character image...")
    bg = create_light_block(650, 716, "RGB")
    im = None

    if img_url:
        try:
            im = img_from_url(img_url)
            print("Image used: [Custom], Continue rendering..")
        except:
            print("Failed to fetch image from URL. Try using Discord for the image host.")
            print("Image used: [Default], Continue rendering..")
            im = img_from_url(ch.preview)
    else: im = img_from_url(ch.preview)

    chara = ImageOps.fit(im, (650, 716), centering=(0.5, 0.5))
    bg.paste(chara, (0, 0), chara if chara.mode == "RGBA" else None)

    fnt = ImageFont.truetype(config["fontFile"], 62)
    dr = ImageDraw.Draw(bg)
    dr.text((19, 5), ch.name, font=fnt, stroke_fill=(26, 26, 26), stroke_width=2)

    fnt = ImageFont.truetype(config["fontFile"], 31)
    dr.text((22, 72), f"Lv. {ch.level}/{ch.max_level}", font=fnt, stroke_fill=(26, 26, 26), stroke_width=2)

    # Parameters for outlining
    outline_width = 3  # width of the outline
    outline_color = (26, 26, 26)  # color of the outline
    element_icon_url = ch.element.icon  # URL of the element icon

    # Resize the image for the outline
    outline_size = (115 + outline_width * 2, 115 + outline_width * 2)
    element_img = img_from_url(element_icon_url)
    outline_img = ImageOps.fit(element_img, outline_size)

    # Create a new image for the outline
    outlined_img = Image.new('RGBA', outline_size, (255, 255, 255, 0))

    # Draw the outline by pasting the resized image in the outline color
    draw = ImageDraw.Draw(outlined_img)
    draw.bitmap((0, 0), outline_img, fill=outline_color)

    # Paste the original image on top of the outline
    main_element_img = ImageOps.fit(element_img, (115, 115))
    outlined_img.paste(main_element_img, (outline_width, outline_width), main_element_img)

    # Paste the outlined element image onto the background image
    bg.paste(outlined_img, (19, 108), outlined_img)

    bgmask = create_rounded_mask(bg.size, 15)
    img.paste(bg, (30, 30), bgmask)

def render_eidolon(img: Image, ch: Character):
    print("Rendering eidolon bar...")
    eidolonbar = create_light_block(124, 487)

    for i, icon in enumerate(ch.eidolon_icons):
        eidolon = ImageOps.fit(img_from_url(icon), (71, 71))
        to_paste = eidolon if i < ch.eidolon else ImageChops.multiply(eidolon, Image.new("RGBA", eidolon.size, (256, 256, 256, 50)))
        eidolonbar.paste(to_paste, (26, 7 + i * (71+10)), to_paste)

    eidolonbarmask = create_rounded_mask(eidolonbar.size, 15)
    img.paste(eidolonbar, (30+650+18, 30), eidolonbarmask)

def render_trace(img: Image, ch: Character):
    print("Rendering trace bar...")
    tracebar = create_light_block(124, 330)

    for i, s in enumerate(["Basic ATK", "Talent", "Skill", "Ultimate"]):
        trace = [x for x in ch.traces if x.type_text == s][0]
        traceimg = ImageOps.fit(img_from_url(trace.icon), (71, 71))

        fnt = ImageFont.truetype(config["fontFile"], 35);
        dr = ImageDraw.Draw(traceimg)

        text = f"{trace.level}"
        size = dr.textlength(text, fnt)
        dr.text((71-size, 71-35), text, font=fnt, stroke_fill=(26, 26, 26), stroke_width=2)

        tracebar.paste(traceimg, (26, 9 + i * (71+10)), traceimg)

    tracebarmask = create_rounded_mask(tracebar.size, 15)
    img.paste(tracebar, (30+650+18, 30+487+18), tracebarmask)

def render_path(img: Image, ch: Character):
    print("Rendering path bar...")
    pathbar = create_light_block(157, 100)
    path = ImageOps.fit(img_from_url(ch.path.icon), (79, 79))

    pathbar.paste(path, (39, 10), path)

    pathbarmask = create_rounded_mask(pathbar.size, 15)
    img.paste(pathbar, (30, 30+716+18), pathbarmask)

def render_user(img: Image, player: Player):
    print("Rendering user bar...")
    usernamebar = create_light_block(475, 100)
    dr = ImageDraw.Draw(usernamebar)

    fnt = ImageFont.truetype(config["fontFile"], 35);
    dr.multiline_text((30, 12.5), f"USER: {player.name}\nUID: {player.uid}", font=fnt)

    usernamebarmask = create_rounded_mask(usernamebar.size, 15)
    img.paste(usernamebar, (30+157+18, 30+716+18), usernamebarmask)

def render_lc(img: Image, ch: Character):
    print("Rendering light cone bar...")
    lcbar = create_light_block(650, 216)
    lc = ch.light_cone

    if lc:
        # Light cone preview
        lcprev = ImageOps.fit(img_from_url(lc.preview), (216, 216), centering=(0, 0))
        lcbar.paste(lcprev, (0, 0), lcprev)

        # Light cone name
        fnt = ImageFont.truetype(config["fontFile"], 35);
        dr = ImageDraw.Draw(lcbar)
        dr.text((216+13, 20), lc.name, font=fnt)

        # Light cone base attributes
        acc = 0
        for i, stat in enumerate(["hp", "atk", "def"]):
            prop = search(lc.attributes, stat)
            if prop:
                txt = prop.displayed_value
                len = dr.textlength(txt, fnt)
                im = ImageOps.fit(img_from_url(prop.icon), (57, 57))

                w = 57+5+int(len)+5
                block = create_dark_block(w, 57)
                drb = ImageDraw.Draw(block)

                block.paste(im, (0, 0), im)
                drb.text((57+5, 7), txt, font=fnt)

                blockmask = create_rounded_mask(block.size, 15)
                lcbar.paste(block, (216+13+acc+i*5, 20+35+16), blockmask)

                acc += w

        # Light cone level
        txt = f"Lv. {lc.level}/{lc.max_level}"
        dr = ImageDraw.Draw(lcbar)
        len = dr.textlength(txt, fnt)

        block = create_dark_block(int(len)+20, 57)
        dr = ImageDraw.Draw(block)
        dr.text((10, 7), txt, font=fnt)

        blockmask = create_rounded_mask(block.size, 15)
        lcbar.paste(block, (216+13, 20+35+16+57+8), blockmask)

        # Light cone superimpose
        txt = f"S{lc.superimpose}"
        dr = ImageDraw.Draw(lcbar)
        len = dr.textlength(txt, fnt)

        block = create_dark_block(int(len)+10, 65)
        dr = ImageDraw.Draw(block)
        dr.text((5, 10), txt, font=fnt)

        blockmask = create_rounded_mask(block.size, 15)
        lcbar.paste(block, (14, 12), blockmask)
    else:
        im = ImageOps.fit(Image.open(config["noLCFile"]), (216, 216))
        lcbar.paste(im, (0, 0), im)

        fnt = ImageFont.truetype(config["fontFile"], 35);
        dr = ImageDraw.Draw(lcbar)
        dr.text((216+13, int(lcbar.height/2 - 35/2)), "No Light Cone", font=fnt)

    lcbarmask = create_rounded_mask(lcbar.size, 15)
    img.paste(lcbar, (30+650+18+124+18, 30), lcbarmask)

def render_stats(img: Image, ch: Character):
    print("Rendering stats bar...")
    statsbar = create_light_block(650, 600)
    small_fnt = ImageFont.truetype(config["fontFile"], 24)

    for small_stat in [
        ["hp", (14, 14)],
        ["def", (14, 14+40+9)],
        ["atk", (14+307+10, 14)],
        ["spd", (14+307+10, 14+40+9)]
    ]:
        stat_block = create_dark_block(307, 40)
        dr = ImageDraw.Draw(stat_block)
        data = search(ch.attributes, small_stat[0]) or search(ch.additions, small_stat[0])
        if data:
            icon = ImageOps.fit(img_from_url(data.icon), (40, 40))
            stat_block.paste(icon, (0, 0), icon)

        dr.text((40, 5), small_stat[0].upper(), font=small_fnt)

        val = comb_stats(ch.attributes, ch.additions, small_stat[0])
        l = dr.textlength(val, small_fnt)
        dr.text((307-l-5, 5), val, font=small_fnt)

        stat_block_mask = create_rounded_mask(stat_block.size, 15)
        statsbar.paste(stat_block, small_stat[1], stat_block_mask)

    big_fnt = ImageFont.truetype(config["fontFile"], 31)

    atk_boosts = get_atk_boosts(ch)
    excluded = [x[0] for x in atk_boosts] + ["hp", "def", "atk", "spd", "all_dmg"]
    other: list[list[str]] = []
    for f in sort_fields(combine_attr_fields(ch.attributes, ch.additions)):
        if len(other) >= 8-len(atk_boosts): break
        if f not in excluded:
            s = search(ch.attributes, f) or search(ch.additions, f)
            other.append([s.field, s.icon, s.name, comb_stats(ch.attributes, ch.additions, f)])

    for i, d in enumerate(other+atk_boosts):
        stat_block = create_dark_block(624, 49)
        dr = ImageDraw.Draw(stat_block)

        icon = ImageOps.fit(img_from_url(d[1]), (40, 40))
        stat_block.paste(icon, (0, 4), icon)

        dr.text((40, 4), d[2], font=big_fnt)

        val = d[3]
        l = dr.textlength(val, big_fnt)
        dr.text((624-l-5, 4), val, font=big_fnt)

        stat_block_mask = create_rounded_mask(stat_block.size, 15)
        statsbar.paste(stat_block, (14, 14+2*(40+9)+i*(49+9)), stat_block_mask)

    statsbarmask = create_rounded_mask(statsbar.size, 15)
    img.paste(statsbar, (30+650+18+124+18, 30+216+18), statsbarmask)

def render_relics(img: Image.Image, ch: Character):
    print("Rendering relics...")
    l = len(ch.relics)
    if l == 0:
        return
    container = Image.new("RGBA", (225*l + 22*(l-1), 426), (0, 0, 0, 0))

    for i, relic in enumerate(ch.relics):
        relicimg = Image.new("RGBA", (225, 426), (0, 0, 0, 0))

        # Relic background
        bg = create_relic_background((225, 426), relic.rarity)

        back = Image.new("RGB", (225, 426), (26, 26, 26))
        back.paste(bg, (0, 0), bg)

        bg_mask = create_rounded_mask(back.size, 15)
        relicimg.paste(back, (0, 0), bg_mask)

        # Relic icon
        relic_icon_img = ImageOps.fit(img_from_url(relic.icon), (207, 113))
        relicimg.paste(relic_icon_img, (9, 0), relic_icon_img)

        # Mainstat outline
        ooutline_width = 3  # width of the outline
        ooutline_color = (26, 26, 26)  # color of the outline

        # Resize the image for the outline
        ooutline_size = (88 + ooutline_width * 2, 88 + ooutline_width * 2)
        ooutline_img = ImageOps.fit(img_from_url(relic.main_affix.icon), ooutline_size)

        # Create a new image for the outline
        outlined_img = Image.new('RGBA', ooutline_size, (255, 255, 255, 0))

        # Draw the outline by pasting the resized image in the outline color
        draw = ImageDraw.Draw(outlined_img)
        draw.bitmap((0, 0), ooutline_img, fill=ooutline_color)

        # Paste the original image on top of the outline
        main_stats_img = ImageOps.fit(img_from_url(relic.main_affix.icon), (88, 88))
        outlined_img.paste(main_stats_img, (ooutline_width, ooutline_width), main_stats_img)

        # Paste the outlined image on the relic image
        relicimg.paste(outlined_img, (0, 0), outlined_img)

        # Relic level 
        fnt = ImageFont.truetype(config["fontFile"], 45)
        dr = ImageDraw.Draw(relicimg)
        level_text = f"+{relic.level}"
        le = dr.textlength(level_text, fnt)
        text_position = (225 - le - 5, 426 - 313 - 5 - 45)
        dr.text(text_position, level_text, font=fnt, stroke_fill=(26, 26, 26), stroke_width=2)

        # Relic sub stats
        sub_stats_img = create_light_block(225, 313)

        for j, sub in enumerate(relic.sub_affixes):
            bar = create_dark_block(207, 57)
            dr = ImageDraw.Draw(bar)

            icon = ImageOps.fit(img_from_url(sub.icon), (57, 57))
            bar.paste(icon, (0, 0), icon)

            fnt = ImageFont.truetype(config["fontFile"], 31)
            le = dr.textlength(sub.displayed_value, fnt)
            dr.text((207-le-5, 10), sub.displayed_value, font=fnt)

            bar_mask = create_rounded_mask(bar.size, 15)
            sub_stats_img.paste(bar, (9, 16+j*(57+17)), bar_mask)

        sub_stats_mask = create_rounded_mask(sub_stats_img.size, 15)
        relicimg.paste(sub_stats_img, (0, 113), sub_stats_mask)
        container.paste(relicimg, (i*(225+22), 0), relicimg)

    img.paste(container, (int(img.width/2-container.width/2), 30+716+18+100+18), container)
