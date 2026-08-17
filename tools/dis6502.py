"""Minimal 6502 disassembler."""
import sys

# opcode -> (mnemonic, addressing mode)
OPS = {
0x00:("BRK","imp"),0x01:("ORA","izx"),0x05:("ORA","zp"),0x06:("ASL","zp"),0x08:("PHP","imp"),0x09:("ORA","imm"),0x0A:("ASL","acc"),0x0D:("ORA","abs"),0x0E:("ASL","abs"),
0x10:("BPL","rel"),0x11:("ORA","izy"),0x15:("ORA","zpx"),0x16:("ASL","zpx"),0x18:("CLC","imp"),0x19:("ORA","absy"),0x1D:("ORA","absx"),0x1E:("ASL","absx"),
0x20:("JSR","abs"),0x21:("AND","izx"),0x24:("BIT","zp"),0x25:("AND","zp"),0x26:("ROL","zp"),0x28:("PLP","imp"),0x29:("AND","imm"),0x2A:("ROL","acc"),0x2C:("BIT","abs"),0x2D:("AND","abs"),0x2E:("ROL","abs"),
0x30:("BMI","rel"),0x31:("AND","izy"),0x35:("AND","zpx"),0x36:("ROL","zpx"),0x38:("SEC","imp"),0x39:("AND","absy"),0x3D:("AND","absx"),0x3E:("ROL","absx"),
0x40:("RTI","imp"),0x41:("EOR","izx"),0x45:("EOR","zp"),0x46:("LSR","zp"),0x48:("PHA","imp"),0x49:("EOR","imm"),0x4A:("LSR","acc"),0x4C:("JMP","abs"),0x4D:("EOR","abs"),0x4E:("LSR","abs"),
0x50:("BVC","rel"),0x51:("EOR","izy"),0x55:("EOR","zpx"),0x56:("LSR","zpx"),0x58:("CLI","imp"),0x59:("EOR","absy"),0x5D:("EOR","absx"),0x5E:("LSR","absx"),
0x60:("RTS","imp"),0x61:("ADC","izx"),0x65:("ADC","zp"),0x66:("ROR","zp"),0x68:("PLA","imp"),0x69:("ADC","imm"),0x6A:("ROR","acc"),0x6C:("JMP","ind"),0x6D:("ADC","abs"),0x6E:("ROR","abs"),
0x70:("BVS","rel"),0x71:("ADC","izy"),0x75:("ADC","zpx"),0x76:("ROR","zpx"),0x78:("SEI","imp"),0x79:("ADC","absy"),0x7D:("ADC","absx"),0x7E:("ROR","absx"),
0x81:("STA","izx"),0x84:("STY","zp"),0x85:("STA","zp"),0x86:("STX","zp"),0x88:("DEY","imp"),0x8A:("TXA","imp"),0x8C:("STY","abs"),0x8D:("STA","abs"),0x8E:("STX","abs"),
0x90:("BCC","rel"),0x91:("STA","izy"),0x94:("STY","zpx"),0x95:("STA","zpx"),0x96:("STX","zpy"),0x98:("TYA","imp"),0x99:("STA","absy"),0x9A:("TXS","imp"),0x9D:("STA","absx"),
0xA0:("LDY","imm"),0xA1:("LDA","izx"),0xA2:("LDX","imm"),0xA4:("LDY","zp"),0xA5:("LDA","zp"),0xA6:("LDX","zp"),0xA8:("TAY","imp"),0xA9:("LDA","imm"),0xAA:("TAX","imp"),0xAC:("LDY","abs"),0xAD:("LDA","abs"),0xAE:("LDX","abs"),
0xB0:("BCS","rel"),0xB1:("LDA","izy"),0xB4:("LDY","zpx"),0xB5:("LDA","zpx"),0xB6:("LDX","zpy"),0xB8:("CLV","imp"),0xB9:("LDA","absy"),0xBA:("TSX","imp"),0xBC:("LDY","absx"),0xBD:("LDA","absx"),0xBE:("LDX","absy"),
0xC0:("CPY","imm"),0xC1:("CMP","izx"),0xC4:("CPY","zp"),0xC5:("CMP","zp"),0xC6:("DEC","zp"),0xC8:("INY","imp"),0xC9:("CMP","imm"),0xCA:("DEX","imp"),0xCC:("CPY","abs"),0xCD:("CMP","abs"),0xCE:("DEC","abs"),
0xD0:("BNE","rel"),0xD1:("CMP","izy"),0xD5:("CMP","zpx"),0xD6:("DEC","zpx"),0xD8:("CLD","imp"),0xD9:("CMP","absy"),0xDD:("CMP","absx"),0xDE:("DEC","absx"),
0xE0:("CPX","imm"),0xE1:("SBC","izx"),0xE4:("CPX","zp"),0xE5:("SBC","zp"),0xE6:("INC","zp"),0xE8:("INX","imp"),0xE9:("SBC","imm"),0xEA:("NOP","imp"),0xEC:("CPX","abs"),0xED:("SBC","abs"),0xEE:("INC","abs"),
0xF0:("BEQ","rel"),0xF1:("SBC","izy"),0xF5:("SBC","zpx"),0xF6:("INC","zpx"),0xF8:("SED","imp"),0xF9:("SBC","absy"),0xFD:("SBC","absx"),0xFE:("INC","absx"),
}
SIZES = {"imp":1,"acc":1,"imm":2,"zp":2,"zpx":2,"zpy":2,"izx":2,"izy":2,"rel":2,"abs":3,"absx":3,"absy":3,"ind":3}

def disasm_line(prg, off, base=0x8000, cpu=None):
    """Disassemble instruction at PRG offset `off`. cpu = base address (default 0x8000 + off%0x4000)."""
    addr = cpu if cpu is not None else base + (off % 0x4000)
    op = prg[off]
    if op not in OPS:
        return addr, 1, f"???"
    mnem, mode = OPS[op]
    size = SIZES[mode]
    if off + size > len(prg):
        return addr, size, f"{mnem} ?"
    if mode == "imp":
        return addr, size, mnem
    if mode == "acc":
        return addr, size, mnem + " A"
    if mode == "imm":
        return addr, size, f"{mnem} #${prg[off+1]:02X}"
    if mode == "zp":
        return addr, size, f"{mnem} ${prg[off+1]:02X}"
    if mode == "zpx":
        return addr, size, f"{mnem} ${prg[off+1]:02X},X"
    if mode == "zpy":
        return addr, size, f"{mnem} ${prg[off+1]:02X},Y"
    if mode == "izx":
        return addr, size, f"{mnem} (${prg[off+1]:02X},X)"
    if mode == "izy":
        return addr, size, f"{mnem} (${prg[off+1]:02X}),Y"
    if mode == "rel":
        rel = prg[off+1]
        if rel >= 0x80: rel -= 0x100
        target = addr + 2 + rel
        return addr, size, f"{mnem} ${target:04X}"
    if mode == "abs":
        v = prg[off+1] | (prg[off+2] << 8)
        return addr, size, f"{mnem} ${v:04X}"
    if mode == "absx":
        v = prg[off+1] | (prg[off+2] << 8)
        return addr, size, f"{mnem} ${v:04X},X"
    if mode == "absy":
        v = prg[off+1] | (prg[off+2] << 8)
        return addr, size, f"{mnem} ${v:04X},Y"
    if mode == "ind":
        v = prg[off+1] | (prg[off+2] << 8)
        return addr, size, f"{mnem} (${v:04X})"
    return addr, size, "?"

def disasm(prg, start, length, base=0x8000):
    lines = []
    off = start
    end = min(start + length, len(prg))
    # MMC3: bank 7 (PRG 0x1C000-0x1FFFF) lives at CPU $C000-$DFFF and
    # $E000-$FFFF (fixed last 8KB bank at 0x1E000).
    if start >= 0x1C000:
        addr = 0xC000 + ((start - 0x1C000) % 0x2000)
        if (start - 0x1C000) >= 0x2000:
            addr = 0xE000 + (start - 0x1C000 - 0x2000)
    else:
        addr = base + (start % 0x4000)
    while off < end:
        a2, size, text = disasm_line(prg, off, base, addr)
        bytes_ = " ".join(f"{prg[off+i]:02X}" for i in range(size))
        lines.append(f"${addr:04X}: {bytes_:<12} {text}")
        off += size
        addr += size
    return lines

if __name__ == "__main__":
    ROM = r"G:\RetroBat\roms\nes\Nekketsu! Street Basket - Go for it, Dunk Heroes (v1.2 Final).nes"
    data = open(ROM, "rb").read()
    prg = data[16:16+8*16384]
    # args: bank start len [cpu_base]
    bank = int(sys.argv[1], 16)
    start = int(sys.argv[2], 16)
    length = int(sys.argv[3], 16)
    base = int(sys.argv[4], 16) if len(sys.argv) > 4 else 0x8000
    prg_off = bank*0x4000 + start
    lines = disasm(prg, prg_off, length, base)
    for l in lines:
        print(l)
