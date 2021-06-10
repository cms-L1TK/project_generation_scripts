# Creates a reduced configuration when given a TC phi region
# Takes a full configuration as input

# Example line from input wires.dat
# Memory              Input node                     Output node
# AS_L1PHICn4 input=> VMR_L1PHIC.allstubout output=> TC_L1L2E.innerallstubin

verbose = False

class node:
    def __init__(self, name):
        self.name = name
        self.connections = []

    def addConnection(self, c):
        for c_ref in self.connections:
            if c.isSame(c_ref): return
        self.connections.append(c)

    def getInputConnections(self):
        found_connections = []
        for c in self.connections:
            if c.coutput.name == self.name: found_connections.append(c)
        return found_connections

    def getOutputConnections(self):
        found_connections = []
        for c in self.connections:
            if c.cinput.name == self.name: found_connections.append(c)
        return found_connections

class connection:
    def __init__(self, memory, cinput, coutput, cinext, coutext):
        self.memory = memory
        self.cinput = cinput
        self.coutput = coutput
        self.cinext = cinext
        self.coutext = coutext

    def printConnection(self):
        out_str = self.memory
        out_str += " input=> %s"%self.cinput.name
        if self.cinext != "": out_str += ".%s "%self.cinext
        out_str += "output=>"
        if self.coutput.name != "": out_str += " %s"%self.coutput.name
        if self.coutext != "": out_str += ".%s"%self.coutext
        return out_str

    def isSame(self, c_ref):
        if self.memory != c_ref.memory: return False
        if self.cinput.name != c_ref.cinput.name: return False
        if self.coutput.name != c_ref.coutput.name: return False
        if self.cinext != c_ref.cinext: return False
        if self.coutext != c_ref.coutext: return False
        return True

class project:
    def __init__(self):
        self.connections = []
        self.nodes = {}
        self.tcs = []
        self.l1phis = []
        self.lxphis = []

    def addNode(self, n):
        if n.name not in self.nodes:
            self.nodes[n.name] = n
        else:
            for c in n.connections:
                self.nodes[n.name].addConnection(c)

    def addConnection(self, c):
        for c_ref in self.connections:
            if c.isSame(c_ref): return
        self.connections.append(c)

    # Load in a project from a wires file
    def loadProject(self, fname):
        with open(fname, "r") as f:
            for line in f:

                # Get raw names from wires file
                mem = line.split("input=>")[0].strip()
                str_in = line.split("input=>")[1].split("output=>")[0].strip()
                str_out = line.split("output=>")[1].strip()

                # Create nodes and extensions from strings
                node_in = node(str_in.split(".")[0])
                in_ext = str_in.split(".")[1] if "." in str_in else ""
                node_out = node(str_out.split(".")[0])
                out_ext = str_out.split(".")[1] if "." in str_out else ""

                # Add connection and nodes to project
                new_c = connection(mem, node_in, node_out, in_ext, out_ext)
                self.addConnection(new_c)
                node_in.addConnection(new_c)
                node_out.addConnection(new_c)
                self.addNode(node_in)
                self.addNode(node_out)

    # Save a project to a wires file
    def saveProject(self, fname):
        with open(fname, "w") as f:
            for c in self.connections:
                f.write(c.printConnection()+"\n")

    def addTC(self, tc, ref_p):
        tcs = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
        l1phis = ["A", "B", "C", "D", "E", "F", "G", "H"]
        lxphis = ["A", "B", "C", "D"]

        if tc.upper() not in tcs:
            print "Bad TC index, not adding."
            return

        tc_i = tcs.index(tc.upper())
        phi1_i = int(tc_i*1.*len(l1phis)/len(tcs))
        phix_i = int(tc_i*1.*len(lxphis)/len(tcs))

        print "Adding regions to project: TC_L1l2%s, L1PHI%s, LxPHI%s"%(tcs[tc_i], l1phis[phi1_i], lxphis[phix_i])
        self.tcs.append(tcs[tc_i])
        self.l1phis.append(l1phis[phi1_i])
        self.lxphis.append(lxphis[phix_i])

        # Add nodes and connections to the project
        # Starting with TC_L1L2x and moving up and down the chain

        print "Starting with node TC_L1L2%s"%tcs[tc_i]
        n = node("TC_L1L2%s"%tcs[tc_i])
        self.addNode(n)
        print "Finding inputs..."
        self.findInputConnections(n, ref_p)
        print "Finding outputs..."
        self.findOutputConnections(n, ref_p)

    def findInputConnections(self, n, ref_p):
        if verbose: print "\t", n.name
        ref_node = ref_p.nodes[n.name]
        ref_inputs = ref_node.getInputConnections()
        if verbose: print "\tInputs:", ["%s -> %s"%(r.cinput.name, r.coutput.name) for r in ref_inputs]
        for ref_c in ref_inputs:
            ref_n = ref_c.cinput
            if self.isIncluded(ref_n):
                if verbose: print "\t\t", "Found good input!:", ref_n.name
                in_n = node(ref_n.name)
                in_c = connection(ref_c.memory, in_n, n, ref_c.cinext, ref_c.coutext)
                n.addConnection(in_c)
                in_n.addConnection(in_c)
                self.addConnection(in_c)
                if in_n.name != "" and in_n.name not in self.nodes:
                    self.addNode(in_n)
                    self.findInputConnections(in_n, ref_p)

    def findOutputConnections(self, n, ref_p):
        if verbose: print "\t", n.name
        ref_node = ref_p.nodes[n.name]
        ref_outputs = ref_node.getOutputConnections()
        if verbose: print "\tOutputs:", ["%s -> %s"%(r.cinput.name, r.coutput.name) for r in ref_outputs]
        for ref_c in ref_outputs:
            ref_n = ref_c.coutput
            if self.isIncluded(ref_n):
                if verbose: print "\t\t", "Found good output!:", ref_n.name
                out_n = node(ref_n.name)
                out_c = connection(ref_c.memory, n, out_n, ref_c.cinext, ref_c.coutext)
                n.addConnection(out_c)
                out_n.addConnection(out_c)
                self.addConnection(out_c)
                if out_n.name != "" and out_n.name not in self.nodes:
                    self.addNode(out_n)
                    self.findOutputConnections(out_n, ref_p)

    def isIncluded(self, n):
        if n.name.startswith("TC_L1L2"):
            for tc in self.tcs:
                if n.name == "TC_L1L2%s"%tc: return True
            return False
        if n.name.startswith("TE_L1PHI"):
            for l1 in self.l1phis:
                for lx in self.lxphis:
                    if "L1PHI%s"%l1 in n.name and "L2PHI%s"%lx in n.name: return True
            return False
        if "L1PHI" in n.name:
            for l1 in self.l1phis:
                if "L1PHI%s"%l1 in n.name: return True
            return False
        if "PHI" in n.name:
            for lx in self.lxphis:
                for x in [2,3,4,5,6]:
                    if "L%sPHI%s"%(x,lx) in n.name: return True
            return False
        if n.name in ["FT_L1L2", "PD", ""]: return True
        return False

# ----------------------------------------------------
# Main function
# ----------------------------------------------------

# Load in full project
print "Loading full wire project..."
full_wires = project()
full_wires.loadProject("wires.dat")
full_wires.saveProject("test.dat")

# Set up reduced project and give it a phi sector in L1
print "Finding reduced configuration..."
reduced_wires = project()
reduced_wires.addTC("F", full_wires)
reduced_wires.saveProject("reduced_wires.dat")

