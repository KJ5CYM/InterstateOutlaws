#! /usr/bin/python
import os
import sys
import string

# some constants
GETTER = 0
SETTER = 1

# output control
DEBUG = 0 # 	debugging ouput
PRINT_UNHANDLED = 0 # output comments about impossible (for now) to handle methods,
PRINT_IGNORED = 0   # output comments about ignored vars
PRINT_LISTS = 0     # output comments about possible pseudolists in interface
PRINT_ITERATORS = 0 # output comments about iterator interfaces
PRINT_FIXES = 0     # output comments about special fixes
PRINT_WEIRDS = 0    # output comments about weird methods found.
PRINT_UNPARSED = 0  # output comments about unparsed lines
PRINT_FILTERED = 0  # output comments about functions with filtered parameters (due to
PRINT_CONFLICTS = 0  # output comments about attribute names in conflict with function names
                    # swig OUTPUT mappings)
STATISTICS = 1      # output statistics

# statistics
unhandled_count = 0
handled_count = 0

# dictionary to hold enum scopes
enums = {}

# global dictionary to hold some data
scandict = {}
scandict["listlike"] = []
scandict["purelist"] = []
scandict["iterators"] = []
scandict["conflicts"] = []
###################################
# Structs to hold parsed data
###################################

class csinterface:
    def __init__(self,name):
        self. name = name
        self.header = ''
        self.attributes = []
	self.allmethods = []
        self.hasiterator = False

class csattribute:
    def __init__(self,name):
        self.name = name
        self.getters = []
        self.setters = []
	self.ignore = False
        
class csmethod:
    def __init__(self,name):
        self.name = name
        self.returntype = ''
        self.fpars = ''
        self.fullpars = ''

class csfuncpar:
    def __init__(self,partype,parname,signature,pardefault=None):
        self.name = parname
        self.type = partype
        self.default = pardefault
        self.signature = signature

###################################
# Cpp parsing code
###################################

def parseFunctionParameters(funcpars):
    # add space after * to separate from parameter name
    rawpars = funcpars.replace("*","* ")
    pars = []
    # separate default argument from parameter name
    rawpars = " = ".join(map(lambda s: s.strip(),rawpars.split("=")))
    # split parameters
    rawpars = map(lambda p: p.strip(), rawpars.split(','))
    # parse each parameter
    for rawpar in rawpars:
        pardefault = None
        parname = None
        parsignature = None
        # check default value
        rawpar = rawpar.split('=')
        if len(rawpar)>1:
            pardefault = rawpar[1].strip()
        # check name
        rawpar = rawpar[0].strip().split(' ')
	if len(rawpar)>1:
            parsignature = "".join(rawpar)
            parname = rawpar[-1:]
            rawpar = rawpar[:-1]
        # check type
        partype = " ".join(rawpar).strip()
	if partype in enums:
	    if enums[partype]:
	        partype = enums[partype]+"::"+partype
        if partype:
            newpar = csfuncpar(partype,parname,parsignature,pardefault)
	    pars.append(newpar)
    if len(pars) == 1 and pars[0].type == "void":
        pars = []
    return pars

# filter out parameters with swig OUTPUT mappings
def filterOutputFunctionParameters(funcpars):
    fpars = []
    for par in funcpars:
        if not (par.signature and par.signature in scandict["outpars"]):
            fpars.append(par)
    return fpars

###################################
# CS header parsing code
###################################

#Check a line from within an interface, and give it an attribute if found
def checkMethod(interface, line, method,methodtype,exclusions,doignores):
    line = line.replace("*","* ")
    if "GlobalIterator" in line:
        return
    if line.startswith("delete") or line.startswith("return"):
        return
    if line.startswith('virtual') or line.startswith('inline'):
        endidx = line.find("(")
        startidx = line[:endidx].strip().rfind(" ")
        methodname = line[startidx:endidx].strip()
        if methodname and not methodname in interface.allmethods:
            if interface.name in doignores and methodname in doignores[interface.name]:
                return
	    interface.allmethods.append(methodname)
    line = line.replace("virtual","").strip()
    line = line.replace("inline","").strip()
    if line.find(' ' + method) > 0 and not "static" in line and not line.startswith("typedef"):
        # parse input parameters
        splitline = line.split('(')
        if not len(splitline) >1:
            print "/* cant parse",line,"*/"
            return
        rawpars = splitline[1].split(')')[0]
        if "/*" in rawpars:
            if PRINT_IGNORED:
                print "/* Ignore commented method:",line,"*/"
            return
        fullpars = parseFunctionParameters(rawpars)
        fpars = filterOutputFunctionParameters(fullpars)
        splitline = splitline[0].replace("*","* ").split(' ')
	filteredmethod = filter(lambda s: s.startswith(method), splitline)
	if not filteredmethod:
            if DEBUG:
                print "/* CANT PARSE",splitline,"*/"
            return
        splitmethod = filteredmethod[0]
        # Check the method is not in the exclusions list
        for a in exclusions:
	    if splitmethod.startswith(a):
                return
        returntype = ''
        for word in splitline[:splitline.index(splitmethod)]:
            returntype += word + ' '
        returntype = returntype.strip()
	if "=" in returntype: # not a method
            return
	if returntype in enums.keys():
            if enums[returntype]:
                returntype = enums[returntype]+"::"+returntype
        # Check the method is not plain 'Get', 'Set' etc
        if splitmethod != method:
            newmethod = csmethod(method)
            newmethod.returntype = returntype
            newmethod.fpars = fpars
            newmethod.fullpars = fullpars
            newattribute = splitmethod.split(method)[1]
            #Check if that attribute already exists within the interface
            attribute = filter(lambda p: p.name == newattribute,interface.attributes)
            if attribute:
                attribute = attribute[0]
                if methodtype == GETTER:
                    attribute.getters.append(newmethod)
                else:
	            attribute.setters.append(newmethod)
                if attribute.ignore and PRINT_IGNORED:
	            print "/* ignored attribute:",interface.name+"::"+newattribute,"*/"
            #No attribute of the name existed, time to make a new one
            else:
                attr = csattribute(newattribute)
		if methodtype == GETTER:
                    attr.getters.append(newmethod)
		else:
                    attr.setters.append(newmethod)
                interface.attributes.append(attr)
    elif line.find(' ' + method) > 0:
        if PRINT_UNPARSED:
            print "/* unparsed method",interface.name,line,"*/"
    # check member variables in class
    elif line.endswith(";") and len(line.split()) == 2 and not ")" in line:
	splitname = line.split()[1][:-1].strip()
        foundattr = filter(lambda p: p.name == splitname,interface.attributes)
        if not foundattr:
            attr = csattribute(splitname)
	    attr.ignore = True
	    interface.attributes.append(attr)
            if PRINT_IGNORED:
	        print "/* ignore:",interface.name+"::"+splitname,"*/"
        else:
            if not foundattr[0].ignore:
                foundattr[0].ignore = True
                if PRINT_IGNORED:
	            print "/* ignore existing:",interface.name+"::"+splitname,"*/"
# parse enums
def checkEnum(line,interface,scope):
    if line.startswith("enum") and not interface == None:
        splitenum = line.split()
        if len(splitenum) > 1:
	    # some enums are scoped
	    if scope:
	        enums[splitenum[1]] = scope
	    else:
	        enums[splitenum[1]] = ""

def findIteratorMethods(interfaces):
    for interface in interfaces:
        if "Next" in interface.allmethods and "HasNext" in interface.allmethods:
            scandict["iterators"].append(interface.name)
            for attribute in interface.attributes:
                if attribute.name == "Next":
                    attribute.ignore = True
            interface.hasiterator = True
    return interfaces

# find list methods
def findListMethods(interfaces):
    for interface in interfaces:
      for attribute in interface.attributes:
        for getter in attribute.getters:
            lists = []
            if attribute.name.endswith("Count") and getter.name == "Get":
                attrname = attribute.name.replace("Count","")
                has_count = True
                methods = []
                if "Get"+attrname+"ByName" in interface.allmethods:
                    methods.append("byname")
                elif "Find"+attrname+"ByName" in interface.allmethods:
                    methods.append("byname")
                if "Remove"+attrname in interface.allmethods:
                    methods.append("rem")
                if "Remove"+attrname+"s" in interface.allmethods:
                    methods.append("remall")
                if "Get"+attrname in interface.allmethods:
                    methods.append("getter")
                if "Add"+attrname in interface.allmethods:
                    methods.append("adder")
                if "Set"+attrname in interface.allmethods:
                    methods.append("setter")
                if "Find"+attrname in interface.allmethods:
                    methods.append("find")
                if len(methods):
                    if not attrname:
                        scandict["purelist"].append(interface.name)
                    else:
                        scandict["listlike"].append(interface.name+"::"+attrname)
    return interfaces

# fix methods with strange names
def fixWeirdMethods(interfaces):
    for interface in interfaces:
      for attribute in interface.attributes:
        for getter in attribute.getters:
    	    weirds = []
            # this is to find about GetAttachedLight/AttachLight kind
            # also FindAttachedEntity/AttachEntity for example.
	    if "Attached" in attribute.name:
                weirdname = attribute.name.replace("Attached","Attach")
                if weirdname in interface.allmethods:
                    weirds.append(weirdname)
	    elif getter.name == "Is":
                # this is to find about Run/IsRunning, Forward/IsMovingForward
                # kind.
		ingindex = attribute.name.find("ing")
		ningindex = attribute.name.find("ning")
		if not ningindex == -1:
		    weirdname = attribute.name[:ningindex]
		    if weirdname in interface.allmethods:
	            	weirds.append(weirdname)
                # this is to find about SetStrafeLeft and IsStrafingLeft kind
		elif not ingindex == -1:
		    weirdname1 = attribute.name.replace("ing","e")
		    weirdname2 = attribute.name[ingindex+3:]
		    if weirdname1 in interface.allmethods:
			weirds.append(weirdname1)
		    if weirdname2 in interface.allmethods:
			weirds.append(weirdname2)
            # found one weird alternative
	    if len(weirds) == 1:
                if PRINT_WEIRDS:
                    print "/* WEIRD",interface.name,attribute.name,weirds[0],"*/"
                newmethod = csmethod(weirds[0])
                newmethod.returntype = "void"
                newmethod.fpars = [csfuncpar(getter.returntype,None,None)]
                newmethod.funcpars = newmethod.fpars
		attribute.setters.append(newmethod)
	    elif len(weirds):
		if PRINT_UNHANDLED:
 		    print "/*MANY WEIRD METHODS FOR",attribute.name,weirds+"*/"
		unhandleds[12]+=1
    return interfaces

# The beef of the code. Searches a file for interfaces, and the getters 
# and setters within it.
def parseFile(filename,doignores):
    if DEBUG:
        print "/* ",filename,"*/"
    interfaces = []
    interface = None
    prevline = ""
    scope = ""
    incomment = False
    inprivate = False
    # parse file
    file = open(filename, 'r')
    bracketcount = 0
    for line in file:
        # jump comments
        if incomment:
            if not "*/" in line:
                continue
            else:
                incomment = False
        line = line.strip()
	if line.startswith("/*") and not "*/" in line:
            incomment = True
            continue
        if line.startswith("//"):
            continue
	# skip private section
	if line.startswith("public:"):
            inprivate = False
	if line.startswith("private:"):
            inprivate = True
        # check empty lines
        if not line:
            continue
        # delete scope when out of scope
        if line.startswith("{"):
            bracketcount+=1
        if "}" in line:
            bracketcount-=1
        if bracketcount == 0:
            scope = ""
        # dont parse private sections
        if inprivate:
            continue
        # continue unfinished lines
        if prevline:
            line = prevline + line
            prevline = ""
        # check scf macros
        if line.startswith('SCF_INTERFACE') or line.startswith("SCF_VERSION"):
            # Found a new interface
            # find name
            splitline = line.split('(')
            splitline = splitline[1].split(',')
            # create interface
            interface = csinterface(splitline[0].strip())
            if DEBUG:
                print "/*",interface.name,"*/"
            # Need to make the path relative to the base
            relpath = filename.split('include/')
            # Add the include for the buildsystem, I think
            interface.header = 'include/' + relpath[1]
            if not interface.name == scope:
	        scope = ""
                bracketcount=0
            # add interface to list
            interfaces.append(interface)
        # check struct start
	if line.startswith('struct') and interface and interface.name in line:
            inprivate = False
	    scope = interface.name
            bracketcount=0
	elif line.startswith('struct') and not ";" in line:
            inprivate = False
	    if len(line.split())>1:
	        scope = line.split()[1].strip()
                bracketcount=0
	elif ((line.startswith('class') and "CS_CRYSTALSPACE_EXPORT " in line) or (line.startswith('class') and not ";" in line)) and not "DEPRECA" in line:
            inprivate = True
            splitline = line.split(" ")
            if "CS_CRYSTALSPACE_EXPORT " in line:
                    ifacename = splitline[2]
            else:
                    ifacename = splitline[1]
            if ifacename:
                interface = csinterface(ifacename)
                relpath = filename.split('include/')
                interface.header = 'include/' + relpath[1]
                scope = interface.name
                bracketcount=0
                interfaces.append(interface)
        # check for unfinished line
	if line.startswith("virtual") and not ")" in line:
	    prevline = line
	    continue
        # check for unfinished from template declaration
	if line.startswith("template"):
            splitline = line[line.rfind(">"):]
            if not "class" in splitline:
	    	prevline = line
	    continue
	if line.startswith("CS_DEPRECATED_") and not ";" in line:
	    prevline = line+" "
	    continue
	if line.endswith("\\"):
	    prevline = line
	    continue
        # check for enums
        checkEnum(line,interface,scope)
        # parse interface
        if interface is not None:
            checkMethod(interface, line, 'Set', SETTER,['Setup'],doignores)
            checkMethod(interface, line, 'Get', GETTER,[],doignores)
            checkMethod(interface, line, 'Query', GETTER,[],doignores)
            checkMethod(interface, line, 'Is', GETTER,['IsZero'],doignores)
            checkMethod(interface, line, 'Has', GETTER,[],doignores)
	    prevline = ""
    # finish reading
    file.close()
    # now have to check if Is methods have a get method with stupid name
    interfaces = fixWeirdMethods(interfaces)
    # check for list interfaces
    interfaces = findListMethods(interfaces)
    interfaces = findIteratorMethods(interfaces)
    return interfaces

###################################
# Comment output code
###################################

unhandled_messages = [ "Attribute name starts with a digit",
    "Setter with too many pars",
    "Setter with no pars",
    "Getter with pars",
    "Returntype with commas",
    "Too many setters",
    "Getter with inputs",
    "Write only multiattr",
    "Too many get and set methods",
    "Too many setter methods",
    "Too many getter methods",
    "No getter or setter",
    "Too many weird methods"]

unhandleds = [0,0,0,0,0,0,0,0,0,0,0,0,0]

def unhandled(idx,debug_text=None):
	global unhandled_count
	unhandled_count+=1
	unhandleds[idx]+=1
	if PRINT_UNHANDLED:
		if not debug_text:
			debug_text = unhandled_messages[idx]
		print "/*"+debug_text+"*/"

def printfix(msg):
    if PRINT_FIXES:
        print "/* FIX:",msg,"*/"

# print debug info for an interface
def printInterfaceDebug(interface):
    print 'Interface:', interface.name, ' ========================='
    for attribute in interface.attributes:
        print ' ', attribute.name
        for method in attribute.getters+attribute.setters:
            print '   Type:', method.name, 'returns:', method.returntype, 'in:',method.fpars

def printFullDebugInfo(interfaces):
    if DEBUG:
        print "/*"
        for interface in interfaces:
            printInterfaceDebug(interface)
        print "*/"

def printStats():
    if not STATISTICS:
        return
    if scandict["mode"] is 2:
    	print '"""'
    else:
    	print "/*"
    print "Total attributes:", handled_count
    print "Total possible lists:", len(scandict["listlike"])
    print "Total iterators:", len(scandict["iterators"])
    print "Total possible purelists:", len(scandict["purelist"])
    print "Total conflicting methods:", len(scandict["conflicts"])
    print "Total unhandled methods:", unhandled_count
    for i in range(len(unhandled_messages)):
        print " ",unhandled_messages[i],unhandleds[i]
    if PRINT_CONFLICTS:
        print "Conflicting methods:"
        for a in scandict["conflicts"]:
            print a
    if scandict["mode"] is 2:
    	print '"""'
    else:
    	print "*/"

def printExtra():
    if PRINT_LISTS:
        print "/*\n LIST LIKE INTERFACES"
        for a in scandict["listlike"]:
            print a
        print "\n PURE LIST INTERFACES"
        for a in scandict["purelist"]:
            print a
        print "*/"

    if PRINT_ITERATORS:
        print "/*\n ITERATOR INTERFACES"
        for a in scandict["iterators"]:
            print a
        print "*/"

###################################
# Code for outputting the python info
###################################
def py_attr(interface,attribute,getmethod=None,setmethod=None):
	prefix = scandict["prefix"]
	if getmethod:
	    lgetmethod = "_"+prefix+"."+interface.name+"_"+getmethod.name+attribute.name
	else:
	    lgetmethod = "None"
	if setmethod:
	    setmethodname = setmethod.name
	    if setmethodname == "Set":
	        setmethodname+=attribute.name
	    lsetmethod = "_"+prefix+"."+interface.name+"_"+setmethodname
	    print prefix+"."+interface.name+".__swig_setmethods__['"+attribute.name+"'] = "+ lsetmethod
	else:
	    lsetmethod = "None"
	proptext = "property("+lgetmethod+","+lsetmethod+")"
	print prefix+"."+interface.name+"."+attribute.name+" = "+proptext

def py_multiattr(interface,attribute,getmethod=None,setmethod=None):
	prefix = scandict["prefix"]
	if getmethod:
	    lgetmethod = "_"+prefix+"."+interface.name+"_"+getmethod.name+attribute.name
	else:
	    lgetmethod = "None"
	if setmethod:
	    setmethodname = setmethod.name
	    if setmethodname == "Set":
	        setmethodname+=attribute.name
	    lsetmethod = "fix_args(_"+prefix+"."+interface.name+"_"+setmethodname+")"
	    print prefix+"."+interface.name+".__swig_setmethods__['"+attribute.name+"'] = "+ lsetmethod
	else:
	    lsetmethod = "None"
	proptext = "property("+lgetmethod+","+lsetmethod+")"
	print prefix+"."+interface.name+"."+attribute.name+" = "+proptext

###################################
# Code for outputting the swig info
###################################
def swig_attr(interface,attribute,getmethod=None,setmethod=None):
        prefix = scandict["prefix"]
        # one get method
	if not getmethod:
                setmethodtype = setmethod.fpars[0].type
		print "%cs_attribute_writeonly("+prefix+","+interface.name+", "+setmethodtype+", "+attribute.name+", "+setmethod.name+attribute.name+")"
        elif not len(getmethod.fpars) == len(getmethod.fullpars):
		if PRINT_FILTERED:
                	print "/*","FILTERED",attribute.name,"*/"
		swig_multiattr(interface,attribute,getmethod,setmethod)
		return
	elif not setmethod:
                methodtype = getmethod.returntype
		print "%cs_attribute("+prefix+","+interface.name+","+methodtype+","+attribute.name+","+getmethod.name+attribute.name+")"
        # one set method
	elif getmethod.name == "Get" and setmethod.name  == "Set":
                methodtype = getmethod.returntype
		print "%cs_attribute("+prefix+","+interface.name+","+methodtype+","+attribute.name+")"
	elif setmethod and getmethod:
                if not setmethod.fpars[0].type == getmethod.returntype:
			swig_multiattr(interface,attribute,getmethod,setmethod)
			return
                methodtype = getmethod.returntype
		setmethodname = setmethod.name
		if setmethodname == "Set":
			setmethodname+=attribute.name
		print "%cs_attribute("+prefix+","+interface.name+","+methodtype+","+attribute.name+","+getmethod.name+attribute.name+","+setmethodname+")"
	else:
		print "/* Unexpected parsing",attribute.name,"*/"

def  swig_multiattr(interface,attribute,getmethod,setmethod):
        prefix = scandict["prefix"]
	if setmethod and getmethod:
		print "%cs_multi_attr("+prefix+","+interface.name+","+attribute.name+","+getmethod.name+attribute.name+","+setmethod.name+attribute.name+")"
	elif getmethod:
		print "%cs_multi_attr_readonly("+prefix+","+interface.name+","+attribute.name+","+getmethod.name+attribute.name+")"
	elif setmethod:
		print "%cs_multi_attr_writeonly("+prefix+","+interface.name+","+attribute.name+","+setmethod.name+attribute.name+")"
	else:
		print "/* Unexpected parsing",attribute.name,attribute.getters,attribute.setters,"*/"

###################################
# Main attribute ourput methods
###################################
def write_attr(interface,attribute,getmethod=None,setmethod=None):
	if scandict["mode"] == 2:
		py_attr(interface,attribute,getmethod,setmethod)
	elif scandict["mode"] == 1:
		swig_attr(interface,attribute,getmethod,setmethod)
def write_multiattr(interface,attribute,getmethod=None,setmethod=None):
	if scandict["mode"] == 2:
		py_multiattr(interface,attribute,getmethod,setmethod)
	elif scandict["mode"] == 1:
		swig_multiattr(interface,attribute,getmethod,setmethod)

# output macros for swig
def outputAttribute(interface,attribute):
        global handled_count
	# avoid wrapping attributes that collide with some function 
	# of same name
	if attribute.name in interface.allmethods:
		scandict["conflicts"].append(interface.name+"::"+attribute.name)
		return
	if attribute.ignore:
                if PRINT_IGNORED:
		    print "/* ignored:",attribute.name,"*/"
		return
        handled_count+=1
	if attribute.name[0] in string.digits:
	    unhandled(0,"Attribute name starts with a digit")
	    return
	# fix cases with Has and Get methods
	if len(attribute.getters)>1:
            get_methods = filter(lambda x: x.name == "Get",attribute.getters)
            has_methods = filter(lambda x: x.name in ["Has","Is"],attribute.getters)
            if len(get_methods) == 1:
                printfix("1")
                attribute.getters = get_methods
            elif has_methods and get_methods:
                printfix("2")
                attribute.getters = [get_methods[0]]
	# fix cases were several getters where detected but only one receives no inputs
        if len(attribute.getters)>1:
            found_method = filter(lambda x: len(x.fpars) == 0, attribute.getters)
            if found_method:
                printfix("4")
                attribute.getters = [found_method[0]]
        # fix cases with several getters where some have void return type
	if len(attribute.getters)>1:
                printfix("3")
                attribute.getters = filter(lambda x: not x.returntype == "void",
                                           attribute.getters)
	# fix cases were several getters where detected with same return value
	if len(attribute.getters)>1:
		rettypes = [attribute.getters[0].returntype]
                
		for attr_getter in attribute.getters[1:]:
			if attr_getter.returntype in rettypes:
				attribute.getters.pop(attribute.getters.index(attr_getter))
			else:
				rettypes.append(attr_getter.returntype)
        # fix cases where getter only has input pars with defaults
        for getmethod in attribute.getters:
            if len(getmethod.fpars):
                printfix("5")
                getmethod.fpars = filter(lambda s: not s.default,getmethod.fpars)
	# now the real attribute output
	# one getter and one setter
	if len(attribute.getters) == 1 and len(attribute.setters) == 1:
		getmethod = attribute.getters[0]
		setmethod = attribute.setters[0]
		if len(setmethod.fpars) > 1:
		    if setmethod.fpars[1].default:
			setmethod.fpars = [setmethod.fpars[0]]
		elif not len(setmethod.fpars):
		    unhandled(2,"SETTER WITH NO PARS: "+interface.name+"::"+attribute.name+"("+setmethod.name+")")
		    setmethod = 0
		if len(getmethod.fpars):
		    unhandled(3,"GETTER WITH PARS: "+interface.name+"::"+attribute.name)
		    return
		if not setmethod:
		    if "," in getmethod.returntype:
			unhandled(4,"returntype with commas")
		        return
		    write_attr(interface,attribute,getmethod)
		elif len(setmethod.fpars)>1:
		    write_multiattr(interface,attribute,getmethod,setmethod)
		else:
		    write_attr(interface,attribute,getmethod,setmethod)
	# one getter, several setters
	elif len(attribute.getters) == 1 and len(attribute.setters):
		getmethod = attribute.getters[0]
                setmethod = attribute.setters[0]
		write_multiattr(interface,attribute,getmethod,setmethod)
		return
	# one getter, no setters
	elif len(attribute.getters) == 1:
		getmethod = attribute.getters[0]
		if len(getmethod.fpars):
		        unhandled(6,"GETMETHOD WITH INPUTS: "+interface.name+"::"+attribute.name+"\n")
			return
		else:
		    if "," in getmethod.returntype:
			unhandled(4,"returntype with commas")
		        return
		    write_attr(interface,attribute,getmethod)
	# one setter only
	elif len(attribute.setters) == 1 and not len(attribute.getters):
		# ... with only one input parameter
		setmethod = attribute.setters[0]
		if len(attribute.setters[0].fpars) == 1:
		        write_attr(interface,attribute,None,setmethod)
		# ... with many input parameters
		else:
		        write_multiattr(interface,attribute,None,setmethod)
	# more than one getter or more than one setter or both
	elif len(attribute.setters)>1 and len(attribute.getters) == 0:
		setmethod = attribute.setters[0]
		write_multiattr(interface,attribute,None,setmethod)
	else:
	    if PRINT_UNHANDLED:
                global unhandled_count
                unhandled_count+=1
		if len(attribute.setters)>1 and len(attribute.getters)>1:
	                print "/*TOO MANY GET AND SET METHODS: ",interface.name+"::"+attribute.name
			unhandleds[8]+=1
		elif len(attribute.getters)>1:
	                print "/*TOO MANY GETTER METHODS: ",interface.name+"::"+attribute.name
			unhandleds[10]+=1
		else:
			print "/*NO GETTER OR SETTER",interface.name+"::"+attribute.name
			unhandleds[11]+=1
		print "Getters:"
	        for a in attribute.getters:
	            print "",a.name,a.returntype
		print "Setters:"
                for a in attribute.setters:
                    print "",a.name,a.fpars
		print "*/"

#Output to the swig interface file the wrapped interfaces
def outputWrapped(interface):
    print '//-------------------------------------'
    print '%include', '"' + interface.header + '"'
    name = interface.name
    if name.startswith('iPc'):
        pyname = name[3:]
    elif name.startswith('i'):
        pyname = name[1:]
    else:
        pyname = name
    factname = pyname.lower()
    print 'CEL_PC(' + interface.name + ',', pyname + ',', factname + ')'

###################################
# Swig interface file parsing
###################################

def findFile(filename):
    scandirs = [scandict["scandir"]]
    if "cflags" in scandict:
        scandirs += map(lambda s: s.replace("-I",""),scandict["cflags"])
    for dir in scandirs:
        path = os.path.join(dir,filename)
        if os.path.exists(path):
            return path
    return None
       
# find OUTPUT parameter mappings in swig file
def getSwigOutputMappings(filename):
    directives = []
    file = open(filename, 'r')
    for line in file:
        line = line.strip()
        if line.startswith("%import"):
            importfile = findFile(line[line.find('"')+1:line.rfind('"')])
            if importfile:
                directives+=getSwigOutputMappings(importfile)
        if line.startswith("%apply") and "OUTPUT" in line:
            par = line[line.find("{")+1:line.find("}")].strip()
            parsignature = "".join(par.split(" "))
            if parsignature and not parsignature in directives:
                directives.append(parsignature)
    file.close()
    return directives

# find per interface directives from swig file
def getSwigInterfaceDirectives(filename, identifier):
    file = open(filename, 'r')
    directives = {}
    for line in file:
        line = line.strip()
        if line.startswith(identifier):
            applied = line[len(identifier) + 1:-1]
            splitapplied = applied.split("::")
            if len(splitapplied) < 2:
                continue
            ifacename = splitapplied[0].strip()
            funcname = splitapplied[1].split("(")[0].strip()
            if ifacename not in directives:
                directives[ifacename] = []
            directives[ifacename].append(funcname)
    file.close()
    return directives

# find directives from swig file
def getSwigGlobalDirectives(filename, identifier,maxcount=0,extfilter=""):
    file = open(filename, 'r')
    applieds = []
    for line in file:
        line = line.strip().replace('"',"")
        if line.startswith(identifier):
            applied = line.split()[-1:][0]
            if not extfilter or applied.endswith(extfilter):
                applieds.append(applied)
            if maxcount and maxcount >= len(applieds):
                file.close()
                return applieds
    file.close()
    return applieds

def getSwigInterfaceInfo(filename, mode):
    applied_includes = getSwigGlobalDirectives(filename, '%include',extfilter=".h")
    ignored_interfaces = getSwigInterfaceDirectives(filename, '%ignore')
    ignored_interfacesf = getSwigGlobalDirectives(filename, '%ignore')
    scandict["ignored_ifaces"] = ignored_interfacesf
    return applied_includes, ignored_interfaces

###################################
# Main entry
###################################

#Scan a folder and subfolders for header files, and parse each one
def scanFolder(mainfolder,folder,doincludes,doignores):
    root, folders, files = os.walk(folder).next()
    headerfiles = filter(lambda f: '.h' in f, files)
    thisinterfaces = []
    for headerfile in headerfiles:
	fullpath = os.path.join(folder,headerfile).replace(mainfolder+"/","")
	if fullpath in doincludes:
	        thisinterfaces += parseFile(os.path.join(folder,headerfile),doignores)
    for subfolder in folders:
	if subfolder != ".svn":
	    thisinterfaces += scanFolder(mainfolder,os.path.join(folder,subfolder),doincludes,doignores)
    return thisinterfaces

# parse command line arguments and fill some values in global scandict.
def parseCmdLine():
    #0 outputs a swig file with %includes and CEL_PC's for cel blcel.i
    #1 generates the attributes
    sysargv = list(sys.argv)
    if "-include" in sys.argv:
        scandict["mode"] = 0
        sysargv.pop(sysargv.index("-include"))
    elif "-pymod" in sys.argv:
        scandict["mode"] = 2
    else:
        scandict["mode"] = 1
    # now parse de arguments
    if len(sysargv) <= 2:
        print 'You need to specify a folder to scan, and an interface file'
        exit(1)

    # second argument is the interface file
    scandict["ifacefile"] = os.path.abspath(sysargv[2])
    
    # first argument is the dir to parse
    scandict["scandir"] = os.path.abspath(sysargv[1])

    # other arguments are cflags for swig
    if len(sysargv) > 3:
        scandict["cflags"] = sysargv[3:]

fix_args_text = """
def fix_args(funct):
    def _inner(self, args):
        if type(args) == tuple:
	    args = (self,) + args
	else:
	    args = (self, args)
        return funct(*args)
    return _inner
"""

def mainScan():
    filename = scandict["ifacefile"]
    mode = scandict["mode"]
    scandir = scandict["scandir"]

    # get some info from swig interface files
    scandict["prefix"] = getSwigGlobalDirectives(filename,"%module",1)[0]
    doincludes, doignores = getSwigInterfaceInfo(filename, mode)
    scandict["outpars"] = getSwigOutputMappings(filename)

    # scan for all interfaces
    interfaces = scanFolder(scandir,scandir,doincludes,doignores)

    # debug output
    printFullDebugInfo(interfaces)

    # now print the output we want
    if mode is 2:
	print "#postprocessing of "+scandict["prefix"]+" module to add python properties"
        print "import "+scandict["prefix"]
        print "import _"+scandict["prefix"]
	print fix_args_text
    for interface in interfaces:
        if interface.name+";" in scandict["ignored_ifaces"] :
	    continue
        if mode is 0:
            outputWrapped(interface)
        elif mode is 1:
            if len(interface.attributes):
                print "\n/* "+interface.name+" ("+interface.header+") */"
            if interface.name.startswith("cs") or interface.name.startswith("i") or interface.name.startswith("cel"):
                for attribute in interface.attributes:
                    outputAttribute(interface,attribute)
        elif mode is 2:
            if len(interface.attributes):
                print "\n# "+interface.name+" ("+interface.header+")"
            if interface.name.startswith("cs") or interface.name.startswith("i") or interface.name.startswith("cel"):
                for attribute in interface.attributes:
                    outputAttribute(interface,attribute)


parseCmdLine()

mainScan()

printStats()
printExtra()

