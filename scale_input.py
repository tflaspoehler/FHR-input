
class comment_class():
    def __init__(self, line):
        self.line = line

class unit_class():
    def __init__(self, line):
        self.line = line
        self.id = int(line.split()[-1])

class hole_class():
    def __init__(self, line):
        self.line = line
        self.id = int(line.split()[1])

class boundary_class():
    def __init__(self, line):
        self.line = line
        self.id = int(line.split()[1])

class media_class():
    def __init__(self, line):
        self.line = line
        self.id = int(line.split()[1])

class array_class():
    def __init__(self, line):
        self.line = line
        self.id = int(line.split()[1])

class geometry_class():
    def __init__(self, line):
        self.line = line
        self.id = int(line.split()[1])  

class scale_unit_class():
    def __init__(self, lines):
        lines = [i.replace("\n","").replace("\r","").replace("\t"," ") for i in lines]
        self.defs = []
        self.lines = []
        while len(lines) > 0:
            line = lines.pop(0)
            if len(line) < 1:
                pass
            else:
                if line[0] == "'":
                    self.lines.append(comment_class(line))
                elif "com" in line.split()[0] and "=" in line.split()[0]:
                    self.lines.append(comment_class(line))
                elif line.split()[0] == "unit":
                    self.lines.append(unit_class(line))
                elif line.split()[0] == "media":
                    self.lines.append(media_class(line))
                elif line.split()[0] == "hole":
                    self.lines.append(hole_class(line))
                elif line.split()[0] == "array":
                    self.lines.append(array_class(line))
                else:
                    self.lines.append(geometry_class(line))
    def print_replace(self, output="inp", unit=0, medias=[], arrays=[], holes=[], globe=False, comments=False):
        for line in self.lines:
        
            if line.line.split()[0] == "unit":
                if unit != 0:
                    if globe==True:
                        output.write("global unit " + repr(unit)+"\n")
                    else:
                        output.write("unit " + repr(unit)+"\n")
                else:
                    if globe==True:
                        output.write("global unit " + line.line+"\n")
                    else:
                        output.write(line.line+"\n")
            elif line.line.split()[0] == "media":
                l = line.line
                for media in medias:
                    if media[0] == line.id:
                        l = "  " + line.line.split()[0] + " " + repr(media[1]) + " " + " ".join(line.line.split()[2:])
                        break
                output.write(l+"\n")
            elif line.line.split()[0] == "array":
                l = line.line
                for array in arrays:
                    if array[0] == line.id:
                        l = "  " + line.line.split()[0] + " " + repr(array[1]) + " " + " ".join(line.line.split()[2:])
                        break
                output.write(l+"\n")
            elif line.line.split()[0] == "hole":
                l = line.line
                for hole in holes:
                    if hole[0] == line.id:
                        if len(line.line.split()) > 2:
                            l = "  " + line.line.split()[0] + " " + repr(hole[1]) + " " + " ".join(line.line.split()[2:])
                        else:
                            l = "  " + line.line.split()[0] + " " + repr(hole[1])
                        break
                output.write(l+"\n")
            elif line.line[0] == "'":
                if comments:
                    output.write(line.line+"\n")
            elif "com" in line.line.split()[0] and "=" in line.line.split()[0]:
                if comments:
                    output.write(line.line+"\n")
            else:
                output.write(line.line+"\n")
                
def multiple_scale_units(input_file):
    lines = open(input_file, "r").readlines()
    unit_lines = [0]
    for i in range(0, len(lines)):
        if lines[i].split()[0] == "boundary":
            unit_lines.append(i)
    unit_lines.pop(len(unit_lines)-1)
    unit_lines.append(len(lines))
    units = []
    for i in range(0, len(unit_lines)-1):
        units.append(scale_unit_class(lines[unit_lines[i]+1:unit_lines[i+1]+1]))
    return units
        