"""Original editorial renderer; Pillow is a build-time dependency only.

Reads independently sourced story data. No network, competitor artwork, logos,
or downloaded fonts are used. The submitted main.py copies the frozen PNG.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image
from make_image import Painter, icon, INK, MUTED, WHITE, RULE, PAPER, font

COLORS = ['#276F8C', '#AF4C33', '#327D68', '#665381', '#A17422', '#466C45']


def fit(p, text, x, y, width, size, minimum, lines, color=INK, bold=False, max_height=None):
    for candidate in range(size, minimum - 1, -1):
        words, current, wrapped = text.split(), '', []
        for word in words:
            test = (current + ' ' + word).strip()
            if font(candidate, 'bold' if bold else 'regular').getlength(test) / 2 <= width:
                current = test
            else:
                if current:
                    wrapped.append(current)
                current = word
        if current:
            wrapped.append(current)
        if len(wrapped) <= lines and (max_height is None or round(candidate * 1.16) * len(wrapped) <= max_height):
            height = p.wrapped((x, y), text, candidate, width, color,
                               'bold' if bold else 'regular', lines)
            return height
    raise ValueError(f'Text cannot fit without sacrificing legibility: {text}')


def new_icon(p, key, x, y, w, h, color):
    if key in ('bridge', 'climate', 'markets', 'trade', 'port', 'food'):
        icon(p, key, x, y, w, h, color)
        return
    def pt(a, b):
        return (x + a * w / 100, y + b * h / 80)
    def line(points, weight=3, shade=color):
        p.line([pt(*v) for v in points], shade, weight)
    def box(a,b,c,d,fill=color):
        p.rect((*pt(a,b),*pt(c,d)),fill)
    if key == 'storm':
        for radius, offset in [(30, 0), (23, 1.5), (15, 3)]:
            points = []
            for i in range(60):
                t=i/59 * math.pi * 1.7 + offset
                points.append((50 + radius*math.cos(t), 34 + radius*.7*math.sin(t)))
            line(points,4)
        p.ellipse((*pt(45,29),*pt(55,39)),WHITE,color,2)
        line([(10,68),(25,62),(40,68),(55,62),(70,68),(90,63)],3,'#7EABB8')
    elif key == 'sport':
        box(23,10,32,63);box(44,10,53,63);box(65,10,74,63)
        line([(20,9),(77,9)],4)
        p.ellipse((*pt(75,49),*pt(94,67)),color)
    elif key == 'energy':
        line([(22,67),(51,9),(79,67)],4)
        for t in (30,43,57):
            line([(34,t),(67,t)],3)
        line([(15,68),(89,68)],4)
        p.ellipse((*pt(45,14),*pt(57,26)),WHITE,color,2)
    elif key == 'diplomacy':
        for a in (24,64):
            line([(a,70),(a,9)],3)
            p.polygon([pt(a,10),pt(a+25,15),pt(a+25,37),pt(a,32)],color)
        line([(15,73),(91,73)],3)
    elif key == 'science':
        line([(38,10),(61,10)],4)
        line([(43,11),(43,37),(21,67),(79,67),(57,37),(57,11)],3)
        line([(30,55),(69,55)],3)
        p.ellipse((*pt(44,45),*pt(51,52)),color)
    elif key == 'fuel':
        p.rect((*pt(20,12),*pt(63,66)),WHITE,color,3,5)
        box(28,21,55,37)
        line([(63,26),(79,33),(79,60),(71,60),(71,47)],4)
        line([(15,69),(70,69)],4)
    else:
        # A schematic location marker, not a geographic claim or a map.
        p.ellipse((*pt(29,9),*pt(73,51)),None,color,4)
        p.polygon([pt(33,44),pt(69,44),pt(51,72)],color)
        p.ellipse((*pt(44,23),*pt(58,37)),WHITE)


def masthead(p, count):
    p.text((30,21),'WORLD / THE DAILY PICTURE',18,INK,'bold')
    p.text((28,52),'21 November 2026',67,INK,'bold')
    p.text((32,130),f'SATURDAY  |  {count} REPORTED DEVELOPMENTS  |  ONE DAY, WORLDWIDE',16,MUTED,'bold')
    p.line([(30,159),(994,159)],INK,2)


def panel(p, story, n, bounds, lead=False):
    x,y,w,h=bounds
    color=COLORS[n % len(COLORS)]
    p.rect((x,y,x+w,y+h),WHITE,RULE,1,8)
    p.rect((x,y,x+5,y+h),color,radius=2)
    fit(p,f'{n+1:02d}  {story["region"]}',x+15,y+12,w-84 if not lead else w-30,
        13,10,1,color=color,bold=True)
    top=y+39
    source_y=y+h-21
    if lead:
        new_icon(p,story['key'],x+w-77,y+27,58,39,color)
        title_y=y+73
        title_h=fit(p,story['title'],x+15,title_y,w-30,36,32,2,bold=True)
        body_y=title_y+title_h+12
        body_h=fit(p,story['deck'],x+15,body_y,w-30,21,18,4,
                   max_height=source_y-body_y-7)
        source_size=13
    else:
        # Fit the region label beside the icon instead of obscuring its text.
        new_icon(p,story['key'],x+w-67,y+6,47,31,color)
        title_h=fit(p,story['title'],x+15,top,w-30,24,21,2,bold=True)
        body_y=top+title_h+8
        body_h=fit(p,story['deck'],x+15,body_y,w-30,18,14,4,
                   max_height=source_y-body_y-7)
        source_size=12
    if body_y+body_h > source_y-6:
        raise ValueError(f'Body-source collision in story {n+1}: {body_y+body_h} > {source_y-6}')
    fit(p,story['sources'],x+15,source_y,w-30,source_size,11,1,color=MUTED)
    p.layout_checks.append({'story':n+1,'title':story['title'],'bounds':list(bounds),
                            'body_source_gap':source_y-(body_y+body_h)})


def briefs(p, stories, first, y, height):
    p.rect((30,y,994,y+height),'#E3EBE8',radius=8)
    p.text((45,y+12),'ALSO REPORTED / THE WORLD BEYOND THE HEADLINES',15,INK,'bold')
    width=460
    for i,story in enumerate(stories[first:]):
        col=i % 2; row=i//2
        x=45+col*480; top=y+40+row*39
        text=f'{first+i+1:02d}  {story["brief"]} ({story["brief_source"]})'
        fit(p,text,x,top,width,16,15,2)
        if top+36>y+height-6:
            raise ValueError('Briefs overflow')


def render(stories, variant, output):
    if len(stories)<12 or len(stories)>18:
        raise ValueError('Need 12–18 verified stories, not invented filler.')
    p=Painter(PAPER)
    count=12 if variant=='A' else min(len(stories),15)
    masthead(p,count)
    if variant=='A':
        for i,story in enumerate(stories[:12]):
            row,col=divmod(i,3)
            panel(p,story,i,(30+col*326,174+row*199,312,187))
    elif variant=='B':
        for i,story in enumerate(stories[:3]):
            panel(p,story,i,(30+i*326,174,312,272),True)
        for i,story in enumerate(stories[3:9],3):
            row,col=divmod(i-3,3)
            panel(p,story,i,(30+col*326,459+row*181,312,169))
        briefs(p,stories[:15],9,827,164)
    elif variant=='C':
        for i,story in enumerate(stories[:2]):
            panel(p,story,i,(30+i*489,174,475,242),True)
        for i,story in enumerate(stories[2:10],2):
            row,col=divmod(i-2,4)
            panel(p,story,i,(30+col*244.5,429+row*195,231,188))
        briefs(p,stories[:15],10,820,171)
    else:
        raise ValueError(variant)
    p.text((33,1004),'Events / first reports on this date. Sources named per story; claims attributed. Original drawings.',12,MUTED)
    output.parent.mkdir(parents=True,exist_ok=True)
    final=p.image.resize((1024,1024),Image.Resampling.LANCZOS)
    final.save(output,'PNG',optimize=True,compress_level=9)
    final.resize((300,300),Image.Resampling.LANCZOS).save(output.with_name(output.stem+'-300.png'))
    return {'variant':variant,'stories':count,'bytes':output.stat().st_size,
            'text_boxes':p.text_checks,'layout_checks':p.layout_checks}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stories',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--variant',choices=['A','B','C','all'],default='all')
    args=ap.parse_args()
    stories=json.loads(args.stories.read_text(encoding='utf-8'))
    variants=['A','B','C'] if args.variant=='all' else [args.variant]
    reports=[]
    for variant in variants:
        reports.append(render(stories,variant,args.out/f'revision-{variant}.png'))
    (args.out/'render-report.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
    print(json.dumps([{'variant':r['variant'],'stories':r['stories'],'bytes':r['bytes']} for r in reports]))


if __name__=='__main__':
    main()
