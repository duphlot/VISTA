import json
import networkx as nx
from typing import Dict, List, Any, Optional
from .graph_builder import CLEVRERGraphBuilder


class GraphSearcher:
    """Search for object trajectories and collision paths in spatio-temporal graph"""
    
    def __init__(self, graph: nx.DiGraph):
        """
        Initialize with a built graph
        
        Args:
            graph: NetworkX directed graph from CLEVRERGraphBuilder
        """
        self.graph = graph
    
    def search_object_trajectory(self, object_id: int) -> Dict[str, Any]:
        """
        Search for complete trajectory of an object including all collisions
        
        Args:
            object_id: ID of the object to track
            
        Returns:
            Dictionary containing complete trajectory information in JSON format
        """
        trajectory = {
            "object_id": object_id,
            "path": [],
            "collisions": [],
            "summary": {
                "total_frames": 0,
                "collision_count": 0,
                "collision_partners": []
            }
        }
        
        # Find all nodes related to this object
        object_nodes = []
        collision_nodes = []
        
        for node_id, data in self.graph.nodes(data=True):
            if data.get("type") == "object" and data.get("object_id") == object_id:
                object_nodes.append((node_id, data))
            elif data.get("type") == "collision" and object_id in data.get("objects", []):
                collision_nodes.append((node_id, data))
        
        # Sort by frame for chronological order
        object_nodes.sort(key=lambda x: x[1].get("frame", 0))
        collision_nodes.sort(key=lambda x: x[1].get("frame", 0))
        
        # Build trajectory path
        for node_id, data in object_nodes:
            path_entry = {
                "frame": data.get("frame"),
                "node_id": node_id,
                "location": data.get("location"),
                "velocity": data.get("velocity"),
                "type": "object_position"
            }
            trajectory["path"].append(path_entry)
        
        # Add collision information
        for node_id, data in collision_nodes:
            collision_partners = data.get("objects", [])
            partner_id = next((oid for oid in collision_partners if oid != object_id), None)
            
            if partner_id is not None:
                # Get partner object properties
                partner_colors = data.get("color", (None, None))
                partner_shapes = data.get("shape", (None, None))
                
                # Determine which color/shape belongs to which object
                partner_color = partner_colors[1] if collision_partners[0] == object_id else partner_colors[0]
                partner_shape = partner_shapes[1] if collision_partners[0] == object_id else partner_shapes[0]
                
                collision_entry = {
                    "frame": data.get("frame"),
                    "node_id": node_id,
                    "collision_with": {
                        "object_id": partner_id,
                        "color": partner_color,
                        "shape": partner_shape
                    },
                    "type": "collision"
                }
                trajectory["collisions"].append(collision_entry)
                
                # Add to collision partners if not already present
                if partner_id not in trajectory["summary"]["collision_partners"]:
                    trajectory["summary"]["collision_partners"].append(partner_id)
        
        # Update summary
        trajectory["summary"]["total_frames"] = len(object_nodes)
        trajectory["summary"]["collision_count"] = len(collision_nodes)
        
        # Merge path and collisions chronologically
        all_events = trajectory["path"] + trajectory["collisions"]
        all_events.sort(key=lambda x: x.get("frame", 0))
        trajectory["complete_timeline"] = all_events
        
        print(trajectory)
        
        return trajectory
    
    def search_collision_between_objects(self, object_id1: int, object_id2: int) -> Dict[str, Any]:
        """
        Search for collisions between two specific objects
        
        Args:
            object_id1: First object ID
            object_id2: Second object ID
            
        Returns:
            Dictionary containing collision information
        """
        collision_info = {
            "object_pair": [object_id1, object_id2],
            "collisions": [],
            "collision_count": 0
        }
        
        for node_id, data in self.graph.nodes(data=True):
            if (data.get("type") == "collision" and 
                set(data.get("objects", [])) == {object_id1, object_id2}):
                
                collision_entry = {
                    "frame": data.get("frame"),
                    "node_id": node_id,
                    "colors": data.get("color"),
                    "shapes": data.get("shape")
                }
                collision_info["collisions"].append(collision_entry)
        
        collision_info["collision_count"] = len(collision_info["collisions"])
        collision_info["collisions"].sort(key=lambda x: x.get("frame", 0))
        
        print(collision_info)
        
        return collision_info


class CLEVRERSearchTool:
    """Main search tool that combines graph building and searching"""
    
    def __init__(self, annotation_file: str):
        """
        Initialize with annotation file
        
        Args:
            annotation_file: Path to annotation JSON file
        """
        self.annotation_file = annotation_file
        self.graph_builder = CLEVRERGraphBuilder(annotation_file)
        self.graph = None
        self.searcher = None
        self._build_graph()
    
    def _build_graph(self):
        """Build the spatio-temporal graph"""
        self.graph = self.graph_builder.build_graph(
            collision_scale=1.1, 
            interp_steps=8
        )
        self.searcher = GraphSearcher(self.graph)
    
    def search_object_trajectory(self, object_id: int) -> str:
        """
        Search for object trajectory and return complete path information as JSON string
        
        Args:
            object_id: ID of object to search
            
        Returns:
            JSON string containing complete trajectory with all collision details
        """
        if self.searcher is None:
            return json.dumps({"error": "Graph not initialized"})
        
        try:
            trajectory = self.searcher.search_object_trajectory(object_id)
            return json.dumps(trajectory, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Search failed: {str(e)}"})