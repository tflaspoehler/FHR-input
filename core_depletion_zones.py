import numpy as np
import os
import sys
from scale_input import *

        
class core_class():
    def __init__(self, output="inp", tritants=1, planks=1, stripes=1, sections=5, axials=16):
        
        a_file = open("arrays.dat", "w")
        output_file = open(output, "w")
        
        self.triso          = scale_unit_class(open("input.triso.inp", "r").readlines())
        self.plates         =  multiple_scale_units("input.plates.inp")
        self.channels       =  multiple_scale_units("input.channels.inp")
        self.third_stack    = scale_unit_class(open("input.one_third_stack.inp", "r").readlines())
        self.assembly       = scale_unit_class(open("input.fuel_assembly.inp", "r").readlines())
        self.axial_assembly = scale_unit_class(open("input.full_assembly.inp", "r").readlines())
        
        self.material    = [i.replace('\n','').replace('\r','').replace('\t','') for i in open("input.material.inp", "r").readlines()]
        self.core_material    = open("input.core_materials.inp", "r").readlines()
                
        u = 1
        m = 101
        a = 1
        n_z = axials
        n_z_total = 16
        
        ## n_z = 1
        
        n_triso_arrays = planks * stripes * tritants * n_z
        n_stack_arrays = tritants * n_z
        
        triso_array = []        
        plate_array = []
        channel_array = []
        
        assembly_levels = []
        for i in range(0, n_z):
            ## print 7 channel units for this tritant axial slice of this assembly
            trits = []
            ## generate tritants either 1 or 3 per axial array within an assembly
            triso_array = []
            a_start = a
            au_start = u
            for j in range(0, tritants):
                a_tritent_start = a
            
                ## for this tritant / assembly o this axial level make the triso units
                for k in range(0, planks):
                    for p in range(0, stripes):
                        triso_array.append([])
                        a += 1
                        for s in range(0, sections):
                            self.triso.print_replace(output=output_file, unit=u, medias=[[101, m]])
                            triso_array[-1].append(u)
                            m += 1
                            u += 1

                            
                ## determine which arrays to fill into each plate 
                plate_array.append([])
                for k in range(0, len(self.plates)):
                    plate_array[-1].append(u)
                    if planks > 1:
                        if stripes > 1:
                            self.plates[k].print_replace(output=output_file, unit=u, arrays=[[101, (a_tritent_start+(k*2))], [102, (a_tritent_start+(k*2))+1]])
                            u += 1
                        else:
                            self.plates[k].print_replace(output=output_file, unit=u, arrays=[[101, a_tritent_start+k],       [102, a_tritent_start+k]])
                            u += 1
                    else:
                            self.plates[k].print_replace(output=output_file, unit=u, arrays=[[101, a_tritent_start],         [102, a_tritent_start]])
                            u += 1

                if j == 0:        
                    channel_array.append([])
                    for k in range(0, len(self.channels)):
                        self.channels[k].print_replace(output=output_file, unit=u)
                        channel_array[-1].append(u)
                        u += 1
                ## add array replacement with correct arrays for each tritent from this iteration
                ##     w/ multiple fuel assemblies we will need an ofset to everything that shouldn't be too hard to implement
                ## AT THIS POINT the code has gotten awawy from object orientedness which has to do with the SCALE inputs
                ##     being fairly basic and uninformed
                ##     w/ more knowledge and functiosn it would be easier to organize everything in a logical flow
                
                next_array = n_triso_arrays + (i*tritants) + j + 1
                
                self.third_stack.print_replace(output=output_file, unit=u, arrays=[[500, next_array]])
                trits.append(u)
                
                stack = "ara=" + repr(next_array) + " nux=1 nuy=13 nuz=1 prt=no typ=square fill "

                for c in range(0,6):
                    stack += repr(channel_array[-1][c]) + " "
                    stack += repr(  plate_array[-1][c]) + " "
                stack += repr(channel_array[-1][-1]) + " end fill"
                a_file.write(stack + "\n")
                u += 1
            if len(trits) > 1:
                self.assembly.print_replace(output=output_file, unit=u, holes=[[500,trits[0]], 
                                                           [501,trits[1]], 
                                                           [502,trits[2]]])
            else:
                self.assembly.print_replace(output=output_file, unit=u, holes=[[500,trits[0]], 
                                                           [501,trits[0]], 
                                                           [502,trits[0]]])
            assembly_levels.append(u)
            u += 1
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
        a_file.write("ara=1000 nux=1 nuy=1 nuz="+repr(n_z_total)+" prt=no typ=rhexagonal fill ")
        
        for level in assembly_levels:
            a_file.write(" ".join([repr(level) for i in range(0, n_z_total/n_z)]) + " ")
        a_file.write(" end fill\n")
        a_file.close()
        m_file = open("material.out","w")
        for i in range(0, m):
            for line in self.material:
                m_file.write(line.split()[0] + " " + repr(i+101) + " " + " ".join(line.split()[2:]) +'\n')
        for line in self.core_material:
            m_file.write(line)
        m_file.close()
        output_file.close()
        
        material = open("material.out", "r").readlines()
        geometry = open(output, "r").readlines()
        arrayeds = open("arrays.dat", "r").readlines()
        
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
        
        output_file.close()
        
output_file = "NEW_ASSEMBLY.inp"
##  lines, tritants=1, planks=1, strips=1):
## core = core_class(tritants=3, planks=6, stripes=2, sections=5)

## core = core_class(output=output_file, tritants=3, planks=6, stripes=2, sections=5)
axial_assembly = core_class(output="2d_test_case.inp", tritants=3, planks=1, stripes=1, sections=1, axials=2)

