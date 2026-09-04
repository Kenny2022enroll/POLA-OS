#注意：在导入devlib后请不要导入mpython，否则会报错，反过来也是，在导入mpython后请不要导入devlib，否则会报错
#
# POLA-OS 定制版（slim）：只保留本系统实际使用的硬件：
#   OLED(SSD1106) / 六个触摸金手指 / 光线传感器
# 上游 devlib 中的 MOTION(加速度计/陀螺仪)、地磁传感器、RGB LED、
# 声音传感器、按键A/B 在 POLA-OS 中均未使用，已整体移除以节省运行内存。
# 如需完整外设驱动，请换回上游版本：https://github.com/emofalling/devlib
# DispChar 亦做了同步精简：POLA-OS 只使用默认渲染模式，未文档化的
# 反色/填充/透明等模式分支已移除（mode=0 跳过、默认绘制保持不变）。

from machine import Pin,I2C,TouchPad,ADC
from esp import flash_read
from ssd1106 import SSD1106_I2C
from framebuf import FrameBuffer
import ustruct

overclock=True
if overclock:
    i2cclock=1250000
else:
    i2cclock= 400000
i2c = I2C(0, scl=Pin(Pin.P19), sda=Pin(Pin.P20), freq=i2cclock)

font_address=0x400000
maximum_fontbitmaplen=64
class OLED(SSD1106_I2C):
    def __init__(self,addr):
        super().__init__(128,64,i2c,addr,external_vcc=True) #VDD=3.3v,且掌控板自带的稳压器带载能力通常比OLED内置的稳压器更好,所以使用external_vcc=True
        #将Font对象集成在OLED内，提高速度
        self.font_addr=font_address
        buffer = bytearray(18)
        flash_read(self.font_addr, buffer)
        self.font_header,\
        self.font_height,\
        self.font_width,\
        self.font_baseline,\
        self.font_x_height,\
        self.font_y_height,\
        self.font_first_char,\
        self.font_last_char = ustruct.unpack('4sHHHHHHH', buffer)
        del buffer
        self.font_lenbuffer=bytearray(6)
        self.font_infobuffer=bytearray(4)
        self.font_bitmapbuffer=bytearray(maximum_fontbitmaplen)
        if self.font_header != b"GUIX":
            print("Font Error: Invalid font header: {}".format(self.font_header))
    def DispChar(self,s,x,y,*,maximum_x=128,space=1,newlinecode=True,return_x=0,return_addy=16):
        # POLA-OS 精简版：只保留默认绘制（mode=1/out=1）行为——逐字绘制、
        # 超出 maximum_x 停止、支持换行。未文档化的测量/多模式参数已移除。
        char_x=x
        char_y=y
        char_h=self.font_height
        lenbuffer=self.font_lenbuffer
        infobuffer=self.font_infobuffer
        bitmapbuffer=self.font_bitmapbuffer

        framebuffer=FrameBuffer
        flashread=flash_read
        unpack=ustruct.unpack

        firstchar=self.font_first_char
        lastchar=self.font_last_char
        charaddr=self.font_addr
        first_char_info_address = charaddr + 18
        blit=self.blit

        for char in s:
            uni=ord(char)
            if uni==10 and newlinecode: #ord("\n")
                char_x=return_x
                char_y+=return_addy
                continue
            if firstchar>uni or lastchar<uni:
                continue
            flashread(first_char_info_address + (uni - firstchar) *6, lenbuffer)
            ptr_char_data, len = unpack('IH', lenbuffer)
            if not (ptr_char_data and len):
                continue
            addr_len = ptr_char_data + charaddr
            flashread(addr_len, infobuffer)
            char_w,_ = unpack('HH', infobuffer)
            flashread(addr_len+4,bitmapbuffer)
            fbuf=framebuffer(bitmapbuffer,char_w,char_h,3)#framebuf.MONO_HLSB = 3
            blit(fbuf,char_x,char_y)
            char_x+=char_w+space
            if char_x>maximum_x:
                break

if 60 in i2c.scan():
    oled = OLED(60)
    display = oled
else:
    pass

# light sensor
light = ADC(Pin(39))
light.atten(light.ATTN_11DB)

#touchpads
# POLA-OS 通过 .read() 轮询触摸值，无需中断封装，直接使用 TouchPad。
touchpad_p = touchPad_P = TouchPad(Pin(27))#Pin.P23
touchpad_y = touchPad_Y = TouchPad(Pin(14))#Pin.P24
touchpad_t = touchPad_T = TouchPad(Pin(12))#Pin.P25
touchpad_h = touchPad_H = TouchPad(Pin(13))#Pin.P26
touchpad_o = touchPad_O = TouchPad(Pin(15))#Pin.P27
touchpad_n = touchPad_N = TouchPad(Pin(4)) #Pin.P28
