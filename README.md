# Making a Sigma Delta DAC on the CLB

This project has a drop in CLB module to add a 16bit DAC to the PIC16F13145. You can confiugre PPSOUT7 to any pin.

The design builds a 16-bit accumulator entirely from CLB LUTs, with each bit using two LUTs (sum and carry), fully utilizing all 32 available LUTs. The DAC output is derived from the carry bit of the accumulator, updated each clock cycle.

By default you can stream points over USB Serial. 

`SD_DAC_16_SIM.clb` is a simulatable CLB file for Microchip's CLB Synthizer, you can't actually build it as it uses 100% of the resources and the current backend can only hit 40-70% utilization. Use `build_dac.py` to build the bitstream (requires [this](https://github.com/ferret-guy/CLB-Bitstream-Tools) lib).

This project is *not affiliated with, endorsed by, or sponsored by Microchip Technology Inc.*
"Microchip" and "CLB" are trademarks of *Microchip Technology Inc.*
All product names, logos, and brands belong to their respective owners.
