import { useMemo } from "react"
import ReactFlow, {
  Background,
  Controls,
  MarkerType,
  type Node,
  type Edge,
} from "reactflow"
import "reactflow/dist/style.css"
import dagre from "dagre"

interface GraphEdgeData {
  source: string
  relation: string
  target: string
}

interface Props {
  edges: GraphEdgeData[]
}

const NODE_WIDTH = 180
const NODE_HEIGHT = 50

function layoutGraph(rawEdges: GraphEdgeData[]): { nodes: Node[]; edges: Edge[] } {
  const dagreGraph = new dagre.graphlib.Graph()
  dagreGraph.setDefaultEdgeLabel(() => ({}))
  dagreGraph.setGraph({ rankdir: "LR", nodesep: 40, ranksep: 90 })

  const nodeNames = new Set<string>()
  rawEdges.forEach((e) => {
    nodeNames.add(e.source)
    nodeNames.add(e.target)
  })

  nodeNames.forEach((name) => {
    dagreGraph.setNode(name, { width: NODE_WIDTH, height: NODE_HEIGHT })
  })
  rawEdges.forEach((e) => {
    dagreGraph.setEdge(e.source, e.target)
  })

  dagre.layout(dagreGraph)

  const nodes: Node[] = Array.from(nodeNames).map((name) => {
    const pos = dagreGraph.node(name)
    return {
      id: name,
      data: { label: name },
      position: { x: pos.x - NODE_WIDTH / 2, y: pos.y - NODE_HEIGHT / 2 },
      style: {
        background: "#1e293b",
        color: "#e2e8f0",
        border: "1px solid #475569",
        borderRadius: 8,
        fontSize: 12,
        fontWeight: 500,
        padding: 10,
        width: NODE_WIDTH,
        textAlign: "center" as const,
      },
    }
  })

  const edges: Edge[] = rawEdges.map((e, i) => ({
    id: `edge-${i}`,
    source: e.source,
    target: e.target,
    label: e.relation,
    labelStyle: { fill: "#94a3b8", fontSize: 10 },
    labelBgStyle: { fill: "#0f172a", fillOpacity: 0.9 },
    style: { stroke: "#475569" },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#475569" },
    animated: false,
  }))

  return { nodes, edges }
}

export default function KnowledgeGraphView({ edges: rawEdges }: Props) {
  const { nodes, edges } = useMemo(() => layoutGraph(rawEdges), [rawEdges])

  if (rawEdges.length === 0) {
    return (
      <p className="text-sm text-slate-500">No graph data available for this report.</p>
    )
  }

  return (
    <div style={{ height: 500 }} className="border border-slate-800 rounded-lg bg-slate-950">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#1e293b" gap={20} />
        <Controls />
      </ReactFlow>
    </div>
  )
}