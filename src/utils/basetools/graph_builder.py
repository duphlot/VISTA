import json
import math
from typing import Dict, List, Optional
import networkx as nx


# Frame selection configurations
KEEP_FRAMES = {0, 15, 20, 25, 40, 45, 75, 80}


class CLEVRERGraphBuilder:
    """Build spatio-temporal graphs from CLEVRER annotation data"""
    
    def __init__(self, annotation_file: str):
        """
        Initialize graph builder with annotation file
        
        Args:
            annotation_file: Path to the JSON annotation file
        """
        with open(annotation_file, "r") as f:
            self.data = json.load(f)
        self.objects = self.data["object_property"]
        self.trajectories = {t["frame_id"]: t for t in self.data["motion_trajectory"]}

    def get_obj_prop(self, oid: int) -> Dict:
        """Get object properties by ID"""
        return next((o for o in self.objects if o["object_id"] == oid), {})

    def distance(self, a: List[float], b: List[float]) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))

    def approx_radius(self, obj_prop: Dict) -> float:
        """
        Approximate object radius based on properties
        
        Args:
            obj_prop: Object property dictionary
            
        Returns:
            Estimated radius for collision detection
        """
        # Use size or scale if available
        if "size" in obj_prop:
            return obj_prop["size"] / 2.0
        if "scale" in obj_prop:
            return obj_prop["scale"] / 2.0
        
        # Heuristic based on shape
        shape = obj_prop.get("shape", "").lower()
        if shape == "sphere": 
            return 0.22
        if shape == "cube": 
            return 0.25
        if shape == "cylinder": 
            return 0.22
        return 0.25  # default fallback

    def build_graph(self, collision_scale: float = 1.0, base_threshold: Optional[float] = None, 
                   interp_steps: int = 5, eps: float = 1e-4) -> nx.DiGraph:
        """
        Build spatio-temporal graph with collision detection
        
        Args:
            collision_scale: Scale factor for collision threshold
            base_threshold: Fixed collision threshold (overrides radius-based)
            interp_steps: Number of interpolation steps for collision detection
            eps: Minimum distance threshold for position changes
            
        Returns:
            NetworkX directed graph representing spatio-temporal relationships
        """
        G = nx.DiGraph()
        last_node = {}
        active_collisions = set()  # track ongoing collisions

        kept = sorted([f for f in KEEP_FRAMES if f in self.trajectories])
        if not kept:
            raise RuntimeError("No kept frames found in trajectories.")

        # Initialize nodes at first frame
        start_f = kept[0]
        start_objs = self.trajectories[start_f]["objects"]
        for obj in start_objs:
            prop = self.get_obj_prop(obj["object_id"])
            nid = f"obj{obj['object_id']}_f{start_f}"
            node_info = {**prop, **obj, "frame": start_f}
            G.add_node(nid, **node_info, type="object")
            last_node[obj["object_id"]] = nid

        radii = {o["object_id"]: self.approx_radius(o) for o in self.objects}

        # Process consecutive frame pairs
        for idx in range(1, len(kept)):
            fprev = kept[idx-1]
            fcur = kept[idx]
            prev_objs = {o["object_id"]: o for o in self.trajectories[fprev]["objects"]}
            cur_objs  = {o["object_id"]: o for o in self.trajectories[fcur]["objects"]}

            # Check collisions using interpolation
            new_collisions = set()
            for s in range(1, interp_steps+1):
                t = s / float(interp_steps)
                interp_pos = {}
                for oid, cur in cur_objs.items():
                    if oid in prev_objs:
                        p0 = prev_objs[oid]["location"]
                        p1 = cur["location"]
                        pos = [p0[i]*(1-t) + p1[i]*t for i in range(len(p0))]
                    else:
                        pos = cur["location"]
                    interp_pos[oid] = pos

                oids = list(interp_pos.keys())
                for i in range(len(oids)):
                    for j in range(i+1, len(oids)):
                        oi, oj = oids[i], oids[j]
                        d = self.distance(interp_pos[oi], interp_pos[oj])
                        if base_threshold is not None:
                            thresh = base_threshold
                        else:
                            thresh = (radii.get(oi,0.25) + radii.get(oj,0.25)) * collision_scale
                        if d <= thresh:
                            a, b = (oi, oj) if oi < oj else (oj, oi)
                            new_collisions.add((a, b))

            # Handle collision changes
            # Remove ended collisions
            to_remove = [pair for pair in active_collisions if pair not in new_collisions]
            for pair in to_remove:
                active_collisions.remove(pair)

            # Add new collisions
            for (a, b) in new_collisions:
                if (a, b) not in active_collisions:
                    coll_id = f"collision_{a}_{b}_f{fcur}"
                    G.add_node(
                        coll_id,
                        color=(self.get_obj_prop(a).get("color"), self.get_obj_prop(b).get("color")),
                        shape=(self.get_obj_prop(a).get("shape"), self.get_obj_prop(b).get("shape")),
                        frame=fcur,
                        objects=(a, b),
                        type="collision"
                    )
                    for oid in (a, b):
                        prev_node = last_node.get(oid)
                        if prev_node:
                            G.add_edge(prev_node, coll_id, frame=fcur)
                        last_node[oid] = coll_id

                    active_collisions.add((a, b))

            # Create object nodes at current frame
            for oid, cur in cur_objs.items():
                prev_node = last_node.get(oid)
                cur_loc = cur["location"]

                # Skip if location unchanged
                skip_new_node = False
                if prev_node:
                    prev_loc = G.nodes[prev_node].get("location")
                    if prev_loc is not None:
                        dist = self.distance(prev_loc, cur_loc)
                        if dist < eps:
                            skip_new_node = True

                if skip_new_node:
                    last_node[oid] = prev_node
                    continue

                node_id = f"obj{oid}_f{fcur}"
                base = self.get_obj_prop(oid)
                node_info = {**base, **cur, "frame": fcur}
                G.add_node(node_id, **node_info, type="object")

                if prev_node:
                    G.add_edge(prev_node, node_id, frame=fcur)

                last_node[oid] = node_id

        return G
