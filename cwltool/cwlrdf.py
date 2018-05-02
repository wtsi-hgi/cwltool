from __future__ import absolute_import
from typing import IO, Any, Dict, Text

from rdflib import Graph

from schema_salad.jsonld_context import makerdf
from schema_salad.ref_resolver import ContextType
from six.moves import urllib

from cwltool.workflow import Workflow
from cwltool.command_line_tool import CommandLineTool, ExpressionTool

from .process import Process

import sys
import textwrap


def gather(tool, ctx):  # type: (Process, ContextType) -> Graph
    g = Graph()

    def visitor(t):
        makerdf(t["id"], t, ctx, graph=g)

    tool.visit(visitor)
    return g


def printrdf(wf, ctx, sr):
    # type: (Process, ContextType, Text) -> Text
    return gather(wf, ctx).serialize(format=sr).decode('utf-8')


def lastpart(uri):  # type: (Any) -> Text
    uri = Text(uri)
    if "/" in uri:
        return uri[uri.rindex("/") + 1:]
    else:
        return uri


def dot_with_parameters(g, stdout):  # type: (Graph, IO[Any]) -> None
    qres = g.query(
        """SELECT ?step ?run ?runtype
           WHERE {
              ?step cwl:run ?run .
              ?run rdf:type ?runtype .
           }""")

    for step, run, runtype in qres:
        stdout.write(u'"%s" [label="%s"]\n' % (lastpart(step), "%s (%s)" % (lastpart(step), lastpart(run))))

    qres = g.query(
        """SELECT ?step ?inp ?source
           WHERE {
              ?wf Workflow:steps ?step .
              ?step cwl:in ?inp .
              ?inp cwl:source ?source .
           }""")

    for step, inp, source in qres:
        stdout.write(u'"%s" [shape=box]\n' % (lastpart(inp)))
        stdout.write(u'"%s" -> "%s" [label="%s"]\n' % (lastpart(source), lastpart(inp), ""))
        stdout.write(u'"%s" -> "%s" [label="%s"]\n' % (lastpart(inp), lastpart(step), ""))

    qres = g.query(
        """SELECT ?step ?out
           WHERE {
              ?wf Workflow:steps ?step .
              ?step cwl:out ?out .
           }""")

    for step, out in qres:
        stdout.write(u'"%s" [shape=box]\n' % (lastpart(out)))
        stdout.write(u'"%s" -> "%s" [label="%s"]\n' % (lastpart(step), lastpart(out), ""))

    qres = g.query(
        """SELECT ?out ?source
           WHERE {
              ?wf cwl:out ?out .
              ?out cwl:source ?source .
           }""")

    for out, source in qres:
        stdout.write(u'"%s" [shape=octagon]\n' % (lastpart(out)))
        stdout.write(u'"%s" -> "%s" [label="%s"]\n' % (lastpart(source), lastpart(out), ""))

    qres = g.query(
        """SELECT ?inp
           WHERE {
              ?wf rdf:type cwl:Workflow .
              ?wf cwl:inputs ?inp .
           }""")

    for (inp,) in qres:
        stdout.write(u'"%s" [shape=octagon]\n' % (lastpart(inp)))

def get_end_url(url):
    return str(url).split("/")[-1]

def get_url_hash(url):
    return str(url).split("#")[-1]

def get_end_name(name):
    hash_regions = str(name).split("#")
    if len(hash_regions) == 2:
        return hash_regions[1]
    else:
        return str(name).split("/")[-1]

def get_out_name(url):
    last_hash = url.rfind("#")
    last_slash = url.rfind("/")
    if last_hash == -1 and last_slash == -1:
        return url

    return url[(last_hash if last_hash > last_slash else last_slash) + 1:]

def print_indent(string):
    print(" " * indent_level + string)

def get_tool_name(url):
    return "/".join(url.split("/")[:-1])

tool_names = set()

"""
"SELECT DISTINCT ?from ?to
WHERE {
    ?wf Workflow:steps ?step.
    ?step cwl:in ?in.
    ?in cwl:source ?source.
    ?step cwl:run ?to_tool.
    OPTIONAL{
        ?source_step cwl:out ?source.
        ?source_step cwl:run ?from_tool.
    }
    OPTIONAL{

    }
}"
"""

from pprint import pprint
import json

drawn_workflows = set()
default_num = 0

def get_udefault():
    global default_num
    default_num += 1
    return f"default{default_num}"

def esc(string):
    if isinstance(string, bool):
        return "true" if string else "false"
    elif isinstance(string, str) \
            and len(string) >= 3 \
            and (string[:2], string[-1]) in (("${", "}"), ("$(", ")")):
        string = string[2:-1]
    else:
        string = repr(string)

    return string \
        .replace("\"", "\\\"") \
        .replace("{", "\\{") \
        .replace("}", "\\}")

def get_workflow_dot(tool):
    global drawn_workflows
    global tool_names
    global indent_level
    print_indent(f"""subgraph "cluster_{get_end_name(tool.tool["id"])}" {{""")
    indent_level += 2
    print_indent(f"""label="{get_end_name(tool.tool["id"])}\";""")

    print_indent("subgraph cluster_inputs {")
    indent_level += 2
    print_indent("rank = \"same\";")
    print_indent("style = \"dashed\";")
    print_indent("label = \"Workflow Inputs\";")
    for cwl_input in tool.tool["inputs"]:
        print_indent(f""""{cwl_input["id"]}" [label="{get_end_name(cwl_input["id"])}", fillcolor="#94DDF4"];""")
        # TODO add a label
    indent_level -= 2
    print_indent("}")

    arrows = []
    inputs_id_to_end_id = dict()
    outputs_id_to_end_id = dict()
    workflows_to_draw = []
    for cwl_step in tool.steps:
        if not isinstance(cwl_step.embedded_tool, Workflow):
            tool_names.add(cwl_step.id)

        for y in cwl_step.tool["inputs"]:
            inputs_id_to_end_id[y["id"]] = y["endId"]

        for y in cwl_step.tool["outputs"]:
            outputs_id_to_end_id[y["id"]] = y["endId"]

    for cwl_step in tool.steps:
        if cwl_step.embedded_tool.tool["id"] in drawn_workflows:
            pass
        if isinstance(cwl_step.embedded_tool, Workflow):
            drawn_workflows.add(cwl_step.embedded_tool.tool["id"])
            workflows_to_draw.append(cwl_step.embedded_tool)
            # get_workflow_dot(cwl_step.embedded_tool)
        else:
            props = []
            props.append(f"""label="{get_end_name(cwl_step.id)}\"""")

            if isinstance(cwl_step.embedded_tool, ExpressionTool):
                props.append(f"""fillcolor="#d3d3d3\"""")
            else:
                assert isinstance(cwl_step.embedded_tool, CommandLineTool)

            if cwl_step.tool.get("scatter") is not None:
                props.append(f"""peripheries=2""")

            print_indent(f""""{cwl_step.id}" [{", ".join(props)}];""")

        for cwl_step_input in cwl_step.tool["inputs"]:
            arrow_target = cwl_step_input["endId"]
            if get_tool_name(cwl_step_input["id"]) in tool_names:
                arrow_target = cwl_step.id
            else:
                pass

            if cwl_step_input.get("default") is not None \
                    or (cwl_step_input.get("valueFrom") is not None \
                    and cwl_step_input.get("source") is None):
                value = cwl_step_input.get("default", cwl_step_input.get("valueFrom"))
                default_node_name = get_udefault()
                print_indent(f""""{default_node_name}" [label="{esc(value)}", fillcolor="#d5aefc"]""")

                arrows.append(f""""{default_node_name}" -> "{arrow_target}" [label="  {get_out_name(cwl_step_input["id"])}  "];""")
            else:
                assert cwl_step_input.get("source") is not None
                if isinstance(cwl_step_input["source"], str):
                    source_list = [cwl_step_input["source"]]
                else:
                    source_list = cwl_step_input["source"]

                if cwl_step_input.get("valueFrom") is not None:
                    value_from_node_name = get_udefault()
                    print_indent(f""""{value_from_node_name}" [label="{esc(cwl_step_input["valueFrom"])}", fillcolor="#d5aefc"]""")

                for source_item in source_list:
                    assert isinstance(source_item, str)

                    if get_tool_name(source_item) in tool_names:
                        arrow_source = get_tool_name(source_item)
                    else:
                        arrow_source = outputs_id_to_end_id.get(source_item, source_item)

                    if cwl_step_input.get("valueFrom") is None:
                        arrows.append(f""""{arrow_source}" -> "{arrow_target}" [label="  {get_out_name(source_item)}  "];""")
                    else:
                        arrows.append(f""""{arrow_source}" -> "{value_from_node_name}\"""")
                        arrows.append(f""""{value_from_node_name}" -> "{arrow_target}" [label="  {get_out_name(source_item)}  "];""")

    print_indent("subgraph cluster_outputs {")
    indent_level += 2
    print_indent("rank = \"same\";")
    print_indent("style = \"dashed\";")
    print_indent("labelloc = \"b\";")
    print_indent("label = \"Workflow Outputs\";")
    for cwl_output in tool.tool["outputs"]:
        print_indent(f""""{cwl_output["id"]}" [label="{get_end_name(cwl_output["id"])}", fillcolor="#94DDF4"];""")

        if isinstance(cwl_output["outputSource"], str):
            cwl_output_source_list = [cwl_output["outputSource"]]
        else:
            cwl_output_source_list = cwl_output["outputSource"]

        for cwl_output_source in cwl_output_source_list:
            assert isinstance(cwl_output_source, str)

            if get_tool_name(cwl_output_source) in tool_names:
                arrow_source = get_tool_name(cwl_output_source)
            else:
                arrow_source = outputs_id_to_end_id[cwl_output_source]

            arrows.append(f""""{arrow_source}" -> "{cwl_output["id"]}" [label="  {get_out_name(cwl_output_source)}  ", fillcolor="#94DDF4"];""")
    indent_level -= 2
    print_indent("}")

    for arrow in arrows:
        print_indent(arrow)

    indent_level -= 2
    print_indent("}")

    for workflow in workflows_to_draw:
        get_workflow_dot(workflow)

start = """
    digraph workflow {
      graph [
        bgcolor = "#eeeeee"
        color = "black"
        fontsize = "10"
        clusterrank = "local"
        # labeljust = "left"
        # ranksep = "0.22"
        # nodesep = "0.05"
      ]

      node [
        fontname = "Helvetica"
        fontsize = "10"
        fontcolor = "black"
        shape = "rect"
        height = "0"
        width = "0"
        color = "black"
        fillcolor = "lightgoldenrodyellow"
        style = "filled"
      ];

      edge [
        fontname="Helvetica"
        fontsize="8"
        fontcolor="black"
        color="black"
        # arrowsize="0.7"
      ];"""

def cwl_viewer_dot(tool_json):
    global indent_level
    print(textwrap.dedent(start))
    indent_level = 2
    get_workflow_dot(tool_json)
    print("}")


def dot_without_parameters(g, stdout):  # type: (Graph, IO[Any]) -> None
    dotname = {}  # type: Dict[Text,Text]
    clusternode = {}

    stdout.write("compound=true\n")
    subworkflows = set()
    qres = g.query(
        """SELECT ?run
           WHERE {
              ?wf rdf:type cwl:Workflow .
              ?wf Workflow:steps ?step .
              ?step cwl:run ?run .
              ?run rdf:type cwl:Workflow .
           } ORDER BY ?wf""")
    for (run,) in qres:
        subworkflows.add(run)

    qres = g.query(
        """SELECT ?wf ?step ?run ?runtype
           WHERE {
              ?wf rdf:type cwl:Workflow .
              ?wf Workflow:steps ?step .
              ?step cwl:run ?run .
              ?run rdf:type ?runtype .
           } ORDER BY ?wf""")

    currentwf = None
    for wf, step, _, runtype in qres:
        if step not in dotname:
            dotname[step] = lastpart(step)

        if wf != currentwf:
            if currentwf is not None:
                stdout.write("}\n")
            if wf in subworkflows:
                if wf not in dotname:
                    dotname[wf] = "cluster_" + lastpart(wf)
                stdout.write(u'subgraph "%s" { label="%s"\n' % (dotname[wf], lastpart(wf)))
                currentwf = wf
                clusternode[wf] = step
            else:
                currentwf = None

        if Text(runtype) != "https://w3id.org/cwl/cwl#Workflow":
            stdout.write(u'"%s" [label="%s"]\n' % (dotname[step], urllib.parse.urldefrag(Text(step))[1]))

    if currentwf is not None:
        stdout.write("}\n")

    qres = g.query(
        """SELECT DISTINCT ?src ?sink ?srcrun ?sinkrun
           WHERE {
              ?wf1 Workflow:steps ?src .
              ?wf2 Workflow:steps ?sink .
              ?src cwl:out ?out .
              ?inp cwl:source ?out .
              ?sink cwl:in ?inp .
              ?src cwl:run ?srcrun .
              ?sink cwl:run ?sinkrun .
           }""")

    for src, sink, srcrun, sinkrun in qres:
        attr = u""
        if srcrun in clusternode:
            attr += u'ltail="%s"' % dotname[srcrun]
            src = clusternode[srcrun]
        if sinkrun in clusternode:
            attr += u' lhead="%s"' % dotname[sinkrun]
            sink = clusternode[sinkrun]
        stdout.write(u'"%s" -> "%s" [%s]\n' % (dotname[src], dotname[sink], attr))


def printdot(wf, ctx, stdout, include_parameters=False):
    # type: (Process, ContextType, Any, bool) -> None
    g = gather(wf, ctx)

    cwl_viewer_dot(wf)
    # stdout.write("digraph {")

    # # g.namespace_manager.qname(predicate)

    # if include_parameters:
    #     dot_with_parameters(g, stdout)
    # else:
    #     dot_without_parameters(g, stdout)

    # stdout.write("}")
