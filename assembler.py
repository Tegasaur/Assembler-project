
'''-------------------------------------------------------------------------------

    Description:
        This is to act as an emulation of the IAR Embedded work bench. It should support the following instructions
        mov:  Move value from source to destination 
        call: Call subroutine
        dec:  Decrement destination by 1
        inc:  Increment destination by 1
        jz:   Jump if not zero
        ret:  Return from subroutine
        and:  Move logical of source and destination to destination
        bis:  Bit set destination with source
        cmp:  Compare source and destination
        add:  Add source to destination
        bit:  Bit test destination with source
        bic:  Bit clear destination with source
        This assemblar should use the 16 bit memory format and have a max value of 65535. Important things to note
        about the assembler includes:
        
        1. If any error is noticed in the first pass, processing for that line is truncated. That is if there is an
        error early in the line it will ignore all errors later in the line
        
        2. Any label that doesnt start in the first column of the file is considered an instruction. So the error
        for that label will be considered an instruction error


        
    Target:              TI LaunchPad development board with MSP430G2553 device 
    Date:                Aug 7, 2019
    Written by:          Samuel Okei Oghenetega, ECE dept, Texas Tech University
    Emulating:           IAR Embedded Workbench IDE
    Scripting Language:  Python 3.7
------------------------------------------------------------------------------'''










import numpy as np

nsp="E"
f=open("TestSourceCode"+nsp+".s43","r+");
array =f.readlines()
errormsg=[]
errorcount=[]
adrscount=512;
linecount=0
currentadrs=0
instuctioncode=0
labeldict={"P2OUT":903,"P1REN":456};
instructions=[]
adrsflg=0
labels=[]
orglist={}
orglist2={}
sublabel=["","","","","","",""]
codegentable=[]
instructioncode=[]
declaratives=["EQU","ORG","DB","DS","DW","END","SP","PC"]
instructionset={"call":"0000", "dec":"0000", "inc":"0000", "jz":"0000", "jnz":"0000", "ret":"0000","mov":"0100", "and":"1111","bis":"1101", "cmp":"1001", "add":"0101","bit":"1011","bic":"1100"}
instructionset3={"mov":"0100", "and":"1111","bic":"1100","bis":"1101", "cmp":"1001", "add":"0101","bit":"1011"}
instructionset2={"call":"0000", "dec":"0000", "inc":"0000", "jz":"0000", "jnz":"0000","ret":"0000","bic":"1100"}


#LINE NUMBER GENERATOR--------------------------------------------------------------------------------------------
#This increments the line number that will appear on the far left of the list file
def lineNumber():
    global linecount
    linecount+=1
#-----------------------------------------------------------------------------------------------------------------









    
#ORIGIN DETECTOR--------------------------------------------------------------------------------------------------
#This detects the origin and updates the address based on it    
def originDetect(items):
    if (items[0]==" "):
        i=items.split()
        if(i[0]=="ORG"):
            global adrscount
            adrscount=int(i[1],16)
#-----------------------------------------------------------------------------------------------------------------









            
#LABEL DETECTOR---------------------------------------------------------------------------------------------------
#This detects the labels and saves them in ana array alongside thier addresses. It also checkes for duplicates            
def labelDetect(items):
    global errorcount
    if ((items[0]==" ")|(items[0]=="#")):
        global labeldict
        return " "
    elif((items[0]!=" ")|(items[0]!="#")):
        i=items.split()
        if(i[0] in labeldict):
            global errormsg
            errormsg.append(str(linecount)+": duplicate label: "+i[0])
            errorcount.append(linecount)
        if(":" in i[0]):
            i[0]=i[0].replace(":","")
        if(i[0][0].isalpha()):
            labeldict[i[0]]=adrscount
            labels.append(i[0])
        else:
            errormsg.append(str(linecount)+": Incorrect label: "+i[0])
            errorcount.append(linecount)
        return i[0]
#-----------------------------------------------------------------------------------------------------------------









    
#MAKE INSTRUCTIONS------------------------------------------------------------------------------------------------
#This helps to construct the instructions that appear on the list file   
def makeInstructions(items):
    if ((items[0]==" ")|(items[0]=="#")):
        i=items.split()
        s=" "
        s=s.join(i)
        return s
    elif((items[0]!=" ")|(items[0]!="#")):
        i=items.split()
        i.pop(0)
        s=" "
        s=s.join(i)
        return s
#-----------------------------------------------------------------------------------------------------------------









    
#GET CONSTANTS----------------------------------------------------------------------------------------------------
#This assigns the address values to the constant values for labels with constant definitions   
def getConstants(items):
    i=items.split();
    if("$" in i):
        pass
    else:
        if ("EQU" in i):
            global adrscount
            global currentadrs
            global adrsflg
            currentadrs=adrscount
            adrsflg=1
            n=i.index("EQU")
            m=n+1
            num=i[m]
            if("%" in num):
                num=num.replace("%","")
                adrscount=int(num,2)
            elif("x" in num):
                num=int(num,16)
                adrscount=num
            else:
                adrscount=int(num)
#---------------------------------------------------------------------------------------------------------------









                
#RESTORE ADDRESS--------------------------------------------------------------------------------------------------
def restadrs():
    global adrsflg
    global adrscount
    global currentadrs
    if (adrsflg==1):
        adrscount=currentadrs
        adrsflg=0
        currentadrs=0
    else:
        pass
#-----------------------------------------------------------------------------------------------------------------









    
#GET VARIABLES----------------------------------------------------------------------------------------------------
#This assigns a new address space for each variable and changes address value accordingly
def getVariables(items):
    i=items.split();
    global adrscount
    if("DB" in i):
        adrscount+=1
    elif("DW" in i):
        adrscount+=2
    elif("DS" in i):
        n=i.index("DS")
        n=n+1
        n=int(i[n])
        adrscount+=n
#---------------------------------------------------------------------------------------------------------------









        
#CALCULATE ADDRESS----------------------------------------------------------------------------------------------
#This helps to get the accurate address of each line of code
def calculateaddress(items):
    global linecount;
    if (items.split()!=[]):
        size=0
        j=items.split()
        new=[]
        global labeldict
        try:
            if j[0].replace(":","") in labeldict:
                j.pop(0)
        except:
            pass
        
        for i in j:
            if ";" in i:
                break
            else:
                new.append(i)      
        try:
            if(new[0][0]==";"):
                new=[]
        except:
            pass
        try:
            if ".b" in new[0]:
                x=new[0].replace(".b","")
            elif ".w" in new[0]:
                x=new[0].replace(".w","")
            else:
                x=new[0]
        except:
            pass
        try:
            if x in instructionset:
                size=2
                if(len(new)==2):
                    if(new[1][0]!="R"):
                        size+=2
                elif(len(new)==3):
                    if(new[1][0]!="R"):
                        size+=2
                    if(new[2][0]!="R"):
                        size+=2
                if(x=="call"):
                    size=4
                if(x=="jnz"):
                    size=2
                if(x=="jz"):
                    size=2
            else:
                pass   
        except:
            pass
        global adrscount
        global instructioncode
        instructioncode.append([linecount]+[hex(adrscount)]+new)
        adrscount+=size
    else:
        pass
#---------------------------------------------------------------------------------------------------------------









    
#DOUBLE OPERAND INSTRUCTION-------------------------------------------------------------------------------------






#OPCODE HANDLER-------------------------------------------------------------------------------------------------
#This gets encoding for opcode of double operand instructions
def getopcode(items):
    global labeldict
    global sublabel
    global errormsg
    global errorcount
    opcode=""
    opcodemsg=""
    new=items[2:]
    try:
        if ".b" in new[0]:
            new[0]=new[0].replace(".b","")
        elif ".w" in new[0]:
            new[0]=new[0].replace(".w","")
        if new[0] in instructionset3:
            if(len(new)==3):
                opcode=instructionset3[new[0]]
                opcodemsg=new[0]
            else:
                pass
        else:
            pass

    except:
        pass
    
    sublabel[3]=opcodemsg
    return opcode
#-----------------------------------------------------------------------------------------------------------------





#BYTE/WORD HANDLER------------------------------------------------------------------------------------------------
#This gets byte/word encoding of double operand instructions
def getbw(items):
    global labeldict
    global sublabel
    bw=""
    bwmsg=""
    new=items[2:]
    try:
        if ".b" in new[0]:
            bw="1"
            bwmsg="byte operation"
        else:
            bw="0"
            bwmsg="word operation"
    except:
        pass
    sublabel[4]=bwmsg
    return bw
#-----------------------------------------------------------------------------------------------------------------





#ADDRESSING MODE FOR SOURCE HANDLER-------------------------------------------------------------------------------
#This gets addressing mode for the source of double operand instructions        
def getas(items):
    global labeldict
    global sublabel
    aS=""
    aSmsg=""
    new=items[2:]
    try:
        if (new[1][0]=='#'):
            aS="11"
            aSmsg="Immediate mode"
        elif (new[1][0]=='R'):
            aS="00"
            aSmsg="Register mode"
        else:
            aS="01"
            aSmsg="Indexed/Absolute or Addressing mode"
    except:
        pass
    sublabel[5]=aSmsg
    return aS
#-----------------------------------------------------------------------------------------------------------------





#ADDRESSING MODE FOR DESTINATION HANDLER--------------------------------------------------------------------------
#This gets addressing mode for the destination of double operand instructions        
def getad(items):
    global sublabel
    global labeldict
    ad=""
    admsg=""
    new=items[2:]
    try:
        if (new[2][0]=="R"):
            ad="0"
            admsg="Register mode"
        else:
            ad="1"
            admsg="Indexed/Absolute or Addressing mode"
    except:
        pass
    sublabel[6]=admsg
    return ad
#-----------------------------------------------------------------------------------------------------------------





#SOURCE REGISTER HANDLER------------------------------------------------------------------------------------------
#This gets source register encoding of double operand instructions
def getsreg(items):
    sreg=""
    new=items[2:]
    try:
        if(new[1][0]=="R"):
            sreg=bin(int(new[1].replace("R","").replace(",","")))[2:][(len(bin(int(new[1].replace("R","").replace(",",""))))-6):]
        elif(new[1][0]=="#"):
            sreg="0000"
        elif "(" in new[1]:
            index=new[1].index("(")
            b=new[1][(index+2):].replace(")","").replace(",","")
            sreg=bin(int(b))[2:][(len(bin(int(b)))-6):]
        else:
            sreg="0000"
    except:
        pass
    return sreg
#-----------------------------------------------------------------------------------------------------------------





#DESTINATION REGISTER HANDLER-------------------------------------------------------------------------------------
#This gets destination register encoding of double operand instructions
def getdreg(items):
    dreg=""
    new=items[2:]
    try:
        if(new[2][0]=="R"):
            dreg=bin(int(new[2].replace("R","").replace(",","")))[2:][(len(bin(int(new[2].replace("R","").replace(",",""))))-6):]
        elif "(" in new[2]:
            index=new[2].index("(")
            b=new[2][(index+2):].replace(")","").replace(",","")
            dreg=bin(int(b))[2:][(len(bin(int(b)))-6):]
        else:
            dreg="0000"
    except:
        pass
    return dreg
#-----------------------------------------------------------------------------------------------------------------





#EXTRA HANDLER----------------------------------------------------------------------------------------------------
#This gets all other needed encodings for the double operand instructions
def getextra(items):
    extra=""
    extra2=""
    new=items[2:]
    try:
        if(new[1][0]=="R"):
            extra=""
        elif(new[1][0]=="#"):
            b=new[1].replace("#","").replace(",","")
            if "+" in b:
                c=0
                b=b.split("+")
                for items in b:
                    if items in labeldict:
                        c=c+(labeldict[items])
                extra=extra+hex(c)[2:]
                
            elif b in labeldict:
                extra=extra+hex(labeldict[b])[2:]
            else:
                extra=extra+hex(int(b,16))[2:]
            if(len(extra)<4):
                extra=("0"*(4-len(extra)))+extra
                
           
        elif(new[1][0]=="&"):
            b=new[1].replace("&","").replace(",","")
            if "+" in b:
                c=0
                b=b.split("+")
                for items in b:
                    if items in labeldict:
                        c=c+(labeldict[items])
                extra=extra+hex(c)[2:]
            elif b in labeldict:
                extra=extra+hex(labeldict[b])[2:]
            else:
                extra=extra+hex(int(b,16))[2:]
            if(len(extra)<4):
                extra=("0"*(4-len(extra)))+extra
        elif "(" in new[1]:
            index=new[1].index("(")
            b=new[1][:index]
            extra=hex(int(b))[2:]
            if(len(extra)<4):
                extra=("0"*(4-len(extra)))+extra
            
        else:
            b=new[1].replace(",","")
            b=int(b,16)
            if(b>=int(items[1],16)+2):
                extra=extra+hex(b-(int(items[1],16)+1))[2:]
            else:
                b=b+65535
                extra=extra+hex(b-(int(items[1],16)+1))[2:]
            if(len(extra)<4):
                extra=("0"*(4-len(extra)))+extra
    except:
        pass
    p=extra[:2]
    o=extra[2:]
    extra=o+p
    try:
        if(new[2][0]=="R"):
            extra2=""
        elif(new[2][0]=="&"):
            b=new[2].replace("&","")
            if "+" in b:
                c=0
                b=b.split("+")
                for items in b:
                    if items in labeldict:
                        c=c+(labeldict[items])
                extra2=extra2+hex(c)[2:]
            elif b in labeldict:
                extra2=extra2+hex(labeldict[b])[2:]
            else:
                extra2=extra2+hex(int(b,16))[2:]
            if(len(extra2)<4):
                extra2=("0"*(4-len(extra2)))+extra2
        elif "(" in new[2]:
            index=new[2].index("(")
            b=new[2][:index]
            extra2=hex(int(b))[2:]
            if(len(extra2)<4):
                extra2=("0"*(4-len(extra2)))+extra2
        else:
            b=new[2]
            b=int(b,16)
            if(b>=int(items[1],16)+3):
                extra2=extra2+hex(b-(int(items[1],16)+3))[2:]
            else:
                b=b+65535
                extra2=extra2+hex(b-(int(items[1],16)+3))[2:]
            if(len(extra2)<4):
                extra2=("0"*(4-len(extra2)))+extra2
    except:
        pass
    p=extra2[:2]
    o=extra2[2:]
    extra2=o+p
    extra=extra+extra2
    return extra
#-----------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------










#SINGLE OPERAND INSTRUCTION---------------------------------------------------------------------------------------





#DECREMENT HANDLER------------------------------------------------------------------------------------------------
def handledec(items):
        opcode=""
        sreg=""
        ad=""
        aS=""
        dreg=""
        bw=""
        extra=""
        opcodemsg=""
        bwmsg=""
        admsg=""
        aSmsg=""
        stuff=""
        new=items[2:]
        try:
            if(new[0].replace(".b","").replace(".w","") =="dec"):
                if ".b" in new[0]:
                    bw="1"
                    bwmsg="byte operation"
                    x=new[0].replace(".b","")
                elif ".w" in new[0]:
                    bw="0"
                    bwmsg="word operation"
                    x=new[0].replace(".w","")
                else:
                    x=new[0]
                    bw="0"
                    bwmsg="word operation"
                if(x=="dec"):
                    opcode="1000"
                    opcodemsg="sub"
                    sreg="0011"
                    aS="01"
                    aSmsg="Absolute, Indexed or Symbolic mode"
                    if(new[1][0]=="R"):
                        dreg=bin(int(new[1].replace("R","").replace(",","")))[2:][(len(bin(int(new[1].replace("R","").replace(",",""))))-6):]
                    elif "(" in new[1]:
                        index=new[1].index("(")
                        b=new[1][(index+2):].replace(")","").replace(",","")
                        dreg=bin(int(b))[2:][(len(bin(int(b)))-6):]
                    else:
                        dreg="0000"
                if (new[1][0]=="R"):
                    ad="0"
                    admsg="Register"
                else:
                    ad="1"
                    admsg="Absolute, Indexed or Symbolic mode"
                if (new[1][0]=="&"):
                    b=new[1].replace("&","")
                    if "+" in b:
                        c=0
                        b=b.split("+")
                        for items in b:
                            if items in labeldict:
                                c=c+(labeldict[items])
                        extra=extra+hex(c)[2:]
                    elif b in labeldict:
                        extra=extra+hex(labeldict[b])[2:]
                    else:
                        extra=extra+hex(int(b,16))[2:]
                    if(len(extra)<4):
                        extra=("0"*(4-len(extra)))+extra
                
        except:
            pass
        p=extra[:2]
        o=extra[2:]
        extra=o+p
        if (sublabel[3]==""):
            sublabel[3]=opcodemsg
            sublabel[4]=bwmsg
            sublabel[5]=aSmsg
            sublabel[6]=admsg
        stuff=ad+bw+aS
        instr=stuff+dreg+opcode+sreg
        if(instr!=""):
            instr=hex(int(instr,2))[2:]
            instr=instr+extra
        return instr
#-----------------------------------------------------------------------------------------------------------------




    
#BIT CLEAR HANDLER------------------------------------------------------------------------------------------------
def handlebic(items):
        opcode=""
        sreg=""
        ad=""
        aS=""
        dreg=""
        bw=""
        extra=""
        opcodemsg=""
        bwmsg=""
        admsg=""
        aSmsg=""
        stuff=""
        new=items[2:]
        try:
            if(new[0].replace(".b","").replace(".w","") =="bic"):
                if ".b" in new[0]:
                    bw="1"
                    bwmsg="byte operation"
                    x=new[0].replace(".b","")
                elif ".w" in new[0]:
                    bw="0"
                    bwmsg="word operation"
                    x=new[0].replace(".w","")
                else:
                    x=new[0]
                    bw="0"
                    bwmsg="word operation"
                if(x=="bic"):
                    opcode="0100"
                    opcodemsg="mov"
                    sreg="0011"
                    aS="01"
                    aSmsg="Absolute, Indexed or Symbolic mode"
                    if(new[1][0]=="R"):
                        dreg=bin(int(new[1].replace("R","").replace(",","")))[2:][(len(bin(int(new[1].replace("R","").replace(",",""))))-6):]
                    elif "(" in new[1]:
                        index=new[1].index("(")
                        b=new[1][(index+2):].replace(")","").replace(",","")
                        dreg=bin(int(b))[2:][(len(bin(int(b)))-6):]
                    else:
                        dreg="0000"
                if (new[1][0]=="R"):
                    ad="0"
                    admsg="Register"
                else:
                    ad="1"
                    admsg="Absolute, Indexed or Symbolic mode"
                if (new[1][0]=="&"):
                    b=new[1].replace("&","")
                    if "+" in b:
                        c=0
                        b=b.split("+")
                        for items in b:
                            if items in labeldict:
                                c=c+(labeldict[items])
                        extra=extra+hex(c)[2:]
                    elif b in labeldict:
                        extra=extra+hex(labeldict[b])[2:]
                    else:
                        extra=extra+hex(int(b,16))[2:]
                    if(len(extra)<4):
                        extra=("0"*(4-len(extra)))+extra
                
        except:
            pass
        p=extra[:2]
        o=extra[2:]
        extra=o+p
        if (sublabel[3]==""):
            sublabel[3]=opcodemsg
            sublabel[4]=bwmsg
            sublabel[5]=aSmsg
            sublabel[6]=admsg
        stuff=ad+bw+aS
        instr=stuff+dreg+opcode+sreg
        if(instr!=""):
            instr=hex(int(instr,2))[2:]
            instr=instr+extra
        return instr
#----------------------------------------------------------------------------------------------------------------




    
#INCREMENT HANDLER-----------------------------------------------------------------------------------------------       
def handleinc(items):
        global labeldict
        global sublabel
        opcode=""
        sreg=""
        ad=""
        aS=""
        dreg=""
        bw=""
        stuff=""
        extra=""
        opcodemsg=""
        bwmsg=""
        admsg=""
        aSmsg=""
        new=items[2:]
        try:
            if(new[0].replace(".b","").replace(".w","") =="inc"):
                if ".b" in new[0]:
                    bw="1"
                    bwmsg="byte operation"
                    x=new[0].replace(".b","")
                elif ".w" in new[0]:
                    bw="0"
                    bwmsg="word operation"
                    x=new[0].replace(".w","")
                else:
                    x=new[0]
                    bw="0"
                    bwmsg="word operation"
                if(x=="inc"):
                    opcode="0100"
                    opcodemsg="mov"
                    sreg="0011"
                    aS="01"
                    aSmsg="Absolute, Indexed or Symbolic mode"
                    if(new[1][0]=="R"):
                        dreg=bin(int(new[1].replace("R","").replace(",","")))[2:][(len(bin(int(new[1].replace("R","").replace(",",""))))-6):]
                    elif "(" in new[1]:
                        index=new[1].index("(")
                        b=new[1][(index+2):].replace(")","").replace(",","")
                        dreg=bin(int(b))[2:][(len(bin(int(b)))-6):]
                    else:
                        dreg="0000"
                if (new[1][0]=="R"):
                    ad="0"
                    admsg="Register"
                else:
                    ad="1"
                    admsg="Absolute, Indexed or Symbolic mode"
                if (new[1][0]=="&"):
                    b=new[1].replace("&","")
                    if "+" in b:
                        c=0
                        b=b.split("+")
                        for items in b:
                            if items in labeldict:
                                c=c+(labeldict[items])
                        extra=extra+hex(c)[2:]
                    if b in labeldict:
                        extra=extra+hex(labeldict[b])[2:]
                    else:
                        extra=extra+hex(int(b,16))[2:]
                    if(len(extra)<4):
                        extra=("0"*(4-len(extra)))+extra          
        except:
            pass
        p=extra[:2]
        o=extra[2:]
        extra=o+p
        if (sublabel[3]==""):
            sublabel[3]=opcodemsg
            sublabel[4]=bwmsg
            sublabel[5]=aSmsg
            sublabel[6]=admsg
        stuff=ad+bw+aS
        instr=stuff+dreg+opcode+sreg
        if(instr!=""):
            instr=hex(int(instr,2))[2:]
            instr=instr+extra
        return instr
#-----------------------------------------------------------------------------------------------------------------




    
#JUMP NOT ZERO HANDLER--------------------------------------------------------------------------------------------
def handlejnz(items):
        global errormsg
        global errorcount
        global labeldict
        global sublabel
        opcode=""
        offset=""
        opcodemsg=""
        bwmsg=""
        aSmsg=""
        admsg=""
        extra=""
        instr=""
        new=items[2:]
        try:
            if new[0].replace(".b","").replace(".w","").replace(",","") in instructionset: 
                if(new[0]=="jnz"):
                    opcode="001000"
                    opcodemsg="jnz"
                    if new[1] in labeldict:
                        b=labeldict[new[1]]-int(items[1],16)
                        offset=str(np.binary_repr(b,width=10))
                    else:
                        pass
                else:
                    pass
            else:
                if new[0].replace(".b","").replace(".w","").replace(",","") in declaratives:
                    pass
                else:
                    pass
                
        except:
            pass
        instr=offset[2:]+opcode+offset[:2]
        if (sublabel[3]==""):
            sublabel[3]=opcodemsg
            sublabel[4]=bwmsg
            sublabel[5]=aSmsg
            sublabel[6]=admsg
        if(instr!=""):
            instr=hex(int(instr,2))[2:]
            instr=instr+extra
        if((len(instr)<4)&(instr!="")):
            instr=("0"*(4-len(instr)))+instr
        return instr
#-------------------------------------------------------------------------------------------------------------------




    
#JUMP IF ZERO HANDLER-----------------------------------------------------------------------------------------------
def handlejz(items):
        global errormsg
        global labeldict
        global sublabel
        global errorcount
        opcode=""
        offset=""
        opcodemsg=""
        bwmsg=""
        aSmsg=""
        admsg=""
        extra=""
        instr=""
        new=items[2:]
        try:
            if new[0].replace(".b","").replace(".w","").replace(",","") in instructionset: 
                if(new[0]=="jz"):
                    opcode="001001"
                    opcodemsg="jz"
                    if new[1] in labeldict:
                        b=labeldict[new[1]]-int(items[1],16)
                        offset=str(np.binary_repr(b,width=10))
                    else:
                        pass
                else:
                    pass
            else:
                if new[0].replace(".b","").replace(".w","").replace(",","") in declaratives:
                    pass
                else:
                    pass

                
        except:
            pass
        instr=offset[2:]+opcode+offset[:2]
        if (sublabel[3]==""):
            sublabel[3]=opcodemsg
            sublabel[4]=bwmsg
            sublabel[5]=aSmsg
            sublabel[6]=admsg   
        if(instr!=""):
            instr=hex(int(instr,2))[2:]
            instr=instr+extra
        if((len(instr)<4)&(instr!="")):
            instr=("0"*(4-len(instr)))+instr
        return instr

#CALL HANDLER-----------------------------------------------------------------------------------------------    
def handlecall(items):
        global errormsg
        global labeldict
        global sublabel
        global errorcount
        opcode=""
        opcodemsg=""
        bwmsg=""
        aSmsg=""
        admsg=""
        extra=""
        instr=""
        new=items[2:]
        try:
            if new[0].replace(".b","").replace(".w","").replace(",","") in instructionset: 
                if(new[0]=="call"):
                    opcode="0001001010110000"
                    opcodemsg="call"
                    if new[1] in labeldict:
                        b=hex(labeldict[new[1]])[2:]
                        extra=b[2:]+b[:2]
                    else:
                        pass
                else:
                    pass
            else:
                if new[0].replace(".b","").replace(".w","").replace(",","") in declaratives:
                    pass
                else:
                    pass

                
        except:
            pass
        instr=opcode[8:]+opcode[:8]
        if (sublabel[3]==""):
            sublabel[3]=opcodemsg
            sublabel[4]=bwmsg
            sublabel[5]=aSmsg
            sublabel[6]=admsg
        if(instr!=""):
            instr=hex(int(instr,2))[2:]
            instr=instr+extra
        if((len(instr)<4)&(instr!="")):
            instr=("0"*(4-len(instr)))+instr
        return instr
#-----------------------------------------------------------------------------------------------------------------




    
#RETURN HANDLER---------------------------------------------------------------------------------------------------
def handleret(items):
        opcode=""
        sreg=""
        ad=""
        aS=""
        dreg=""
        bw=""
        stuff=""
        opcodemsg=""
        bwmsg=""
        admsg=""
        aSmsg=""
        new=items[2:]
        try:
            if(new[0].replace(".b","").replace(".w","") =="ret"):
                if ".b" in new[0]:
                    bw="1"
                    bwmsg="byte operation"
                    x=new[0].replace(".b","")
                elif ".w" in new[0]:
                    bw="0"
                    bwmsg="word operation"
                    x=new[0].replace(".w","")
                else:
                    x=new[0]
                    bw="0"
                    bwmsg="word operation"
                if(x=="ret"):
                    opcode="0100"
                    opcodemsg="move"
                    sreg="0001"
                    aS="00"
                    aSmsg="Register"
                    dreg="0000"
                    ad="0"
                    admsg="Register"
        except:
            pass
        if (sublabel[3]==""):
            sublabel[3]=opcodemsg
            sublabel[4]=bwmsg
            sublabel[5]=aSmsg
            sublabel[6]=admsg
        stuff=ad+bw+aS
        instr=stuff+dreg+opcode+sreg
        if(instr!=""):
            instr=hex(int(instr,2))[2:]
        if((len(instr)<4)&(instr!="")):
            instr=("0"*(4-len(instr)))+instr
        return instr
#-----------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------









    
#ERROR HANDLER----------------------------------------------------------------------------------------------------
#This handles all instruction based errors
def errorhandler(items):
    global instructionset
    global errormsg
    global declaratives
    global labeldict
    instr=""
    new=items[2:]
    if(new!=[]):
        if new[0].replace(".b","").replace(".w","") in instructionset:
            if(len(new)>=2):
                if(new[1]!=""):
                    if (new[1][0]=="R"):
                        try:
                            if (int(new[1].replace("R",""))>15):
                                errormsg.append(str(items[0])+": Long Operand Error")
                                errorcount.append(linecount)
                        except:
                            errormsg.append(str(items[0])+": Incorrect Operand Error")
                            errorcount.append(linecount)


                    elif (new[1][0]=="#"):
                        try:
                            if "+" in new[1]:
                                c=0
                                b=b.split("+")
                                for items in b:
                                    if items in labeldict:
                                        c=(labeldict[items])
                                extra=hex(c)[2:]
                            elif new[1].replace("#","").replace(",","") not in labeldict:
                                if (int(new[1].replace("#","").replace(",",""),16)>65535):
                                    errormsg.append(str(items[0])+": Incorrect Operand Error")
                                    errorcount.append(linecount)
                                
                        except:
                           errormsg.append(str(items[0])+": Incorrect Operand Error")
                           errorcount.append(linecount)
                    elif (new[1][0]=="&"):
                        try:
                            if "+" in new[1]:
                                b=new[1]
                                c=0
                                b=b.split("+")
                                for items in b:
                                    if items in labeldict:
                                        c=(labeldict[items])
                                extra=hex(c)[2:]
                            elif new[1].replace("&","").replace(",","") not in labeldict:
                                if (int(new[1].replace("&","").replace(",",""),16)>65535):
                                    errormsg.append(str(items[0])+": Incorrect Operand Error")
                                    errorcount.append(linecount)
                        except:
                           errormsg.append(str(items[0])+": Incorrect Operand Error")
                           errorcount.append(linecount)
                    elif "(" in new[1]:
                        try:
                            index=new[1].index("(")
                            b=new[1][(index+1):].replace(")","").replace("R","").replace(",","")
                            if(int(b)>15):
                                errormsg.append(str(items[0])+": Long Operand Error")
                                errorcount.append(linecount)
                        except:
                            errormsg.append(str(items[0])+": Incorrect Operand Error")
                            errorcount.append(linecount)

                            
                    else:
                        b=new[1]
                        try:
                            if b not in labeldict:
                                if b not in declaratives:
                                    if (int(b,16)>65535):
                                        errormsg.append(str(items[0])+": Long Operand Error")
                                        errorcount.append(linecount)
                        except:
                                errormsg.append(str(items[0])+": Incorrect Operand Error")
                                errorcount.append(linecount)
           

            if(len(new)>=3):
                if(len(new[2])>0):
                    if (new[2][0]=="R"):
                        try:
                            if (int(new[2].replace("R",""))>15):
                                print(int(new[1].replace("R","")))
                                errormsg.append(str(items[0])+": Long Operand Error")
                                errorcount.append(linecount)
                        except:
                            errormsg.append(str(items[0])+": Incorrect Operand Error")
                            errorcount.append(linecount)

                    elif (new[2][0]=="&"):
                        try:
                            if "+" in new[2]:
                                b=new[2]
                                c=0
                                b=b.split("+")
                                for items in b:
                                    if items in labeldict:
                                        c=(labeldict[items])
                                extra=hex(c)[2:]
                            elif new[2].replace("&","").replace(",","") not in labeldict:
                                if (int(new[2].replace("&","").replace(",",""),16)>65535):
                                    errormsg.append(str(items[0])+": Incorrect Operand Error")
                                    errorcount.append(linecount)
                        except:
                           errormsg.append(str(items[0])+": Incorrect Operand Error")
                           errorcount.append(linecount)
                    elif "(" in new[2]:
                        try:
                            index=new[2].index("(")
                            b=new[2][(index+1):].replace(")","").replace("R","")
                            
                            if(int(b)>15):
                                errormsg.append(str(items[0])+": Long Operand Error")
                                errorcount.append(linecount)
                        except:
                            errormsg.append(str(items[0])+": Incorrect Operand Error")
                            errorcount.append(linecount)
                    else:
                        b=new[2]
                        try:
                            if b not in labeldict:
                                if b not in declaratives:
                                    if (int(b,16)>65535):
                                        errormsg.append(str(items[0])+": Long Operand Error")
                                        errorcount.append(linecount)
                        except:
                                errormsg.append(str(items[0])+": Incorrect Operand Error")
                                errorcount.append(linecount)

        elif new[0] in declaratives:
            if(len(new)>=2):
                if(new[0]=="DB"):
                    instr="0"
                elif(new[0]=="DW"):
                    instr="00"
                elif(new[0]=="DS"):
                    instr="0"*int(new[1])
                

        else:
            errormsg.append(str(items[0])+": Instruction Error")
            errorcount.append(linecount)
        return instr
#---------------------------------------------------------------------------------------------------------------









            
#GET BUFFER TABLE SIZE------------------------------------------------------------------------------------------
#This helps to get the size for a buffer table that has been initialized in the previous line
def getBufferTableSize(items):
    i=items.split()
    global labeldict
    global adrscount
    global adrsflg
    global currentadrs
    if("$" in i):
        currentadrs=adrscount
        adrsflg=1
        n=i.index("$")
        n=n+2
        m=i[n]
        o=labeldict[m]
        adrscount=adrscount-o
#---------------------------------------------------------------------------------------------------------------









        
#GET ADDRESS COUNT----------------------------------------------------------------------------------------------
#This limits the address count ar FFFF
def editAddressCount():
    global adrscount
    if (adrscount>=65535):
            adrscount=0
#---------------------------------------------------------------------------------------------------------------









            
#FIRST PASS-----------------------------------------------------------------------------------------------------
for items in array:
    c=0
    if(items[0]==";"):
        c=0;
        editAddressCount()
        adrss=hex(adrscount)[2:]
        if(len(adrss)<4):
            adrss=("0"*(4-len(adrss)))+adrss
        a=[str(linecount)+" "*(5-len(str(linecount))),adrss+" "*(8-len(adrss))," "*(20),items]
        instructions.append(a)
    elif(items.split()==[]):
        c=1
    elif((items[0]!=";")&(items.split()!=[])):
        c=0
        originDetect(items)
        inst=makeInstructions(items)
        getConstants(items)
        getBufferTableSize(items)
        lab=labelDetect(items)
        editAddressCount()
        adrss=hex(adrscount)[2:]
        if(len(adrss)<4):
            adrss=("0"*(4-len(adrss)))+adrss
        b=[str(linecount)+" "*(5-len(str(linecount))),adrss+" "*(8-len(adrss)),lab+" "*(20-len(lab)),inst]
        restadrs()
        getVariables(items)
        instructions.append(b)
    calculateaddress(items)
    if(c==0):
        lineNumber()
    else:
        pass
#---------------------------------------------------------------------------------------------------------------









    
#SECOND PASS----------------------------------------------------------------------------------------------------
objectfile=""
objectfile+="SamuelOghenetegaOkei00"
instrhold=["","","",""]
instrh=""
l=0
k=0
start=0
adrr=""
size=""
for items in instructioncode:
        sublabel=[items[0], items[1],"","","","",""]
        instr="         "
        instr2="         "
        inst=errorhandler(items)
        if(len(items)==5):
            try:
                a=getopcode(items)
                b=getbw(items)
                c=getas(items)
                d=getad(items)
                e=getsreg(items)
                g=getdreg(items)
                h=getextra(items)
                opcode=hex(int(a,2))[2:]
                sreg=hex(int(e,2))[2:]
                stuff=hex(int(d+b+c,2))[2:]
                dreg=hex(int(g,2))[2:]
                extra=h
                instr=stuff+dreg+opcode+sreg+extra+" "*(20-len(stuff+dreg+opcode+sreg+extra))
            except:
                pass
        elif((len(items)==4)|(len(items)==3)):
            ret=handleret(items)
            dec=handledec(items)
            inc=handleinc(items)
            jnz=handlejnz(items)
            jzz=handlejz(items)
            call=handlecall(items)
            bic=handlebic(items)
            instr=ret+dec+inc+call+jnz+jzz+bic+inst
            instr=instr+" "*(20-len(instr))
        else:
            opcode=""
            sreg=""
            stuff=""
            dreg=""
            extra=""
            instr=" "*20
        if items[0] in errorcount:
            instr2=" "*20
        else:
            instr2=instr
        if (len(instructions[items[0]])==4):
            if(instr2.replace(" ","")!=""):
                if(int(instr2,16)!=0):
                    instructions[items[0]].insert(2,instr2)
                else:
                    instructions[items[0]].insert(2," "*20)
            else:
                instructions[items[0]].insert(2," "*20)
            
        if sublabel in codegentable:
            pass
        else:
            if(sublabel[3]!=""):
                codegentable.append(sublabel)
        sublabel=[]
        if(len(items)>=3):
            if(items[2]=="ORG"):
                start=1
            if (start==1):
                 instrh+=instr2.replace(" ","")
                 if(items[2]=="ORG" or items[2]=="END"):
                     instrhold[l]=instrh
                     instrh=""
                     l+=1
for items in instructioncode:
            if(len(items)>=3):
                if(items[2]=="ORG"):
                    objectfile+="FF00AA55"
                    adrr=items[1][2:]
                    if(len(adrr)<4):
                        adrr=((4-len(adrr))*"0")+adrr
                    objectfile+=adrr
                    k+=1
                    if (k<len(instrhold)):
                        size=str(round(len(instrhold[k])/2))
                    if(len(size)<4):
                        size=((4-len(size))*"0")+size
                    objectfile+=size
                    if (k<len(instrhold)):
                        objectfile+=instrhold[k]
                else:
                    pass                 
errormsg=list(set(errormsg))
objectfile+="FFAA5500"
#---------------------------------------------------------------------------------------------------------------










#List File Generator--------------------------------------------------------------------------------------------
for i in range(0,len(instructions)):
    s="       "
    instructions[i]=s.join(instructions[i])
f.close()
open("listf"+nsp+".lst", 'w').close()
f=open("listf"+nsp+".lst","r+")


f.write("Title: SAMS ASSEMBLER\n")
f.write("\n")
f.write("Name: Samuel Okei \n")
f.write("\n")
f.write("Instructor: Dr Micheal Helm \n")
f.write("\n")
f.write("R-Number: 11550144 \n")
f.write("\n")
for i in range(0,len(instructions)):
    f.write(instructions[i])
    f.write("\n")
f.write("SYMBOL TABLE")
f.write("\n")
f.write("\n")
f.write("%s    :    %s" % ("LABEL"+" "*(25-len("LABEL")), "VALUE"+" "*(25-len("VALUE"))))
f.write("\n")
f.write("\n")
for key in sorted(labeldict.keys()):
    f.write("%s    :    %s" % (key+" "*(25-len(key)), hex(labeldict[key])+" "*(25-len(key))))
    f.write("\n")
f.write("\n")

f.write("CODE GEN TABLE")
f.write("\n")
f.write("\n")
f.write("     %s    :    %s     :     %s     :     %s      :     %s     :       %s     " % (str("N/O")+" "*(5-len("N/O")), "ADDRESS"+" "*(12-len("ADDRESS")),"OPCODE"+" "*(12-len("OPCODE")),"BYTE/WORD"+" "*(25-len("BYTE/WORD")),"SOURCE ADRS MODE"+" "*(40-len("SOURCE ADRS MODE")),"DEST ADRS MODE"+" "*(10-len("DEST ADRS MODE"))))
f.write("\n")
f.write("\n")
for items in codegentable:
    f.write("     %s    :    %s     :     %s     :     %s      :      %s     :       %s     " % (str(items[0])+" "*(5-len(str(items[0]))), items[1]+" "*(12-len(items[1])),items[3]+" "*(12-len(items[3])),items[4]+" "*(25-len(items[4])),items[5]+" "*(40-len(items[5])),items[6]+" "*(10-len(items[6]))))
    f.write("\n")
f.write("\n")
f.write("ERROR MESSAGES")
f.write("\n")
f.write("\n")
for items in errormsg:
    f.write(items)
    f.write("\n")
f.close()
#---------------------------------------------------------------------------------------------------------------------










#List Object File Generator--------------------------------------------------------------------------------------------
open("obcode"+nsp+".txt", 'w').close()
f=open("obcode"+nsp+".txt","r+")
if(errormsg==[]):
    f.write(objectfile)
f.close()
