 /*
 * MAIN Generated Driver File
 * 
 * @file main.c
 * 
 * @defgroup main MAIN
 * 
 * @brief This is the generated driver implementation file for the MAIN driver.
 *
 * @version MAIN Driver Version 1.0.2
 *
 * @version Package Version: 3.1.2
*/

#include "mcc_generated_files/system/system.h"
#include <stdio.h>

bool high = true;

void EUSART1_ReceiveISR(void)
{
    if(high){
        CLBSWINM = RC1REG;
    } else {
        // Latches write
        CLBSWINL = RC1REG;
    }
    high ^= 1;

    if (RC1STAbits.OERR)
    {
        RC1STAbits.CREN = 0;
        RC1STAbits.CREN = 1;
    }
}
/*
    Main application
*/

int main(void)
{
    SYSTEM_Initialize();
    CLB1_Enable();
    CLB1_SWIN_Write16(0);
    
    
    // Enable the Global Interrupts 
    INTERRUPT_GlobalInterruptEnable();  
    INTERRUPT_PeripheralInterruptEnable(); 
    IO_OUT_SetDigitalOutput();
    IO_OUT_SetPushPull();
    IO_OUT_SetDigitalMode();
    
    
    while (1)
    {
    }   
}
