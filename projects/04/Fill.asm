
// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm
// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(INFILOOP) // inifinite loop that listens to keyboard input

//** 1. starting with saving the address of the top-left pixel as index number  **/
    @SCREEN
        D = A 

    @PIXELNUM //variable to store the pixel index
        M = D

//**2. deciding the value of the colour based on the keyboard input **/
    @KBD
        D = M //loading the keyboard input 
        @IS_BLACK
            D;JGT // if any key is pressed the input is different than 0, the colour will be BLACK

        @IS_WHITE
            D;JEQ // else, no key is pressed and the colour is WHITE

        (IS_BLACK) //if key is pressed
            @COLOUR  
                M = -1 // colour is set to BLACK

            @LOOPSCREEN 
               0;JMP //when finished changing the screen - repeat process

        (IS_WHITE) //if no key is pressed
            @COLOUR 
                 M = 0 //colour is set to WHITE

            @LOOPSCREEN
                0;JMP ////when finished changing the screen - repeat process

//** 3. painting the screen the desired colour **/
(LOOPSCREEN)
    
    //** 3.1 - painting the current pixel based on the desired colour **/
        @COLOUR
            D = M //loading the desired colour

        @PIXELNUM
            A = M //loading the pixel address
            
            M = D // changing the pixels colour 

    //** 3.2 - checking if reached end of screen while painting **/
        @PIXELNUM
            D = M + 1 //upping the pixel location to check if reached end of screen

        @KBD
             D = A - D //checking if the pixel index is the same as the keyboard index 

    //3.3 upping the index number to continue the loop **
       @PIXELNUM 
            M = M + 1 //incrementing the location

            A = M //loading the address of the next desired pixel to paint
        
    //** 3.4 continuing to paint the next pixel  **/
        @LOOPSCREEN
             D;JGT

    //** 3.5 if  reached the end of the screen, repeat process **/
    @INFILOOP
            0;JMP


//while(){
// if (input != 0) {
 //for (int i = 0; i < 512; i++){
//   for(int j = 0; j < 256; j++ )
  //    pixel[i][j] = 1;
// }
// }
//}
// 
