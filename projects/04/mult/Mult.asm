// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

//Loading RAM[2] to be 0 
    @R2
    M = 0

//checking if RAM[0] = 0, if so goto END
    @R0 
    D = M

@END
    D;JEQ

(LOOP)
    @R0 // using Ram[0] as a counter for the ammount of times to sum Ram[1]
        M = M - 1

    @R1 // the product to be summed "RAM[0]" times
        D = M

    @R2 // the location in which to store the product
        M = M + D

    @R0 //Loads RAM[0] to D
        D = M

    @LOOP
        D;JGT 

(END)