import os

# ==========================================
# 1. SETUP & PATHS (SILENCING SKIDL WARNINGS)
# ==========================================
app_symbols = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols'
app_footprints = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints'
user_config = '/Users/softage/Documents/KiCad/8.0'

os.environ['KICAD_SYMBOL_DIR'] = app_symbols
os.environ['KICAD6_SYMBOL_DIR'] = app_symbols
os.environ['KICAD7_SYMBOL_DIR'] = app_symbols
os.environ['KICAD8_SYMBOL_DIR'] = app_symbols
os.environ['KICAD9_SYMBOL_DIR'] = app_symbols

os.environ['KICAD_FOOTPRINT_DIR'] = app_footprints
os.environ['KICAD8_FOOTPRINT_DIR'] = app_footprints

from skidl import *

lib_search_paths[KICAD].extend([app_symbols, user_config])
footprint_search_paths[KICAD].append(app_footprints)

set_default_tool(KICAD)

# ==========================================
# 2. GLOBAL NETS
# ==========================================
gnd, vbus = Net('GND'), Net('VBUS')
v3v3, v1v1, v1v8 = Net('+3V3'), Net('+1V1'), Net('+1V8')

# ==========================================
# 3. POWER MANAGEMENT & PRECISE FILTERING
# ==========================================
u10 = Part('Regulator_Linear', 'NCP1117-3.3_SOT223', footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')
u10[1, 2, 3] += gnd, v3v3, vbus
c100 = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0805_2012Metric')
c400 = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0805_2012Metric')
c100[1, 2] += vbus, gnd
c400[1, 2] += v3v3, gnd

v2 = Part('Regulator_Linear', 'AMS1117-1.8', footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')
v2[1, 2, 3] += gnd, v1v8, v3v3

# FIXED: Added the two 10uF caps for the 1.8V regulator shown in the schematic
c_1v8_in = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0805_2012Metric')
c_1v8_out = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0805_2012Metric')
c_1v8_in[1, 2] += v3v3, gnd
c_1v8_out[1, 2] += v1v8, gnd

# Specific rail decoupling
c6, c7 = [Part('Device', 'C', value='100n', footprint='Capacitor_SMD:C_0402_1005Metric') for _ in range(2)]
c6[1, 2] += v1v1, gnd
c7[1, 2] += v1v1, gnd

c8, c10 = [Part('Device', 'C', value='1u', footprint='Capacitor_SMD:C_0603_1608Metric') for _ in range(2)]
c8[1, 2] += v3v3, gnd  
c10[1, 2] += v3v3, gnd 

# FIXED: Changed range from 5 to 6 to match C9, C11, C12, C13, C14, C15
c_3v3 = [Part('Device', 'C', value='100n', footprint='Capacitor_SMD:C_0402_1005Metric') for _ in range(6)]
for c in c_3v3: 
    c[1, 2] += v3v3, gnd

# ==========================================
# 4. MICROCONTROLLER: RP2040 (U3)
# ==========================================
mcu = Part('MCU_RaspberryPi', 'RP2040', footprint='Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm')
mcu['IOVDD.*', 'USB_VDD', 'ADC_AVDD', 'VREG_IN'] += v3v3
mcu['DVDD.*', 'VREG_VOUT'] += v1v1
mcu['GND', 'TESTEN'] += gnd

# ==========================================
# 5. BOOT/RESET CIRCUIT 
# ==========================================
r100 = Part('Device', 'R', value='1k', footprint='Resistor_SMD:R_0402_1005Metric')
r200 = Part('Device', 'R', value='10k', footprint='Resistor_SMD:R_0402_1005Metric')
usb_boot = Net('USB_BOOT')

mcu['RUN'] += r200[1]
r200[2] += v3v3 
qspi_ss = Net('QSPI_SS')
qspi_ss += mcu['QSPI_SS'], r100[1]
r100[2] += usb_boot

# FIXED: Added the physical Boot switch shown in the schematic
sw_boot = Part('Switch', 'SW_Push', footprint='Button_Switch_SMD:SW_SPST_B3U-1000P')
sw_boot[1, 2] += usb_boot, gnd

# ==========================================
# 6. FLASH MEMORY (U4)
# ==========================================
flash = Part('Memory_Flash', 'W25Q32JVSS', footprint='Package_SO:SOIC-8_5.23x5.23mm_P1.27mm')
flash[8, 4] += v3v3, gnd 
flash[1] += qspi_ss
flash[6] += mcu['QSPI_SCLK']
flash[5, 2, 3, 7] += mcu['QSPI_SD0', 'QSPI_SD1', 'QSPI_SD2', 'QSPI_SD3']

# ==========================================
# 7. CRYSTAL CIRCUIT 
# ==========================================
xtal = Part('Device', 'Crystal_GND24', value='12MHz', footprint='Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm')
c200 = Part('Device', 'C', value='15p', footprint='Capacitor_SMD:C_0402_1005Metric')
c300 = Part('Device', 'C', value='15p', footprint='Capacitor_SMD:C_0402_1005Metric')
r500 = Part('Device', 'R', value='1k', footprint='Resistor_SMD:R_0402_1005Metric')

xtal[2, 4] += gnd
mcu['XIN'] += xtal[1], c200[1]
mcu['XOUT'] += r500[1]
r500[2] += xtal[3], c300[1]
gnd += c200[2], c300[2]

# ==========================================
# 8. ROTARY ENCODER 
# ==========================================
enc_tmpl = Part('Device', 'R', dest=TEMPLATE) 
enc_tmpl.name = 'Rotary_Encoder'
enc_tmpl.ref_prefix = 'SW'
enc_tmpl.footprint = 'Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm'
enc_tmpl.pins = [
    Pin(num='A', name='A'),
    Pin(num='B', name='B'),
    Pin(num='C', name='C')
]

encoder = enc_tmpl()
mcu['GPIO8'] += encoder['A']
mcu['GPIO10'] += encoder['B'] 
mcu['GPIO9'] += encoder['C']

# ==========================================
# 9. OPTICAL SENSOR & LED 
# ==========================================
u2_tmpl = Part('Device', 'R', dest=TEMPLATE) 
u2_tmpl.name = 'PMW3360DM'
u2_tmpl.ref_prefix = 'U'
u2_tmpl.footprint = 'OptoDevice:PixArt_PMW3360DM-T2QU' 
# FIXED: Updated pin numbers to match the schematic exactly
u2_tmpl.pins = [
    Pin(num='3', name='VDDPIX'), Pin(num='4', name='VDD'), Pin(num='5', name='VDDIO'), Pin(num='8', name='GND'),
    Pin(num='12', name='MISO'), Pin(num='11', name='MOSI'), Pin(num='10', name='SCLK'), 
    Pin(num='13', name='NCS'), Pin(num='9', name='MOTION'), Pin(num='7', name='LED_P')
]

sensor = u2_tmpl()
sensor['VDDPIX', 'VDD'] += v1v8, v1v8
sensor['VDDIO'] += v3v3
sensor['GND'] += gnd
sensor['MISO', 'MOSI', 'SCLK', 'NCS'] += mcu['GPIO16', 'GPIO19', 'GPIO18', 'GPIO17']
sensor['MOTION'] += mcu['GPIO15']

# FIXED: Added the missing 100nF and 4.7uF caps for the sensor power
c_sensor_1 = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0402_1005Metric')
c_sensor_2 = Part('Device', 'C', value='4.7uF', footprint='Capacitor_SMD:C_0603_1608Metric')
c_sensor_1[1, 2] += v1v8, gnd
c_sensor_2[1, 2] += v1v8, gnd

led_3360 = Part('Device', 'LED', footprint='LED_SMD:LED_0805_2012Metric')
r39 = Part('Device', 'R', value='10k', footprint='Resistor_SMD:R_0402_1005Metric')
sensor['LED_P'] += r39[1]
r39[2] += gnd
led_3360[1, 2] += v3v3, sensor['LED_P'] 

# ==========================================
# 10. BUTTON MATRIX 
# ==========================================
mb_a, mb_b = Net('MB_A'), Net('MB_B')
sw_gpios = ['GPIO2', 'GPIO3', 'GPIO4', 'GPIO5', 'GPIO6', 'GPIO7']

for i, gpio_name in enumerate(sw_gpios):
    sw = Part('Switch', 'SW_SPDT', footprint='Button_Switch_SMD:SW_SPDT_PCM12') 
    d1 = Part('Device', 'D', footprint='Diode_SMD:D_SOD-123')
    d2 = Part('Device', 'D', footprint='Diode_SMD:D_SOD-123')
    m_net = Net(f'M{i+1}')
    
    sw[2] += m_net
    mcu[gpio_name] += m_net
    sw[1] += d1[1]; d1[2] += mb_a
    sw[3] += d2[1]; d2[2] += mb_b

# ==========================================
# 11. USB CONNECTOR & DATA
# ==========================================
usb_tmpl = Part('Device', 'R', dest=TEMPLATE) 
usb_tmpl.name = 'USB_C_Receptacle'
usb_tmpl.ref_prefix = 'J'
usb_tmpl.footprint = 'Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12'
usb_tmpl.pins = [
    Pin(num='1', name='VBUS'), Pin(num='2', name='GND'),
    Pin(num='3', name='DP1'), Pin(num='4', name='DP2'),
    Pin(num='5', name='DN1'), Pin(num='6', name='DN2')
]

usb = usb_tmpl()
r_usb_p = Part('Device', 'R', value='27', footprint='Resistor_SMD:R_0603_1608Metric')
r_usb_n = Part('Device', 'R', value='27', footprint='Resistor_SMD:R_0603_1608Metric')

usb['VBUS'] += vbus
usb['GND'] += gnd
usb['DP1', 'DP2'] += r_usb_p[2]
usb['DN1', 'DN2'] += r_usb_n[2]

mcu['USB_DP'] += r_usb_p[1]
mcu['USB_DM'] += r_usb_n[1]
import csv
from collections import defaultdict

# ==========================================
# 12. OUTPUT & BOM GENERATION
# ==========================================
def generate_csv_bom(filename='mouse_bom.csv'):
    """Extracts all components from the SKiDL circuit and groups them into a CSV."""
    
    bom_groups = defaultdict(list)
    
    for part in default_circuit.parts: # type: ignore
        # FIXED: Using getattr() safely checks for 'dest' and 'ref' without crashing if they don't exist
        is_template = getattr(part, 'dest', None) == TEMPLATE # type: ignore
        has_no_ref = not getattr(part, 'ref', None)
        
        if is_template or has_no_ref:
            continue
            
        name = part.name
        value = getattr(part, 'value', '')
        footprint = getattr(part, 'footprint', '')
        
        key = (name, value, footprint)
        bom_groups[key].append(part.ref)
        
    with open(filename, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Quantity', 'Reference(s)', 'Value', 'Part Name', 'Footprint'])
        
        for (name, value, footprint), refs in bom_groups.items():
            refs.sort() 
            ref_string = ", ".join(refs)
            qty = len(refs)
            writer.writerow([qty, ref_string, value, name, footprint])
            
    print(f"✅ BOM successfully saved to: {filename}")

# Generate the KiCad Netlist
generate_netlist(filename='mouse_final_v13.net')

# Generate the Excel-ready BOM
generate_csv_bom(filename='mouse_final_BOM.csv')
