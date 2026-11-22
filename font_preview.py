import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
S=sys.argv[1]; F=S+'/fonts/'; Y=(255,226,122)
def font(name,size,var=None):
    f=ImageFont.truetype(F+name,size)
    if var: f.set_variation_by_name(var)
    return f
PS=lambda s,v='Italic': font('PublicSans-Italic%5Bwght%5D.ttf',s,v)
bg=Image.open(S+'/bg.png').convert('RGB').resize((576,1024))
reg=bg.crop((100,280,476,360)).filter(ImageFilter.GaussianBlur(14)); bg.paste(reg,(100,280))
bg=ImageEnhance.Brightness(bg).enhance(0.8)
def text(img,xy,s,f,fill,anchor='mm',shadow=6,track=0):
    def draw(d,col):
        if not track: d.text(xy,s,font=f,fill=col,anchor=anchor); return
        w=sum(f.getlength(c) for c in s)+track*(len(s)-1); x=xy[0]-w/2
        for c in s: d.text((x,xy[1]),c,font=f,fill=col,anchor='lm'); x+=f.getlength(c)+track
    sh=Image.new('RGBA',img.size,(0,0,0,0)); draw(ImageDraw.Draw(sh),(0,0,0,170))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(shadow)))
    draw(ImageDraw.Draw(img),fill)
def card(p,lines,f,y=460):
    d=ImageDraw.Draw(p); h=40*len(lines)+30
    d.rounded_rectangle((70,y-h//2,506,y+h//2),14,fill=(255,250,235,235))
    for i,l in enumerate(lines): d.text((288,y-h//2+35+40*i),l,font=f,fill=(40,40,40),anchor='mm')
def emph(p,f2):
    f1=font('BootzyTM.ttf',56)
    text(p,(288,420),'the',f1,'white',track=4); text(p,(288,495),'perfect',f2,Y); text(p,(288,575),'suit',f1,'white',track=4)
def panel(label,accent):
    p=bg.convert('RGBA'); d=ImageDraw.Draw(p)
    d.rounded_rectangle((16,16,560,64),12,fill=(0,0,0,190))
    d.text((288,40),label,font=PS(22,'Bold Italic'),fill='white',anchor='mm')
    text(p,(288,150),'AbsolutLEE I DO',font('BootzyTM.ttf',62),Y,track=4)
    text(p,(288,212),'wedding diaries · ep 1',PS(26,'SemiBold Italic'),'white',shadow=3)
    accent(p)
    text(p,(288,840),"first fitting and i'm already sold",PS(30,'SemiBold Italic'),'white',shadow=4)
    return p
L=['bangkok · 3 fittings','5 days · thb 18,000']
panels=[
 ('A · SCRIPT (Great Vibes)', lambda p: text(p,(288,480),'so dapper',font('GreatVibes-Regular.ttf',110),Y)),
 ('B · SERIF ITALIC (Playfair)', lambda p: emph(p,font('PlayfairDisplay-Italic%5Bwght%5D.ttf',76,'Bold Italic'))),
 ('C · TYPEWRITER (Courier Prime)', lambda p: card(p,L,font('CourierPrime-Regular.ttf',28))),
 ('D · BE VIETNAM PRO (italic)', lambda p: card(p,L,font('BeVietnamPro-BoldItalic.ttf',30))),
 ('E · NOTO SERIF (italic)', lambda p: emph(p,font('NotoSerif-Italic.ttf',72,'SemiBold Italic'))),
]
ps=[panel(l,a) for l,a in panels]
out=Image.new('RGB',(576*5+80,1024),(20,20,20))
for i,p in enumerate(ps): out.paste(p.convert('RGB'),(i*596,0))
out=out.resize((out.width*2//3,out.height*2//3),Image.LANCZOS)
out.save('/home/user/capcut/accent-fonts-preview-v2.png')
