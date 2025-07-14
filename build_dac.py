from itertools import cycle
from pathlib import Path

from bitstream import Bitstream
from build_lut import LUT4, a, b, c, d
from clb_graph import generate_dot_from_config
from data_model import (_CLB_ENUM, BLE_CFG, BLEXY, FLOPSEL, LUT_IN_A, LUT_IN_B,
                        LUT_IN_C, LUT_IN_D, PPS_OUT_NUM, CLKDIV)

BANKS = {"A": LUT_IN_A, "B": LUT_IN_B, "C": LUT_IN_C, "D": LUT_IN_D}
NAME2BANK = {n: k for k, v in BANKS.items() for n in v.__members__}
SYM = {"A": a, "B": b, "C": c, "D": d}

ble = lambda i: (LUT_IN_A, LUT_IN_B, LUT_IN_C, LUT_IN_D)[i // 8][f"CLB_BLE_{i}"]
swin = lambda i: (LUT_IN_A, LUT_IN_B, LUT_IN_C, LUT_IN_D)[i // 8][f"CLBSWIN{i}"]

bs = Bitstream()

# BLE indices grouped by bank
luts = {b: [i for i in range(32) if NAME2BANK[ble(i).name] == b] for b in "ABCD"}

carry_cycle = cycle("CD")
stages = {
    i: (
        luts["B" if i < 8 else "A"].pop(0),  # SUM LUT
        luts[next(carry_cycle)].pop(0),
    )  # CARRY LUT
    for i in range(16)
}

for bit, (sum_lut, car_lut) in stages.items():
    d_in = swin(bit)
    s_fb = ble(sum_lut)
    taps = [d_in, s_fb] if bit == 0 else [d_in, s_fb, ble(stages[bit - 1][1])]

    va, vb, *vc = [SYM[NAME2BANK[t.name]] for t in taps]  # symbols
    sum_expr = va ^ vb if bit == 0 else va ^ vb ^ vc[0]
    carry_expr = va & vb if bit == 0 else (va & vb) | (vb & vc[0]) | (va & vc[0])

    kws = {f"LUT_I_{NAME2BANK[t.name]}": t for t in taps}
    bs.LUTS[BLEXY(sum_lut)] = BLE_CFG(
        LUT_CONFIG=LUT4(sum_expr).bitstream(), FLOPSEL=FLOPSEL.ENABLE.value, **kws
    )
    bs.LUTS[BLEXY(car_lut)] = BLE_CFG(
        LUT_CONFIG=LUT4(carry_expr).bitstream(),
        FLOPSEL=FLOPSEL.ENABLE.value if bit == 15 else FLOPSEL.DISABLE.value,
        **kws,
    )

# Final sigma‑delta output
fin = stages[15][1]
grp = fin // 4
bs.PPS_OUT[PPS_OUT_NUM[grp]].OUT = _CLB_ENUM[grp](fin % 4)
print(repr(_CLB_ENUM[grp](fin % 4)))
print(generate_dot_from_config(bs))

bs.save_bitstream_s(Path(r"clbBitstream.s"))
