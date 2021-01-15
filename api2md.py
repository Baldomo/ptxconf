#!/usr/bin/python
import pdoc
import sys
import os

modpath = os.path.dirname(os.path.abspath(sys.argv[1]))
modname = os.path.basename(sys.argv[1]).split(".py")[0]

context = pdoc.Context()
modules = [pdoc.Module(mod, context=context) for mod in sys.argv[1:]]
pdoc.link_inheritance(context)

def recursive_html(mod: pdoc.Module):
    yield mod.name, mod.html()
    for submod in mod.submodules():
        yield from recursive_html(submod)

for mod in modules:
    for modname, modhtml in recursive_html(mod):
        print(modhtml)

# for line in pdoc.text(modname).split("\n"):
#     md.append(line)
# md.append("")

# for i, line in enumerate(md):
#     if i > len(md) - 2:
#         break
#     # first level headings
#     if "----" == md[i + 1][0:4]:
#         print("# " + line)

#     # first level definitions class names / functions
#     elif (
#         line != ""
#         and "    " != line[0:4]
#         and "----" != line[0:4]
#         and "----" != md[i + 1][0:4]
#     ):
#         print("## " + line)

#     elif "    " == line[0:4] and "----" in md[i + 1][4:8]:
#         print("### " + line[4:])
#     # methods
#     elif "(self" in line:
#         print("#### " + line[4:])
#     # plain text/members
#     elif line != "" and "    " == line[0:4] and "----" not in line:
#         print(line[4:].strip())
