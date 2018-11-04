import numpy as np
import os
import sys
from scale_input import *

        
class core_class():
    def __init__(self, output="inp", tritants=1, planks=1, stripes=1, sections=5, axials=16, assemblies=1, comments=False):
        
        ## -----------------------------------------
        ##  read and open input and output files
        a_file = open("arrays.dat", "w")
        output_file = open(output, "w")
        self.triso          = scale_unit_class(open("units/input.triso.inp", "r").readlines())
        self.plates         =  multiple_scale_units("units/input.plates.inp")
        self.channels       =  multiple_scale_units("units/input.channels.inp")
        self.third_stack    = scale_unit_class(open("units/input.one_third_stack.inp", "r").readlines())
        self.assembly       = scale_unit_class(open("units/input.fuel_assembly.inp", "r").readlines())
        self.axial_assembly = scale_unit_class(open("units/input.full_assembly.inp", "r").readlines())
        self.reflectors = multiple_scale_units("units/input.reflectors.inp")
        self.core = scale_unit_class(open("units/input.core.inp", "r").readlines())
        self.material    = [i.replace('\n','').replace('\r','').replace('\t','') for i in open("units/input.material.inp", "r").readlines()]
        self.core_material    = open("units/input.core_materials.inp", "r").readlines()
        ## -----------------------------------------
                
        
        ## -----------------------------------------
        ##     define parameters for assemblies
        u = 1
        m = 101
        a = 1
        n_z = axials
        n_z_total = 16
        n_triso_arrays = tritants * planks * stripes * n_z * assemblies
        n_stack_arrays = tritants * n_z
        assembly_units = []
        
        for assembly in range(0, assemblies):
            ## -----------------------------------------
            ##     define variables for bookkeeping
            triso_array = []        
            plate_array = []
            channel_array = []
            stacks = []
            trits = []
            triso_array = []
            a_start = a
            au_start = u
            
            for j in range(0, tritants):
                a_tritent_start = a
                for i in range(0, n_z):
                    ## for this tritant / assembly o this axial level make the triso units
                    for k in range(0, planks):
                        for p in range(0, stripes):
                            triso_array.append([])
                            a += 1
                            for s in range(0, sections):
                                self.triso.print_replace(output=output_file, unit=u, medias=[[101, m]], comments=comments)
                                triso_array[-1].append(u)
                                m += 1
                                u += 1

                    ###### ------------------------------------------------------------------------------------ 
                    ######        define plates and channels for this level and tritant
                    plate_array.append([])
                    for k in range(0, len(self.plates)):
                        plate_array[-1].append(u)
                        if planks > 1:
                            if stripes > 1:
                                self.plates[k].print_replace(output=output_file, unit=u, arrays=[[101, (a_tritent_start+(k*2))], [102, (a_tritent_start+(k*2))+1]], comments=comments)
                                u += 1
                            else:
                                self.plates[k].print_replace(output=output_file, unit=u, arrays=[[101, a_tritent_start+k],       [102, a_tritent_start+k]], comments=comments)
                                u += 1
                        else:
                                self.plates[k].print_replace(output=output_file, unit=u, arrays=[[101, a_tritent_start],         [102, a_tritent_start]], comments=comments)
                                u += 1
                    ######        only define coolant channels once per assembly level
                    if (j == 0):
                        channel_array.append([])
                        for k in range(0, len(self.channels)):
                            self.channels[k].print_replace(output=output_file, unit=u, comments=comments)
                            channel_array[-1].append(u)
                            u += 1
                    ###### ------------------------------------------------------------------------------------ 
                                
                ###### ------------------------------------------------------------------------------------ 
                ######        add channel and fuel stack for this trident over all axial layers
                next_array = n_triso_arrays + j + 1
                stack = ["ara=" + repr(next_array) + " nux=1 nuy=13 nuz=" + repr(n_z_total) + " prt=no typ=square fill "]
                
                for s in range(0, n_z):
                    for b in range(0, n_z_total/n_z):
                        stack.append("     ")
                        for c in range(0,6):
                            stack[-1] += repr(channel_array[0-n_z+(s)][c]) + " "
                            stack[-1] += repr(  plate_array[0-n_z+(s)][c]) + " "
                        stack[-1] += repr(channel_array[0-n_z+(s)][-1])
                stack[-1] += " end fill"
                
                stacks.append(stack)
                
                self.third_stack.print_replace(output=output_file, unit=u, arrays=[[500, next_array]], comments=comments)
                trits.append(u)
                u += 1
                ###### ------------------------------------------------------------------------------------
        
            ###### ------------------------------------------------------------------------------------ 
            ######        print array blocks to array.dat
            for j in range(0, len(triso_array)):
                if len(triso_array[j]) > 1:
                    a_file.write("ara="+repr(a_start+j)+" nux=202 nuy=5 nuz=371 prt=no typ=square fill" + " 41R" + repr(triso_array[j][0]+0)
                                                                                                        + " 40R" + repr(triso_array[j][0]+1)
                                                                                                        + " 40R" + repr(triso_array[j][0]+2)
                                                                                                        + " 40R" + repr(triso_array[j][0]+3)
                                                                                                        + " 41R" + repr(triso_array[j][0]+4)
                                                                                                        + " 1854Q202 end fill" + "\n")
                else:
                    a_file.write("ara="+repr(a_start+j)+" nux=202 nuy=5 nuz=371 prt=no typ=square fill " + repr(202*5*371) + "R" + repr(triso_array[j][0]) + " end fill" + "\n")

            for stack in stacks:   
                for stick in stack:
                    a_file.write(stick + "\n")
            ###### ------------------------------------------------------------------------------------
            
            
            ###### ------------------------------------------------------------------------------------
            ######        print out this assembly
            globe = True
            globe = False
            if (assemblies > 1):
                globe = False
            if len(trits) > 1:
                self.axial_assembly.print_replace(output=output_file, unit=u, holes=[[100,trits[0]], 
                                                                                     [101,trits[1]], 
                                                                                     [102,trits[2]]],
                                                                                     globe=globe, comments=comments)
            else:
                self.axial_assembly.print_replace(output=output_file, unit=u, holes=[[100,trits[0]], 
                                                                                     [101,trits[0]], 
                                                                                     [102,trits[0]]],
                                                                                     globe=globe, comments=comments)
            assembly_units.append(u)
            u += 1
            ###### ------------------------------------------------------------------------------------

        ###### ------------------------------------------------------------------------------------
        ######        print units for the reflector assemblies (and whatever else is left)
        for reflector in self.reflectors:
            reflector.print_replace(output=output_file, unit=u, comments=comments)
            u += 1
        ###### ------------------------------------------------------------------------------------

        ###### ------------------------------------------------------------------------------------
        ######        print the global core unit and the array for the core layout
        self.core.print_replace(output=output_file, unit=u, arrays=[[1, next_array+1]], globe=True, comments=comments)

        core_array = [[2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2],
                      [2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2],
                      [2,  2,  2,  2,  2,  2,  2,  2,  2,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,  2,  2],
                      [2,  2,  2,  2,  2,  2,  2,  1,  1,  3,  3,  3,  3,  3,  3,  3,  1,  1,  2,  2,  2,  2,  2,  2,  2],
                      [2,  2,  2,  2,  2,  1,  1,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  1,  1,  2,  2,  2,  2,  2],
                      [2,  2,  2,  2,  1,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  1,  2,  2,  2,  2],
                      [2,  2,  2,  1,  1,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  1,  1,  2,  2,  2],
                      [2,  2,  2,  1,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  1,  2,  2,  2],
                      [2,  2,  1,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  1,  2,  2],
                      [2,  2,  1,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  1,  2,  2],
                      [2,  2,  1,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  1,  2,  2],
                      [2,  2,  1,  3,  3,  3,  3,  3,  3,  3,  3,  3,  1,  3,  3,  3,  3,  3,  3,  3,  3,  3,  1,  2,  2],
                      [2,  2,  1,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  1,  2,  2],
                      [2,  2,  1,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  1,  2,  2],
                      [2,  2,  1,  1,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  1,  1,  2,  2],
                      [2,  2,  2,  1,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  1,  2,  2,  2],
                      [2,  2,  2,  2,  1,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  1,  2,  2,  2,  2],
                      [2,  2,  2,  2,  1,  1,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  1,  1,  2,  2,  2,  2],
                      [2,  2,  2,  2,  2,  2,  1,  1,  3,  3,  3,  3,  3,  3,  3,  3,  3,  1,  1,  2,  2,  2,  2,  2,  2],
                      [2,  2,  2,  2,  2,  2,  2,  2,  1,  1,  3,  1,  3,  1,  3,  1,  1,  2,  2,  2,  2,  2,  2,  2,  2],
                      [2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  1,  2,  1,  2,  1,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2],
                      [2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2],
                      [2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2]]
        for k in range(0, len(assembly_units)):
            done = False
            for j in range(0, len(core_array)):
                for i in range(0, len(core_array[j])):
                    if (core_array[j][i] == 1):
                        core_array[j][i] = u-2
                    if (core_array[j][i] == 2):
                        core_array[j][i] = u-1
                    if (core_array[j][i] == 3 and not done):
                        core_array[j][i] = assembly_units[k]
                        if (assemblies > 1):
                            done = True
        a_file.write("ara=" + repr(next_array+1) + "  nux=25 nuy=23 nuz=1 typ=rhexagonal" + "\n")
        a_file.write("  fill" + "\n")
        for j in range(0, len(core_array)):
            for i in range(0, len(core_array[j])):
                core_array[j][i] = repr(core_array[j][i])
                core_array[j][i] = " "*(len(repr(u))-len(core_array[j][i])+1) + core_array[j][i]
            a_file.write("      " + "".join(core_array[j]) + "\n")
        a_file.write("  end fill\n")
        ###### ------------------------------------------------------------------------------------
        
        
        
        
        
        ###### ------------------------------------------------------------------------------------
        ######        read in materials for the problem and copy the fuel units to be depleted
        m_file = open("materials.dat","w")
        for i in range(101, m):
            for line in self.material:
                if line[0] != "'":
                    m_file.write(line.split()[0] + " " + repr(i) + " " + " ".join(line.split()[2:]) +'\n')
                else:
                    m_file.write(line+'\n')
        for line in self.core_material:
            m_file.write(line)
        m_file.close()
        output_file.close()
        a_file.close()
        ###### ------------------------------------------------------------------------------------
        
        ###### ------------------------------------------------------------------------------------
        ######        read in all the blocks that were generated to compile into final input file
        material = open("materials.dat", "r").readlines()
        geometry = open(output, "r").readlines()
        arrayeds = open("arrays.dat", "r").readlines()
        ###### ------------------------------------------------------------------------------------
        
        ###### ------------------------------------------------------------------------------------
        ######        print input file
        output_file = open(output, "w")
        output_file.write("=csas6"+"\n")
        output_file.write("FHR"+"\n")
        output_file.write("ce_v7.1_endf"+"\n")
        
        output_file.write("read composition"+"\n")
        for m in material:
            output_file.write(m)
        output_file.write("end composition"+"\n")
        
        output_file.write("read parameters"+"\n")
        output_file.write("nsk=50"+"\n")
        output_file.write("gen=250"+"\n")
        output_file.write("npg=100000"+"\n")
        output_file.write("flx=yes"+"\n")
        output_file.write("end parameters"+"\n")        
        
        output_file.write("read geometry"+"\n")
        for g in geometry:
            output_file.write(g)
        output_file.write("end geometry"+"\n")       
        
        output_file.write("read array"+"\n")
        for a in arrayeds:
            output_file.write(a)
        output_file.write("end array"+"\n")
        
        if False:
            output_file.write("read bounds"+"\n")
            output_file.write("    surface(1)=mirror"+"\n")
            output_file.write("    surface(2)=mirror"+"\n")
            output_file.write("    surface(3)=mirror"+"\n")
            output_file.write("    surface(4)=mirror"+"\n")
            output_file.write("    surface(5)=mirror"+"\n")
            output_file.write("    surface(6)=mirror"+"\n")
            output_file.write("    surface(7)=mirror"+"\n")
            output_file.write("    surface(8)=mirror"+"\n")
            output_file.write("end bounds"+"\n")

        output_file.write("end data"+"\n")
        output_file.write("end"+"\n")
        ###### ------------------------------------------------------------------------------------
        
        output_file.close()
        
axial_assembly = core_class(output="assembly.inp", tritants=1, planks=1, stripes=1, sections=1, axials=16)

full_core      = core_class(output="full_core.16ax.3tri.inp", tritants=3, planks=1, stripes=1, sections=1, axials=16, assemblies=252)
full_core      = core_class(output="full_core.16ax.single-assembly.inp", tritants=1, planks=1, stripes=1, sections=1, axials=16, assemblies=252)
full_core      = core_class(output="full_core.single-assembly.inp", tritants=1, planks=1, stripes=1, sections=1, axials=1, assemblies=1, comments=True)

