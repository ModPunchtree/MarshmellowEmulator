# Marshmellow Emulator
The simplest possible 16 bit Von Neumann CPU that is designed specifically to run Core URCL.

# Specs
* 8x4 character terminal
* 4k 16 bit words of RAM
* 12 bit program counter

## 8 Main Registers:
*   R0          - Constant 0
*   R1 to R5    - General purpose registers (16 bit)
*   SP          - Stack pointer (physically it is just a normal register like R1 to R5) (16 bit)
*   PC          - Program counter (12 bit)

```
Instructions  Unused      Op Code     Op1     Op2     Op3
         ADD    XXXX          000     CCC     AAA     BBB
         BGE    XXXX          001     CCC     AAA     BBB
         NOR    XXXX          010     CCC     AAA     BBB
         RSH    XXXX          011     CCC     AAA     000
         LOD    XXXX          100     CCC     AAA     000
         STR    XXXX          101     000     AAA     BBB
          IN    XXXX          110     CCC     000     000
         OUT    XXXX          111     000     AAA     000

Registers     Index
       R0       000
       R1       001
       R2       010
       R3       011
       R4       100
       R5       101
       SP       110
       PC       111
```
## Note
IMM instructions are not directly supported by the CPU - instead you must load a RAM location which contains the desired immediate value.